"""Substitution simulator — numeric checks against spec formulas."""

from backend.app.services.simulation import simulate_substitution
from data_pipeline.config import (
    SIM_DEF_BLK_PCT,
    SIM_DEF_DBPM,
    SIM_DEF_STL_PCT,
    SIM_OFF_AST_PCT,
    SIM_OFF_OBPM,
    SIM_OFF_TOV_PCT,
    SIM_OFF_TS,
)


def _player(**kwargs):
    base = {
        "player_id": 1,
        "player_name": "A",
        "team_abbr": "TST",
        "obpm": 0.0,
        "dbpm": 0.0,
        "ts_pct": 0.55,
        "ast_pct": 0.15,
        "tov_pct": 0.12,
        "stl_pct": 0.02,
        "blk_pct": 0.04,
    }
    base.update(kwargs)
    return base


def test_substitution_formula_matches_spec():
    removed = _player(player_id=1, player_name="Out")
    incoming = _player(
        player_id=2,
        player_name="In",
        obpm=1.0,
        dbpm=0.5,
        ts_pct=0.56,
        ast_pct=0.20,
        tov_pct=0.13,
        stl_pct=0.025,
        blk_pct=0.05,
    )
    cur_off, cur_def = 110.0, 108.0
    out = simulate_substitution(
        team_abbr="TST",
        lineup_id="x",
        cur_off=cur_off,
        cur_def=cur_def,
        removed=removed,
        incoming=incoming,
    )
    d_obpm, d_ts = 1.0, 0.01
    d_ast, d_tov = 0.05, 0.01
    d_dbpm = 0.5
    d_stl, d_blk = 0.005, 0.01

    exp_off = (
        cur_off
        + SIM_OFF_OBPM * d_obpm
        + SIM_OFF_TS * d_ts
        + SIM_OFF_AST_PCT * d_ast
        - SIM_OFF_TOV_PCT * d_tov
    )
    exp_def = cur_def - SIM_DEF_DBPM * d_dbpm - SIM_DEF_STL_PCT * d_stl - SIM_DEF_BLK_PCT * d_blk
    exp_net = exp_off - exp_def

    assert abs(out.projected_offensive_rating - exp_off) < 1e-9
    assert abs(out.projected_defensive_rating - exp_def) < 1e-9
    assert abs(out.projected_net_rating - exp_net) < 1e-9
    assert abs(out.projected_net_rating - (out.projected_offensive_rating - out.projected_defensive_rating)) < 1e-9
