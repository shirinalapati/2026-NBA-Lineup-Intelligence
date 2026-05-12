"""Fetch player advanced / base stats (regular season)."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from sqlalchemy import text
from sqlalchemy.engine import Engine

from data_pipeline.config import SEASON, SEASON_TYPE
from data_pipeline.db import get_engine

logger = logging.getLogger(__name__)


def _rate_0_1(x: object) -> float | None:
    """NBA.com sometimes returns pct stats as 0–1 or 0–100; normalize to decimal rate."""
    if x is None:
        return None
    if isinstance(x, (float, np.floating)) and pd.isna(x):
        return None
    v = float(x)
    if v > 1.25:
        return v / 100.0
    return v


def fetch_players_df() -> pd.DataFrame:
    adv = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON,
        season_type_all_star=SEASON_TYPE,
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="PerGame",
        timeout=90,
    )
    df = adv.get_data_frames()[0]

    # Proxy impact metrics when BPM not on NBA.com advanced table
    lo = df["OFF_RATING"].quantile(0.1) if "OFF_RATING" in df.columns else 108
    ld = df["DEF_RATING"].quantile(0.9) if "DEF_RATING" in df.columns else 116
    if "OFF_RATING" in df.columns:
        df["OBPM_PROXY"] = (df["OFF_RATING"] - lo) / 8.0
    else:
        df["OBPM_PROXY"] = 0.0
    if "DEF_RATING" in df.columns:
        df["DBPM_PROXY"] = (ld - df["DEF_RATING"]) / 8.0
    else:
        df["DBPM_PROXY"] = 0.0
    if "NET_RATING" in df.columns:
        df["BPM_PROXY"] = df["NET_RATING"] / 12.0
    else:
        df["BPM_PROXY"] = df["OBPM_PROXY"] + df["DBPM_PROXY"]

    pos = df["PLAYER_POSITION"] if "PLAYER_POSITION" in df.columns else pd.Series(["F-G"] * len(df))
    out = pd.DataFrame(
        {
            "player_id": df["PLAYER_ID"],
            "player_name": df["PLAYER_NAME"],
            "team_abbr": df["TEAM_ABBREVIATION"],
            "position": pos,
        }
    )

    out["games_played"] = df["GP"]
    out["minutes_played"] = df["MIN"]
    out["points_per_game"] = df["PTS"] if "PTS" in df.columns else None
    out["rebounds_per_game"] = df["REB"] if "REB" in df.columns else None
    out["assists_per_game"] = df["AST"] if "AST" in df.columns else None
    out["ts_pct"] = df.get("TS_PCT")
    out["efg_pct"] = df.get("EFG_PCT")
    out["bpm"] = df.get("BPM_PROXY")
    out["obpm"] = df.get("OBPM_PROXY")
    out["dbpm"] = df.get("DBPM_PROXY")
    out["offensive_rating"] = df.get("OFF_RATING")
    out["defensive_rating"] = df.get("DEF_RATING")
    out["usage_rate"] = df.get("USG_PCT")
    out["ast_pct"] = df.get("AST_PCT")
    out["tov_pct"] = df.get("TOV_PCT")
    out["fg3_pct"] = df.get("FG3_PCT")
    out["stl"] = df.get("STL", 0)
    out["blk"] = df.get("BLK", 0)
    out["stl_pct"] = df["STL_PCT"].map(_rate_0_1) if "STL_PCT" in df.columns else np.nan
    out["blk_pct"] = df["BLK_PCT"].map(_rate_0_1) if "BLK_PCT" in df.columns else np.nan
    out["oreb_pct"] = df.get("OREB_PCT")
    out["dreb_pct"] = df.get("DREB_PCT")
    out["salary"] = None
    out["season"] = SEASON

    out["position"] = out["position"].fillna("F-G")

    return out.where(pd.notnull(out), None)


def upsert_players(engine: Engine, df: pd.DataFrame) -> int:
    rows = 0
    with engine.begin() as conn:
        for _, r in df.iterrows():
            conn.execute(
                text(
                    """
                INSERT INTO players (
                  player_id, player_name, team_abbr, position, games_played, minutes_played,
                  points_per_game, rebounds_per_game, assists_per_game,
                  ts_pct, efg_pct, bpm, obpm, dbpm, offensive_rating, defensive_rating,
                  usage_rate, ast_pct, tov_pct, fg3_pct, stl, blk, stl_pct, blk_pct,
                  oreb_pct, dreb_pct, salary, season
                ) VALUES (
                  :player_id, :player_name, :team_abbr, :position, :games_played, :minutes_played,
                  :points_per_game, :rebounds_per_game, :assists_per_game,
                  :ts_pct, :efg_pct, :bpm, :obpm, :dbpm, :offensive_rating, :defensive_rating,
                  :usage_rate, :ast_pct, :tov_pct, :fg3_pct, :stl, :blk, :stl_pct, :blk_pct,
                  :oreb_pct, :dreb_pct, :salary, :season
                )
                ON CONFLICT(player_id) DO UPDATE SET
                  player_name = excluded.player_name,
                  team_abbr = excluded.team_abbr,
                  position = excluded.position,
                  games_played = excluded.games_played,
                  minutes_played = excluded.minutes_played,
                  points_per_game = excluded.points_per_game,
                  rebounds_per_game = excluded.rebounds_per_game,
                  assists_per_game = excluded.assists_per_game,
                  ts_pct = excluded.ts_pct,
                  efg_pct = excluded.efg_pct,
                  bpm = excluded.bpm,
                  obpm = excluded.obpm,
                  dbpm = excluded.dbpm,
                  offensive_rating = excluded.offensive_rating,
                  defensive_rating = excluded.defensive_rating,
                  usage_rate = excluded.usage_rate,
                  ast_pct = excluded.ast_pct,
                  tov_pct = excluded.tov_pct,
                  fg3_pct = excluded.fg3_pct,
                  stl = excluded.stl,
                  blk = excluded.blk,
                  stl_pct = excluded.stl_pct,
                  blk_pct = excluded.blk_pct,
                  oreb_pct = excluded.oreb_pct,
                  dreb_pct = excluded.dreb_pct,
                  salary = excluded.salary,
                  season = excluded.season
                """
                ),
                r.to_dict(),
            )
            rows += 1
    return rows


def run(engine: Engine | None = None) -> int:
    eng = engine or get_engine()
    df = fetch_players_df()
    logger.info("Fetched %s players", len(df))
    return upsert_players(eng, df)
