"""
Central configuration for ingestion and scoring.

**Scope (do not change without updating docs + UI):**
- Season: **2025-26** only (`SEASON` must match NBA.com `Season` parameter).
- Games: **Regular Season** only — excludes playoffs, play-in, All-Star, preseason
  (`season_type_all_star` / `SeasonType` = Regular Season in nba_api).
"""

SEASON = "2025-26"
# nba_api SeasonTypeAllStar.regular → "Regular Season"
SEASON_TYPE = "Regular Season"

# Default filters (aligned with product spec)
DEFAULT_MIN_LINEUP_MINUTES = 50.0
# ULS + LUB: only lineups with minutes >= this participate in ULS norms and LUB_raw range
ULS_MIN_MINUTES = 50.0

# Winsorization percentiles (lineup traits / legacy helpers — not used for ULS min-max)
WINSOR_LOW = 0.02
WINSOR_HIGH = 0.98

# ULS weights (must sum to 1.0) — spec
ULS_WEIGHT_NET = 0.35
ULS_WEIGHT_OFF = 0.20
ULS_WEIGHT_INV_DEF = 0.20
ULS_WEIGHT_LIMITED_USAGE = 0.15
ULS_WEIGHT_POSS = 0.10

# Substitution simulator — exact coefficients (TS/AST/TOV/STL/BLK as decimals)
SIM_OFF_OBPM = 1.8
SIM_OFF_TS = 8.0
SIM_OFF_AST_PCT = 0.12
SIM_OFF_TOV_PCT = 0.08
SIM_DEF_DBPM = 1.5
SIM_DEF_STL_PCT = 0.10
SIM_DEF_BLK_PCT = 0.10


def validate_season_scope() -> None:
    """Fail fast if config drifts from the intended 2025-26 regular-season product scope."""
    if SEASON != "2025-26":
        raise ValueError(f"SEASON must be '2025-26' for this product, got {SEASON!r}")
    if SEASON_TYPE != "Regular Season":
        raise ValueError(
            f"SEASON_TYPE must be 'Regular Season' (excludes playoffs/play-in), got {SEASON_TYPE!r}"
        )
