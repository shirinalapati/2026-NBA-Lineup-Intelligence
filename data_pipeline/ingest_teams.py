"""Fetch team advanced ratings for the configured season."""

from __future__ import annotations

import logging

import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams as static_teams
from sqlalchemy import text
from sqlalchemy.engine import Engine

from data_pipeline.config import SEASON, SEASON_TYPE
from data_pipeline.db import get_engine

logger = logging.getLogger(__name__)


def fetch_teams_df() -> pd.DataFrame:
    e = leaguedashteamstats.LeagueDashTeamStats(
        season=SEASON,
        season_type_all_star=SEASON_TYPE,
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="Per100Possessions",
        timeout=90,
    )
    df = e.get_data_frames()[0]
    rename = {
        "TEAM_ABBREVIATION": "team_abbr",
        "TEAM_NAME": "team_name",
        "OFF_RATING": "offensive_rating",
        "DEF_RATING": "defensive_rating",
        "NET_RATING": "net_rating",
        "PACE": "pace",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    # NBA.com sometimes omits TEAM_ABBREVIATION; map from TEAM_ID via static team list.
    if "team_abbr" not in df.columns or df["team_abbr"].isna().all():
        id_to_abbr = {int(t["id"]): t["abbreviation"] for t in static_teams.get_teams()}
        if "TEAM_ID" in df.columns:
            df["team_abbr"] = df["TEAM_ID"].map(lambda x: id_to_abbr.get(int(x)) if pd.notna(x) else None)
    cols = ["team_abbr", "team_name", "offensive_rating", "defensive_rating", "net_rating", "pace"]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    out = df[cols].dropna(subset=["team_abbr"])
    return out.drop_duplicates(subset=["team_abbr"])


def upsert_teams(engine: Engine, df: pd.DataFrame) -> int:
    rows = 0
    with engine.begin() as conn:
        for _, r in df.iterrows():
            conn.execute(
                text(
                    """
                INSERT INTO teams (team_abbr, team_name, offensive_rating, defensive_rating, net_rating, pace)
                VALUES (:a, :n, :o, :d, :net, :p)
                ON CONFLICT(team_abbr) DO UPDATE SET
                  team_name = excluded.team_name,
                  offensive_rating = excluded.offensive_rating,
                  defensive_rating = excluded.defensive_rating,
                  net_rating = excluded.net_rating,
                  pace = excluded.pace
                """
                ),
                {
                    "a": r["team_abbr"],
                    "n": r["team_name"],
                    "o": r["offensive_rating"],
                    "d": r["defensive_rating"],
                    "net": r["net_rating"],
                    "p": r["pace"],
                },
            )
            rows += 1
    return rows


def run(engine: Engine | None = None) -> int:
    eng = engine or get_engine()
    df = fetch_teams_df()
    logger.info("Fetched %s teams", len(df))
    return upsert_teams(eng, df)
