"""
Normalization, lineup trait scores, Underrated Lineup Score (ULS), and Limited Usage Bonus (LUB).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from data_pipeline.config import (
    ULS_MIN_MINUTES,
    ULS_WEIGHT_INV_DEF,
    ULS_WEIGHT_LIMITED_USAGE,
    ULS_WEIGHT_NET,
    ULS_WEIGHT_OFF,
    ULS_WEIGHT_POSS,
    WINSOR_HIGH,
    WINSOR_LOW,
)


def winsorize_series(s: pd.Series, low: float = WINSOR_LOW, high: float = WINSOR_HIGH) -> pd.Series:
    if s.empty:
        return s
    lo = s.quantile(low)
    hi = s.quantile(high)
    return s.clip(lower=lo, upper=hi)


def normalize_0_100(s: pd.Series) -> pd.Series:
    """Min-max to 0–100 after winsorization (used for lineup trait blending, not ULS)."""
    s = winsorize_series(s)
    mn, mx = s.min(), s.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(50.0, index=s.index)
    return ((s - mn) / (mx - mn)) * 100.0


def uls_minmax_0_100(s: pd.Series) -> pd.Series:
    """Pure min-max to 0–100 (no winsorization). Safe when max == min."""
    s = pd.to_numeric(s, errors="coerce")
    mn, mx = float(s.min()), float(s.max())
    if np.isnan(mn) or np.isnan(mx) or mx == mn:
        return pd.Series(50.0, index=s.index)
    return (s - mn) / (mx - mn) * 100.0


def invert_for_defense(s: pd.Series) -> pd.Series:
    """Lower defensive rating is better — invert before normalization."""
    return -s


def limited_usage_bonus_raw(minutes: pd.Series) -> pd.Series:
    """
    LUB = 1 - (Minutes - min(Minutes)) / (max(Minutes) - min(Minutes))
    Computed only on a population that already meets the ULS minutes floor (caller filters).
    """
    min_m = float(minutes.min())
    max_m = float(minutes.max())
    if max_m == min_m:
        return pd.Series(1.0, index=minutes.index)
    return 1.0 - (minutes - min_m) / (max_m - min_m)


def compute_uls_for_dataframe(lineups: pd.DataFrame) -> pd.Series:
    """
    ULS = 0.35*norm(Net) + 0.20*norm(Off) + 0.20*norm(invDef) + 0.15*norm(LUB) + 0.10*norm(Poss)

    - All norms are min-max 0–100 on the **eligible** set (minutes >= ULS_MIN_MINUTES only).
    - invDef: invert defensive rating (negate) then min-max.
    - LUB: formula on eligible minutes, then LUB is min-maxed to 0–100 again.
    - Lineups below ULS_MIN_MINUTES get NaN ULS.
    """
    result = pd.Series(np.nan, index=lineups.index, dtype=float)
    req = ["net_rating", "offensive_rating", "defensive_rating", "minutes"]
    if any(c not in lineups.columns for c in req):
        return result
    base = lineups[req].copy()
    for col in req:
        base[col] = pd.to_numeric(base[col], errors="coerce")
    base = base.dropna(subset=req)
    if base.empty:
        return result
    elig = base["minutes"] >= ULS_MIN_MINUTES
    if not elig.any():
        return result

    sub = base.loc[elig].copy()
    if "possessions" in lineups.columns:
        poss = pd.to_numeric(lineups.loc[sub.index, "possessions"], errors="coerce")
    else:
        poss = pd.Series(np.nan, index=sub.index)
    poss = poss.fillna(sub["minutes"] * 2.0)

    n_net = uls_minmax_0_100(sub["net_rating"])
    n_off = uls_minmax_0_100(sub["offensive_rating"])
    n_invdef = uls_minmax_0_100(invert_for_defense(sub["defensive_rating"]))

    lub_step1 = limited_usage_bonus_raw(sub["minutes"])
    n_lub = uls_minmax_0_100(lub_step1)

    n_poss = uls_minmax_0_100(poss)

    uls = (
        ULS_WEIGHT_NET * n_net
        + ULS_WEIGHT_OFF * n_off
        + ULS_WEIGHT_INV_DEF * n_invdef
        + ULS_WEIGHT_LIMITED_USAGE * n_lub
        + ULS_WEIGHT_POSS * n_poss
    )
    result.loc[sub.index] = uls
    return result


def compute_lineup_traits(players_df: pd.DataFrame) -> dict[str, float]:
    """
    Aggregate five player rows into trait scores (0–100 scale within batch elsewhere).
    Expects per-player columns: ts_pct, efg_pct, fg3_pct, ast_pct, ast, tov_pct,
    stl, blk, dbpm, reb, oreb_pct, dreb_pct (nullable).
    """
    n = max(len(players_df), 1)
    ts = players_df.get("ts_pct", pd.Series([0.55] * n)).fillna(0.55)
    efg = players_df.get("efg_pct", pd.Series([0.52] * n)).fillna(0.52)
    fg3 = players_df.get("fg3_pct", pd.Series([0.35] * n)).fillna(0.35)
    ast_pct = players_df.get("ast_pct", pd.Series([0.15] * n)).fillna(0.15)
    ast = players_df.get("assists_per_game", players_df.get("ast", pd.Series([2.0] * n))).fillna(2.0)
    tov = players_df.get("tov_pct", pd.Series([0.12] * n)).fillna(0.12)
    stl = players_df.get("stl", pd.Series([0.8] * n))
    blk = players_df.get("blk", pd.Series([0.4] * n))
    stl = pd.to_numeric(stl, errors="coerce").fillna(0.8)
    blk = pd.to_numeric(blk, errors="coerce").fillna(0.4)
    dbpm = players_df.get("dbpm", pd.Series([0.0] * n)).fillna(0.0)
    reb = players_df.get("rebounds_per_game", pd.Series([4.0] * n)).fillna(4.0)

    spacing = float((0.4 * fg3 + 0.35 * efg + 0.25 * ts).mean())
    playmaking = float((0.45 * ast_pct + 0.35 * (ast / 10.0).clip(0, 1) + 0.2 * (1 - tov)).mean())
    def_activity = float((0.35 * (stl / 2.5).clip(0, 1) + 0.35 * (blk / 2.0).clip(0, 1) + 0.3 * (dbpm + 3) / 6).mean())
    rebounding = float((reb / 12.0).clip(0, 1).mean())

    return {
        "spacing_score": spacing,
        "playmaking_score": playmaking,
        "defensive_activity_score": def_activity,
        "rebounding_score": rebounding,
    }


def trait_scores_to_0_100(val: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 50.0
    return float(np.clip((val - lo) / (hi - lo) * 100.0, 0.0, 100.0))
