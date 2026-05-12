"""
Fetch 2025-26 regular-season player → team mapping from NBA Stats (same contract as live ingest).

Used by synthetic seed so demo lineups use **correct team rosters** instead of random active players.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import teams as static_teams

from data_pipeline.config import SEASON, SEASON_TYPE

logger = logging.getLogger(__name__)

ROSTER_CAP = 17  # max players per team to mirror typical roster depth in seed stats


def fetch_regular_season_rosters_by_team(timeout: int = 120) -> dict[str, list[dict[str, Any]]] | None:
    """
    Returns ``team_abbr -> [{id, full_name, position, min}, ...]`` for NBA teams only.

    Traded players: keep the team where they logged the **most minutes** (``idxmax`` on ``MIN``).
    """
    try:
        adv = leaguedashplayerstats.LeagueDashPlayerStats(
            season=SEASON,
            season_type_all_star=SEASON_TYPE,
            measure_type_detailed_defense="Base",
            per_mode_detailed="PerGame",
            timeout=timeout,
        )
        df = adv.get_data_frames()[0]
    except Exception as exc:
        logger.warning("Could not fetch LeagueDashPlayerStats for seeded rosters: %s", exc)
        return None

    if df.empty or "PLAYER_ID" not in df.columns:
        return None

    nba_abbrs = {t["abbreviation"] for t in static_teams.get_teams()}
    df = df[df["TEAM_ABBREVIATION"].isin(nba_abbrs)].copy()

    # One row per player: primary team = most minutes (handles mid-season trades)
    if "MIN" in df.columns:
        df["_min"] = pd.to_numeric(df["MIN"], errors="coerce").fillna(0.0)
        # Traded players: keep the team row with the most minutes in 2025-26 RS
        df = df.sort_values("_min", ascending=False).drop_duplicates("PLAYER_ID", keep="first")
    else:
        df = df.drop_duplicates(subset=["PLAYER_ID"], keep="first")

    by_team: dict[str, list[dict[str, Any]]] = {abbr: [] for abbr in sorted(nba_abbrs)}

    for abbr in sorted(nba_abbrs):
        sub = df[df["TEAM_ABBREVIATION"] == abbr].copy()
        if "MIN" in sub.columns:
            sub["_m"] = pd.to_numeric(sub["MIN"], errors="coerce").fillna(0.0)
            sub = sub.sort_values("_m", ascending=False)
        sub = sub.head(ROSTER_CAP)
        for _, r in sub.iterrows():
            pos = r.get("PLAYER_POSITION")
            if pos is None or (isinstance(pos, float) and pd.isna(pos)):
                pos = "F-G"
            by_team[abbr].append(
                {
                    "id": int(r["PLAYER_ID"]),
                    "full_name": str(r["PLAYER_NAME"]).strip(),
                    "position": str(pos),
                    "min_season": float(r["MIN"]) if pd.notna(r.get("MIN")) else 0.0,
                }
            )

    # Require enough depth to build 5-man lineups everywhere
    short = [t for t, rows in by_team.items() if len(rows) < 5]
    if short:
        logger.warning("Roster fetch returned <%s players for teams: %s", 5, short[:10])
        return None

    logger.info(
        "Loaded 2025-26 RS rosters from NBA Stats: %s team mappings (season=%s, type=%s)",
        len(by_team),
        SEASON,
        SEASON_TYPE,
    )
    return by_team
