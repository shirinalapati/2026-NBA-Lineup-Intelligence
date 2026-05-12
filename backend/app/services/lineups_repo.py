"""SQL helpers for lineup / player / team reads."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.schemas import SortMetric
from data_pipeline.config import DEFAULT_MIN_LINEUP_MINUTES

SORT_COLS: dict[SortMetric, str] = {
    "net_rating": "net_rating",
    "offensive_rating": "offensive_rating",
    "defensive_rating": "defensive_rating",
    "minutes": "minutes",
    "possessions": "possessions",
    "underrated_lineup_score": "underrated_lineup_score",
}


def fetch_lineups(
    db: Session,
    *,
    min_minutes: float = DEFAULT_MIN_LINEUP_MINUTES,
    team: str | None = None,
    sort: SortMetric = "net_rating",
    position: str | None = None,
    limit: int = 200,
    search: str | None = None,
    fetch_all: bool = False,
) -> list[dict[str, Any]]:
    order = SORT_COLS.get(sort, "net_rating")
    params: dict[str, Any] = {"min_min": min_minutes}
    where = ["minutes >= :min_min"]
    if team:
        where.append("team_abbr = :team")
        params["team"] = team.upper()
    if search:
        where.append(
            "("
            "player_1_name LIKE :q OR player_2_name LIKE :q OR player_3_name LIKE :q OR "
            "player_4_name LIKE :q OR player_5_name LIKE :q OR team_abbr LIKE :q"
            ")"
        )
        params["q"] = f"%{search}%"
    pos_extra = ""
    if position:
        pos_like = f"%{position.upper()}%"
        params["pos_like"] = pos_like
        pos_extra = """ AND (
          EXISTS (SELECT 1 FROM players p WHERE p.player_id = lineups.player_1_id AND UPPER(IFNULL(p.position,'')) LIKE :pos_like)
          OR EXISTS (SELECT 1 FROM players p WHERE p.player_id = lineups.player_2_id AND UPPER(IFNULL(p.position,'')) LIKE :pos_like)
          OR EXISTS (SELECT 1 FROM players p WHERE p.player_id = lineups.player_3_id AND UPPER(IFNULL(p.position,'')) LIKE :pos_like)
          OR EXISTS (SELECT 1 FROM players p WHERE p.player_id = lineups.player_4_id AND UPPER(IFNULL(p.position,'')) LIKE :pos_like)
          OR EXISTS (SELECT 1 FROM players p WHERE p.player_id = lineups.player_5_id AND UPPER(IFNULL(p.position,'')) LIKE :pos_like)
        )"""

    # Secondary sort by minutes so "best net" lists stay stable when ratings tie or are close
    eff_limit = 0 if fetch_all else limit
    limit_clause = ""
    if eff_limit != 0:
        params["lim"] = eff_limit
        limit_clause = "LIMIT :lim"

    sql = f"""
    SELECT * FROM lineups
    WHERE {" AND ".join(where)}
    {pos_extra}
    ORDER BY {order} DESC, minutes DESC
    {limit_clause}
    """
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


def fetch_lineup_by_id(db: Session, lineup_id: str) -> dict[str, Any] | None:
    r = db.execute(text("SELECT * FROM lineups WHERE lineup_id = :lid"), {"lid": lineup_id}).mappings().first()
    return dict(r) if r else None


def fetch_player(db: Session, player_id: int) -> dict[str, Any] | None:
    r = db.execute(text("SELECT * FROM players WHERE player_id = :pid"), {"pid": player_id}).mappings().first()
    return dict(r) if r else None


def fetch_team(db: Session, team_abbr: str) -> dict[str, Any] | None:
    r = db.execute(
        text("SELECT * FROM teams WHERE team_abbr = :t"),
        {"t": team_abbr.upper()},
    ).mappings().first()
    return dict(r) if r else None


def fetch_players_by_team(db: Session, team_abbr: str) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT * FROM players WHERE team_abbr = :t ORDER BY minutes_played DESC NULLS LAST, player_name"
        ),
        {"t": team_abbr.upper()},
    ).mappings().all()
    return [dict(r) for r in rows]


def fetch_teams(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(text("SELECT * FROM teams ORDER BY team_abbr")).mappings().all()
    return [dict(r) for r in rows]
