"""Substitution projection — explicit formulas from product spec."""

from __future__ import annotations

from backend.app.schemas import PlayerOut, SimulateSubstitutionOut
from data_pipeline.config import (
    SIM_DEF_BLK_PCT,
    SIM_DEF_DBPM,
    SIM_DEF_STL_PCT,
    SIM_OFF_AST_PCT,
    SIM_OFF_OBPM,
    SIM_OFF_TOV_PCT,
    SIM_OFF_TS,
)


def _f(x: float | None, default: float) -> float:
    if x is None:
        return default
    return float(x)


def simulate_substitution(
    *,
    team_abbr: str,
    lineup_id: str,
    cur_off: float,
    cur_def: float,
    removed: dict,
    incoming: dict,
) -> SimulateSubstitutionOut:
    # TS% (True Shooting Percentage), AST% (Assist Percentage), TOV% (Turnover Percentage),
    # STL% (Steal Percentage), BLK% (Block Percentage) are decimals (e.g. 0.58).
    # OBPM (Offensive Box Plus/Minus) and DBPM (Defensive Box Plus/Minus) are BPM-scale.
    rem_obpm = _f(removed.get("obpm"), 0.0)
    inc_obpm = _f(incoming.get("obpm"), 0.0)
    rem_ts = _f(removed.get("ts_pct"), 0.55)
    inc_ts = _f(incoming.get("ts_pct"), 0.55)
    rem_ast = _f(removed.get("ast_pct"), 0.15)
    inc_ast = _f(incoming.get("ast_pct"), 0.15)
    rem_tov = _f(removed.get("tov_pct"), 0.12)
    inc_tov = _f(incoming.get("tov_pct"), 0.12)
    rem_dbpm = _f(removed.get("dbpm"), 0.0)
    inc_dbpm = _f(incoming.get("dbpm"), 0.0)
    rem_stl = _f(removed.get("stl_pct"), 0.02)
    inc_stl = _f(incoming.get("stl_pct"), 0.02)
    rem_blk = _f(removed.get("blk_pct"), 0.04)
    inc_blk = _f(incoming.get("blk_pct"), 0.04)

    d_obpm = inc_obpm - rem_obpm
    d_ts = inc_ts - rem_ts
    d_ast = inc_ast - rem_ast
    d_tov = inc_tov - rem_tov
    d_dbpm = inc_dbpm - rem_dbpm
    d_stl = inc_stl - rem_stl
    d_blk = inc_blk - rem_blk

    proj_off = (
        cur_off
        + SIM_OFF_OBPM * d_obpm
        + SIM_OFF_TS * d_ts
        + SIM_OFF_AST_PCT * d_ast
        - SIM_OFF_TOV_PCT * d_tov
    )
    proj_def = (
        cur_def
        - SIM_DEF_DBPM * d_dbpm
        - SIM_DEF_STL_PCT * d_stl
        - SIM_DEF_BLK_PCT * d_blk
    )
    base_net = cur_off - cur_def
    proj_net = proj_off - proj_def

    summary = _build_summary(
        removed_name=str(removed.get("player_name")),
        incoming_name=str(incoming.get("player_name")),
        d_obpm=d_obpm,
        d_ts=d_ts,
        d_ast=d_ast,
        d_tov=d_tov,
        d_dbpm=d_dbpm,
        d_stl=d_stl,
        d_blk=d_blk,
        d_net=proj_net - base_net,
    )

    return SimulateSubstitutionOut(
        team_abbr=team_abbr,
        lineup_id=lineup_id,
        baseline_offensive_rating=cur_off,
        baseline_defensive_rating=cur_def,
        baseline_net_rating=base_net,
        projected_offensive_rating=proj_off,
        projected_defensive_rating=proj_def,
        projected_net_rating=proj_net,
        delta_offensive_rating=proj_off - cur_off,
        delta_defensive_rating=proj_def - cur_def,
        delta_net_rating=proj_net - base_net,
        summary=summary,
        removed_player=PlayerOut.model_validate(removed),
        incoming_player=PlayerOut.model_validate(incoming),
    )


def _build_summary(
    *,
    removed_name: str,
    incoming_name: str,
    d_obpm: float,
    d_ts: float,
    d_ast: float,
    d_tov: float,
    d_dbpm: float,
    d_stl: float,
    d_blk: float,
    d_net: float,
) -> str:
    """
    Name drivers by approximate rating-point leverage (|coefficient × delta|), not coarse buckets,
    so similar swaps are not always tagged with the same two generic phrases.
    """
    thresh = 0.05  # ~0.05 pts per 100 from one model term
    scored: list[tuple[float, str]] = [
        (abs(SIM_OFF_OBPM * d_obpm), "OBPM"),
        (abs(SIM_OFF_TS * d_ts), "true shooting"),
        (abs(SIM_OFF_AST_PCT * d_ast), "assist rate"),
        (abs(SIM_OFF_TOV_PCT * d_tov), "turnover rate"),
        (abs(SIM_DEF_DBPM * d_dbpm), "DBPM"),
        (abs(SIM_DEF_STL_PCT * d_stl), "steal rate"),
        (abs(SIM_DEF_BLK_PCT * d_blk), "block rate"),
    ]
    scored = [(m, lab) for m, lab in scored if m >= thresh]
    scored.sort(key=lambda x: -x[0])
    top = [lab for _, lab in scored[:4]]
    if top:
        driver_phrase = "Strongest model pulls (by rating-point leverage): " + ", ".join(top) + "."
    else:
        driver_phrase = (
            "No single proxy moved enough to dominate—the shift is the sum of small OBPM/TS%/AST%/TOV% and "
            "DBPM/STL%/BLK% differences."
        )

    direction = "improves" if d_net > 0.15 else "hurts" if d_net < -0.15 else "slightly adjusts"
    return (
        f"Replacing {removed_name} with {incoming_name} {direction} the projected lineup "
        f"(Δ net ≈ {d_net:+.2f} per 100). {driver_phrase} "
        "Heuristic projection—not a calibrated forecast."
    )
