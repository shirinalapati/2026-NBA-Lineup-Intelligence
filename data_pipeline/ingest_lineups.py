"""Fetch 5-man lineup advanced stats (regular season)."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

import pandas as pd
from nba_api.stats.endpoints import leaguedashlineups
from sqlalchemy import text
from sqlalchemy.engine import Engine

from data_pipeline.config import SEASON, SEASON_TYPE
from data_pipeline.db import get_engine
from data_pipeline.scoring import compute_lineup_traits, compute_uls_for_dataframe

logger = logging.getLogger(__name__)


def _sql_real(x: Any) -> float | None:
    """Bind floats for SQLite; NaN → NULL (SQLite does not store NaN reliably)."""
    if pd.isna(x):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _parse_player_ids(group_id: Any) -> list[int]:
    if group_id is None or (isinstance(group_id, float) and pd.isna(group_id)):
        return []
    s = str(group_id).strip()
    parts = re.split(r"[-–]", s)
    ids: list[int] = []
    for p in parts:
        p = p.strip()
        if p.isdigit():
            ids.append(int(p))
    return ids[:5]


def _parse_player_names(group_name: Any) -> list[str]:
    if group_name is None or (isinstance(group_name, float) and pd.isna(group_name)):
        return []
    s = str(group_name)
    parts = re.split(r"\s*[-–]\s*", s)
    return [p.strip() for p in parts if p.strip()][:5]


def _make_lineup_id(team_abbr: str, player_ids: list[int]) -> str:
    key = team_abbr + "|" + "-".join(sorted(str(i) for i in player_ids))
    return hashlib.sha256(key.encode()).hexdigest()[:24]


def fetch_lineups_df() -> pd.DataFrame:
    e = leaguedashlineups.LeagueDashLineups(
        season=SEASON,
        season_type_all_star=SEASON_TYPE,
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="Per100Possessions",
        group_quantity="5",
        timeout=120,
    )
    df = e.get_data_frames()[0]
    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        pids = _parse_player_ids(r.get("GROUP_ID"))
        names = _parse_player_names(r.get("GROUP_NAME"))
        team = r.get("TEAM_ABBREVIATION")
        if not team:
            continue
        while len(names) < 5:
            names.append("Unknown")
        names = names[:5]
        while len(pids) < 5:
            pids.append(None)
        pids = pids[:5]
        pids = [int(x) if x is not None else None for x in pids]

        poss = r.get("POSS")
        if poss is None or (isinstance(poss, float) and pd.isna(poss)):
            pace = r.get("PACE") or 100.0
            mn = float(r.get("MIN") or 0)
            poss = max(1.0, (pace / 48.0) * mn)

        row = {
            "team_abbr": team,
            "player_1_id": pids[0],
            "player_2_id": pids[1],
            "player_3_id": pids[2],
            "player_4_id": pids[3],
            "player_5_id": pids[4],
            "player_1_name": names[0],
            "player_2_name": names[1],
            "player_3_name": names[2],
            "player_4_name": names[3],
            "player_5_name": names[4],
            "minutes": float(r.get("MIN") or 0),
            "possessions": float(poss),
            "offensive_rating": r.get("OFF_RATING"),
            "defensive_rating": r.get("DEF_RATING"),
            "net_rating": r.get("NET_RATING"),
            "pace": r.get("PACE"),
            "ast_pct": r.get("AST_PCT"),
            "reb_pct": r.get("REB_PCT"),
            "tov_pct": r.get("TOV_PCT"),
            "efg_pct": r.get("EFG_PCT"),
            "season": SEASON,
        }
        real_ids = [x for x in pids if x and x > 0]
        if len(real_ids) == 5:
            lid = _make_lineup_id(team, sorted(real_ids))
        elif len(real_ids) >= 1:
            lid = _make_lineup_id(team, sorted(real_ids + [hash(names[i]) % 10_000 for i in range(5)]))
        else:
            lid = _make_lineup_id(team, [hash(n) % 10_000_000 for n in names])
        row["lineup_id"] = lid
        rows.append(row)

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.dropna(subset=["offensive_rating", "defensive_rating", "net_rating"], how="any")
    return out


def enrich_traits_and_uls(engine: Engine) -> None:
    """Compute spacing/playmaking/defense/reb traits and ULS from joined players."""
    from data_pipeline.scoring import normalize_0_100

    with engine.connect() as conn:
        lu = pd.read_sql(text("SELECT * FROM lineups"), conn)
        pl = pd.read_sql(text("SELECT * FROM players"), conn)

    if lu.empty:
        return

    pl_idx = pl.set_index("player_id")

    traits_list: list[dict[str, float]] = []
    for _, row in lu.iterrows():
        ids = [
            row.get("player_1_id"),
            row.get("player_2_id"),
            row.get("player_3_id"),
            row.get("player_4_id"),
            row.get("player_5_id"),
        ]
        frames: list[pd.Series] = []
        for pid in ids:
            try:
                ip = int(pid) if pid is not None else 0
            except (TypeError, ValueError):
                ip = 0
            if ip and ip in pl_idx.index:
                frames.append(pl_idx.loc[ip])
        if frames:
            sub = pd.DataFrame(frames)
            t = compute_lineup_traits(sub)
        else:
            t = {
                "spacing_score": 0.55,
                "playmaking_score": 0.45,
                "defensive_activity_score": 0.45,
                "rebounding_score": 0.45,
            }
        traits_list.append(t)

    trait_df = pd.DataFrame(traits_list)
    for c in ["spacing_score", "playmaking_score", "defensive_activity_score", "rebounding_score"]:
        lu[c] = normalize_0_100(trait_df[c])

    lu["underrated_lineup_score"] = compute_uls_for_dataframe(lu)

    with engine.begin() as conn:
        for _, r in lu.iterrows():
            conn.execute(
                text(
                    """
                UPDATE lineups SET
                  spacing_score = :sp, playmaking_score = :pl, defensive_activity_score = :df,
                  rebounding_score = :rb, underrated_lineup_score = :uls
                WHERE lineup_id = :lid
                """
                ),
                {
                    "sp": _sql_real(r["spacing_score"]),
                    "pl": _sql_real(r["playmaking_score"]),
                    "df": _sql_real(r["defensive_activity_score"]),
                    "rb": _sql_real(r["rebounding_score"]),
                    "uls": _sql_real(r["underrated_lineup_score"]),
                    "lid": str(r["lineup_id"]),
                },
            )


def upsert_lineups(engine: Engine, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rows = 0
    with engine.begin() as conn:
        for _, r in df.iterrows():
            conn.execute(
                text(
                    """
            INSERT INTO lineups (
              lineup_id, team_abbr,
              player_1_id, player_1_name, player_2_id, player_2_name,
              player_3_id, player_3_name, player_4_id, player_4_name,
              player_5_id, player_5_name,
              minutes, possessions, offensive_rating, defensive_rating, net_rating,
              pace, ast_pct, reb_pct, tov_pct, efg_pct,
              spacing_score, playmaking_score, defensive_activity_score, rebounding_score,
              underrated_lineup_score, season
            ) VALUES (
              :lineup_id, :team_abbr,
              :player_1_id, :player_1_name, :player_2_id, :player_2_name,
              :player_3_id, :player_3_name, :player_4_id, :player_4_name,
              :player_5_id, :player_5_name,
              :minutes, :possessions, :offensive_rating, :defensive_rating, :net_rating,
              :pace, :ast_pct, :reb_pct, :tov_pct, :efg_pct,
              :spacing_score, :playmaking_score, :defensive_activity_score, :rebounding_score,
              :underrated_lineup_score, :season
            )
            ON CONFLICT(lineup_id) DO UPDATE SET
              team_abbr = excluded.team_abbr,
              player_1_id = excluded.player_1_id,
              player_1_name = excluded.player_1_name,
              player_2_id = excluded.player_2_id,
              player_2_name = excluded.player_2_name,
              player_3_id = excluded.player_3_id,
              player_3_name = excluded.player_3_name,
              player_4_id = excluded.player_4_id,
              player_4_name = excluded.player_4_name,
              player_5_id = excluded.player_5_id,
              player_5_name = excluded.player_5_name,
              minutes = excluded.minutes,
              possessions = excluded.possessions,
              offensive_rating = excluded.offensive_rating,
              defensive_rating = excluded.defensive_rating,
              net_rating = excluded.net_rating,
              pace = excluded.pace,
              ast_pct = excluded.ast_pct,
              reb_pct = excluded.reb_pct,
              tov_pct = excluded.tov_pct,
              efg_pct = excluded.efg_pct,
              spacing_score = excluded.spacing_score,
              playmaking_score = excluded.playmaking_score,
              defensive_activity_score = excluded.defensive_activity_score,
              rebounding_score = excluded.rebounding_score,
              underrated_lineup_score = excluded.underrated_lineup_score,
              season = excluded.season
            """
                ),
                {
                    "lineup_id": r["lineup_id"],
                    "team_abbr": r["team_abbr"],
                    "player_1_id": r.get("player_1_id"),
                    "player_1_name": r.get("player_1_name"),
                    "player_2_id": r.get("player_2_id"),
                    "player_2_name": r.get("player_2_name"),
                    "player_3_id": r.get("player_3_id"),
                    "player_3_name": r.get("player_3_name"),
                    "player_4_id": r.get("player_4_id"),
                    "player_4_name": r.get("player_4_name"),
                    "player_5_id": r.get("player_5_id"),
                    "player_5_name": r.get("player_5_name"),
                    "minutes": r["minutes"],
                    "possessions": r["possessions"],
                    "offensive_rating": r["offensive_rating"],
                    "defensive_rating": r["defensive_rating"],
                    "net_rating": r["net_rating"],
                    "pace": r.get("pace"),
                    "ast_pct": r.get("ast_pct"),
                    "reb_pct": r.get("reb_pct"),
                    "tov_pct": r.get("tov_pct"),
                    "efg_pct": r.get("efg_pct"),
                    "spacing_score": r.get("spacing_score"),
                    "playmaking_score": r.get("playmaking_score"),
                    "defensive_activity_score": r.get("defensive_activity_score"),
                    "rebounding_score": r.get("rebounding_score"),
                    "underrated_lineup_score": r.get("underrated_lineup_score"),
                    "season": r["season"],
                },
            )
            rows += 1
    return rows


def run(engine: Engine | None = None) -> int:
    eng = engine or get_engine()
    df = fetch_lineups_df()
    logger.info("Fetched %s lineups raw", len(df))
    if df.empty:
        return 0
    # placeholder scores; filled in enrich
    for c in [
        "spacing_score",
        "playmaking_score",
        "defensive_activity_score",
        "rebounding_score",
        "underrated_lineup_score",
    ]:
        if c not in df.columns:
            df[c] = None
    n = upsert_lineups(eng, df)
    enrich_traits_and_uls(eng)
    return n
