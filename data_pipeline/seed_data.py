"""
Deterministic synthetic 2025-26 regular-season dataset for offline demo only.

Use `python -m data_pipeline.ingest_all --seed` or `python -m data_pipeline.seed_data`.
Live installs should use `python -m data_pipeline.ingest_all` (no `--seed`) for real NBA Stats.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import numpy as np
import pandas as pd
from nba_api.stats.static import players as static_players
from nba_api.stats.static import teams as static_teams
from sqlalchemy import text
from sqlalchemy.engine import Engine

from data_pipeline.config import SEASON, validate_season_scope
from data_pipeline.db import clear_tables, get_engine, init_schema
from data_pipeline.ingestion_meta import write_scope_meta
from data_pipeline.seed_rosters import fetch_regular_season_rosters_by_team

from data_pipeline.ingest_lineups import enrich_traits_and_uls

logger = logging.getLogger(__name__)

RNG = np.random.default_rng(42)

POSITIONS = ["G", "G", "F", "F", "C", "F-G", "G-F"]

ROSTER_SIZE = 17
TEAM_COUNT = 30
PLAYERS_NEEDED = ROSTER_SIZE * TEAM_COUNT  # 510 (scrambled fallback only)


def _lineup_id(team: str, pids: list[int]) -> str:
    key = team + "|" + "-".join(sorted(str(p) for p in pids))
    return hashlib.sha256(key.encode()).hexdigest()[:24]


def _synthetic_player_row(
    abbr: str,
    player_id: int,
    player_name: str,
    position: str,
    base_off: float,
    base_def: float,
) -> dict[str, Any]:
    skill = RNG.normal(0, 1)
    ts = float(np.clip(0.52 + 0.04 * skill, 0.48, 0.68))
    efg = float(np.clip(0.50 + 0.04 * skill, 0.45, 0.66))
    fg3 = float(np.clip(0.33 + 0.05 * skill, 0.28, 0.45))
    ast_pct = float(np.clip(0.12 + 0.04 * skill, 0.05, 0.35))
    tov_pct = float(np.clip(0.11 + 0.02 * RNG.normal(), 0.07, 0.18))
    off_rtg = float(np.clip(base_off + skill * 4.0, 102, 128))
    def_rtg = float(np.clip(base_def - skill * 3.5, 106, 122))
    return {
        "player_id": player_id,
        "player_name": player_name,
        "team_abbr": abbr,
        "position": position,
        "games_played": int(RNG.integers(45, 83)),
        "minutes_played": float(RNG.uniform(8, 36)),
        "points_per_game": float(np.clip(6 + skill * 4, 0, 32)),
        "rebounds_per_game": float(np.clip(3 + skill * 1.5, 0, 14)),
        "assists_per_game": float(np.clip(2 + skill * 2.5, 0, 11)),
        "ts_pct": ts,
        "efg_pct": efg,
        "bpm": float(skill * 1.2),
        "obpm": float(skill * 0.8),
        "dbpm": float(skill * 0.6),
        "offensive_rating": off_rtg,
        "defensive_rating": def_rtg,
        "usage_rate": float(np.clip(0.12 + 0.1 * skill, 0.08, 0.36)),
        "ast_pct": ast_pct,
        "tov_pct": tov_pct,
        "fg3_pct": fg3,
        "stl": float(np.clip(0.5 + skill * 0.4, 0, 2.2)),
        "blk": float(np.clip(0.3 + skill * 0.3, 0, 2.5)),
        "stl_pct": float(np.clip(0.012 + 0.008 * skill, 0.005, 0.045)),
        "blk_pct": float(np.clip(0.018 + 0.014 * skill, 0.004, 0.085)),
        "oreb_pct": float(np.clip(0.04 + 0.02 * skill, 0.01, 0.12)),
        "dreb_pct": float(np.clip(0.12 + 0.04 * skill, 0.05, 0.28)),
        "salary": None,
        "season": SEASON,
    }


def _append_lineups_for_team(
    abbr: str,
    roster_pids: list[int],
    name_by_id: dict[int, str],
    base_off: float,
    base_def: float,
    pace: float,
    lineup_rows: list[dict[str, Any]],
) -> None:
    if len(roster_pids) < 5:
        return
    for _ in range(24):
        choice = RNG.choice(roster_pids, size=5, replace=False)
        p5 = sorted([int(x) for x in choice])
        minutes = float(RNG.exponential(35) + 25)
        if RNG.random() < 0.35:
            minutes = float(RNG.uniform(50, 220))
        off = float(base_off + RNG.normal(0, 4))
        deff = float(base_def + RNG.normal(0, 4))
        net = off - deff
        poss = max(20.0, minutes * (pace / 48.0) * 1.8)
        names = [name_by_id[x] for x in p5]
        lid = _lineup_id(abbr, p5)
        lineup_rows.append(
            {
                "lineup_id": lid,
                "team_abbr": abbr,
                "player_1_id": p5[0],
                "player_1_name": names[0],
                "player_2_id": p5[1],
                "player_2_name": names[1],
                "player_3_id": p5[2],
                "player_3_name": names[2],
                "player_4_id": p5[3],
                "player_4_name": names[3],
                "player_5_id": p5[4],
                "player_5_name": names[4],
                "minutes": minutes,
                "possessions": poss,
                "offensive_rating": off,
                "defensive_rating": deff,
                "net_rating": net,
                "pace": pace,
                "ast_pct": float(np.clip(0.45 + RNG.normal() * 0.08, 0.25, 0.72)),
                "reb_pct": float(np.clip(0.48 + RNG.normal() * 0.05, 0.38, 0.62)),
                "tov_pct": float(np.clip(0.11 + RNG.normal() * 0.02, 0.07, 0.18)),
                "efg_pct": float(np.clip(0.52 + RNG.normal() * 0.03, 0.44, 0.64)),
                "season": SEASON,
            }
        )


def _frames_from_nba_rosters(
    nba: list[dict[str, Any]],
    rosters: dict[str, list[dict[str, Any]]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Correct team assignments from LeagueDashPlayerStats (2025-26 RS)."""
    team_rows: list[dict[str, Any]] = []
    player_rows: list[dict[str, Any]] = []
    lineup_rows: list[dict[str, Any]] = []
    name_by_id: dict[int, str] = {}

    for tm in nba:
        abbr = tm["abbreviation"]
        tname = tm["full_name"]
        base_off = float(RNG.normal(114.5, 3.0))
        base_def = float(RNG.normal(113.8, 3.0))
        pace = float(RNG.normal(99.5, 2.0))
        team_rows.append(
            {
                "team_abbr": abbr,
                "team_name": tname,
                "offensive_rating": base_off,
                "defensive_rating": base_def,
                "net_rating": base_off - base_def,
                "pace": pace,
            }
        )
        roster = rosters.get(abbr, [])
        roster_pids: list[int] = []
        for rp in roster:
            pid = int(rp["id"])
            pname = str(rp["full_name"])
            roster_pids.append(pid)
            name_by_id[pid] = pname
            pos = str(rp.get("position") or "F-G")
            player_rows.append(_synthetic_player_row(abbr, pid, pname, pos, base_off, base_def))

        _append_lineups_for_team(abbr, roster_pids, name_by_id, base_off, base_def, pace, lineup_rows)

    return pd.DataFrame(team_rows), pd.DataFrame(player_rows), pd.DataFrame(lineup_rows)


def _load_active_player_pool() -> list[dict[str, Any]]:
    raw = static_players.get_active_players()
    pool = [p for p in raw if p.get("full_name") and p.get("id")]
    if len(pool) < PLAYERS_NEEDED:
        raise RuntimeError(
            f"Active player list too small for {ROSTER_SIZE}/team × {TEAM_COUNT} teams: "
            f"{len(pool)} < {PLAYERS_NEEDED}. Lower ROSTER_SIZE or refresh nba_api."
        )
    return pool


def _pick_players_for_seed(pool: list[dict[str, Any]]) -> list[dict[str, Any]]:
    n = len(pool)
    indices = RNG.choice(n, size=PLAYERS_NEEDED, replace=False)
    return [pool[int(i)] for i in indices]


def _frames_scrambled_fallback(nba: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Offline-only: random active players assigned to teams (misaligned rosters)."""
    pool = sorted(_load_active_player_pool(), key=lambda x: int(x["id"]))
    real_players = _pick_players_for_seed(pool)
    name_by_id = {int(p["id"]): str(p["full_name"]) for p in real_players}

    team_rows: list[dict[str, Any]] = []
    player_rows: list[dict[str, Any]] = []
    lineup_rows: list[dict[str, Any]] = []

    player_iter = iter(real_players)

    for tm in nba:
        abbr = tm["abbreviation"]
        name = tm["full_name"]
        base_off = float(RNG.normal(114.5, 3.0))
        base_def = float(RNG.normal(113.8, 3.0))
        pace = float(RNG.normal(99.5, 2.0))
        team_rows.append(
            {
                "team_abbr": abbr,
                "team_name": name,
                "offensive_rating": base_off,
                "defensive_rating": base_def,
                "net_rating": base_off - base_def,
                "pace": pace,
            }
        )

        roster_pids: list[int] = []
        for _ in range(ROSTER_SIZE):
            rp = next(player_iter)
            pid = int(rp["id"])
            pname = str(rp["full_name"])
            roster_pids.append(pid)
            pos = POSITIONS[int(RNG.integers(0, len(POSITIONS)))]
            player_rows.append(_synthetic_player_row(abbr, pid, pname, pos, base_off, base_def))

        _append_lineups_for_team(abbr, roster_pids, name_by_id, base_off, base_def, pace, lineup_rows)

    return pd.DataFrame(team_rows), pd.DataFrame(player_rows), pd.DataFrame(lineup_rows)


def build_seed_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, bool]:
    """
    Prefer NBA Stats **2025-26 regular-season** team rosters so player ↔ team matches reality.

    Returns (teams_df, players_df, lineups_df, used_api_rosters).
    """
    nba = sorted(static_teams.get_teams(), key=lambda x: x["abbreviation"])
    rosters = fetch_regular_season_rosters_by_team()
    if rosters is not None:
        logger.info("Seed using NBA Stats team rosters (2025-26 regular season).")
        tdf, pdf, ldf = _frames_from_nba_rosters(nba, rosters)
        return tdf, pdf, ldf, True

    logger.warning(
        "NBA Stats roster fetch failed — using scrambled active players (teams will NOT match real life). "
        "Retry when stats.nba.com is reachable."
    )
    tdf, pdf, ldf = _frames_scrambled_fallback(nba)
    return tdf, pdf, ldf, False


def _upsert_teams(engine: Engine, df: pd.DataFrame) -> None:
    with engine.begin() as conn:
        for _, r in df.iterrows():
            conn.execute(
                text(
                    """
            INSERT INTO teams (team_abbr, team_name, offensive_rating, defensive_rating, net_rating, pace)
            VALUES (:team_abbr,:team_name,:offensive_rating,:defensive_rating,:net_rating,:pace)
            ON CONFLICT(team_abbr) DO UPDATE SET
              team_name=excluded.team_name, offensive_rating=excluded.offensive_rating,
              defensive_rating=excluded.defensive_rating, net_rating=excluded.net_rating, pace=excluded.pace
            """
                ),
                dict(r),
            )


def _upsert_players(engine: Engine, df: pd.DataFrame) -> None:
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
              :player_id,:player_name,:team_abbr,:position,:games_played,:minutes_played,
              :points_per_game,:rebounds_per_game,:assists_per_game,
              :ts_pct,:efg_pct,:bpm,:obpm,:dbpm,:offensive_rating,:defensive_rating,
              :usage_rate,:ast_pct,:tov_pct,:fg3_pct,:stl,:blk,:stl_pct,:blk_pct,
              :oreb_pct,:dreb_pct,:salary,:season
            )
            ON CONFLICT(player_id) DO UPDATE SET
              player_name=excluded.player_name, team_abbr=excluded.team_abbr, position=excluded.position,
              games_played=excluded.games_played, minutes_played=excluded.minutes_played,
              points_per_game=excluded.points_per_game, rebounds_per_game=excluded.rebounds_per_game,
              assists_per_game=excluded.assists_per_game,
              ts_pct=excluded.ts_pct, efg_pct=excluded.efg_pct, bpm=excluded.bpm, obpm=excluded.obpm, dbpm=excluded.dbpm,
              offensive_rating=excluded.offensive_rating, defensive_rating=excluded.defensive_rating,
              usage_rate=excluded.usage_rate, ast_pct=excluded.ast_pct, tov_pct=excluded.tov_pct, fg3_pct=excluded.fg3_pct,
              stl=excluded.stl, blk=excluded.blk, stl_pct=excluded.stl_pct, blk_pct=excluded.blk_pct,
              oreb_pct=excluded.oreb_pct, dreb_pct=excluded.dreb_pct,
              salary=excluded.salary, season=excluded.season
            """
                ),
                dict(r),
            )


def _upsert_lineups_raw(engine: Engine, df: pd.DataFrame) -> None:
    with engine.begin() as conn:
        for _, r in df.iterrows():
            row = r.to_dict()
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
              :lineup_id,:team_abbr,
              :player_1_id,:player_1_name,:player_2_id,:player_2_name,
              :player_3_id,:player_3_name,:player_4_id,:player_4_name,
              :player_5_id,:player_5_name,
              :minutes,:possessions,:offensive_rating,:defensive_rating,:net_rating,
              :pace,:ast_pct,:reb_pct,:tov_pct,:efg_pct,
              NULL,NULL,NULL,NULL,NULL,:season
            )
            ON CONFLICT(lineup_id) DO UPDATE SET
              team_abbr=excluded.team_abbr,
              player_1_id=excluded.player_1_id, player_1_name=excluded.player_1_name,
              player_2_id=excluded.player_2_id, player_2_name=excluded.player_2_name,
              player_3_id=excluded.player_3_id, player_3_name=excluded.player_3_name,
              player_4_id=excluded.player_4_id, player_4_name=excluded.player_4_name,
              player_5_id=excluded.player_5_id, player_5_name=excluded.player_5_name,
              minutes=excluded.minutes, possessions=excluded.possessions,
              offensive_rating=excluded.offensive_rating, defensive_rating=excluded.defensive_rating,
              net_rating=excluded.net_rating, pace=excluded.pace,
              ast_pct=excluded.ast_pct, reb_pct=excluded.reb_pct, tov_pct=excluded.tov_pct, efg_pct=excluded.efg_pct,
              season=excluded.season
            """
                ),
                row,
            )


def run(engine: Engine | None = None) -> None:
    validate_season_scope()
    eng = engine or get_engine()
    init_schema(eng)
    clear_tables(eng)
    teams_df, players_df, lineups_df, aligned = build_seed_frames()
    logger.info(
        "Seed: teams=%s players=%s lineups=%s (nba_team_rosters=%s)",
        len(teams_df),
        len(players_df),
        len(lineups_df),
        aligned,
    )
    _upsert_teams(eng, teams_df)
    _upsert_players(eng, players_df)
    _upsert_lineups_raw(eng, lineups_df)
    enrich_traits_and_uls(eng)
    with eng.begin() as conn:
        write_scope_meta(
            conn,
            "synthetic_seed_2025_26",
            extras={
                "roster_mode": "nba_stats_teams" if aligned else "scrambled_active",
            },
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
