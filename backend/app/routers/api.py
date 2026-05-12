from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import (
    LineupOut,
    PlayerOut,
    SeasonScopeOut,
    SimulateSubstitutionIn,
    SimulateSubstitutionOut,
    SortMetric,
    TeamOut,
)
from backend.app.services import lineups_repo
from backend.app.services.simulation import simulate_substitution
from data_pipeline.config import DEFAULT_MIN_LINEUP_MINUTES, SEASON, SEASON_TYPE

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok", "product": "2025-26 NBA Lineup Intelligence"}


@router.get("/scope", response_model=SeasonScopeOut)
def get_season_scope(db: Session = Depends(get_db)):
    """Season + game-type filter stored at ingest time (2025-26 regular season only)."""
    rows = db.execute(text("SELECT key, value FROM ingestion_meta")).mappings().all()
    meta = {r["key"]: r["value"] for r in rows}
    return SeasonScopeOut(
        season=str(meta.get("season", SEASON)),
        season_type=str(meta.get("season_type", SEASON_TYPE)),
        data_source=str(meta.get("source", "unknown")),
        roster_mode=meta.get("roster_mode"),
    )


@router.get("/teams", response_model=list[TeamOut])
def get_teams(db: Session = Depends(get_db)):
    return lineups_repo.fetch_teams(db)


@router.get("/players", response_model=list[PlayerOut])
def get_players(
    team: Optional[str] = None,
    position: Optional[str] = None,
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    rows = lineups_repo.fetch_players_by_team(db, team) if team else _all_players(db, limit)
    if position:
        pl = position.upper()
        rows = [r for r in rows if r.get("position") and pl in str(r["position"]).upper()]
    return rows[:limit]


def _all_players(db: Session, limit: int) -> list[dict]:
    from sqlalchemy import text

    r = db.execute(
        text("SELECT * FROM players ORDER BY team_abbr, player_name LIMIT :lim"),
        {"lim": limit},
    ).mappings().all()
    return [dict(x) for x in r]


@router.get("/lineups", response_model=list[LineupOut])
def get_lineups(
    min_minutes: float = Query(DEFAULT_MIN_LINEUP_MINUTES, ge=0, le=2000),
    team: Optional[str] = None,
    sort: SortMetric = "net_rating",
    position: Optional[str] = None,
    fetch_all: bool = Query(
        False,
        description="If true, return every row matching filters (no LIMIT). Otherwise use `limit`.",
    ),
    limit: int = Query(200, ge=1, le=50_000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    eff_limit = 0 if fetch_all else limit
    return lineups_repo.fetch_lineups(
        db,
        min_minutes=min_minutes,
        team=team,
        sort=sort,
        position=position,
        limit=eff_limit,
        search=search,
    )


@router.get("/lineups/top", response_model=list[LineupOut])
def get_lineups_top(
    min_minutes: float = Query(DEFAULT_MIN_LINEUP_MINUTES, ge=0, le=2000),
    team: Optional[str] = None,
    sort: SortMetric = "net_rating",
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return lineups_repo.fetch_lineups(
        db,
        min_minutes=min_minutes,
        team=team,
        sort=sort,
        position=None,
        limit=limit,
        search=None,
    )


@router.get("/lineups/team/{team}", response_model=list[LineupOut])
def get_lineups_team(
    team: str,
    min_minutes: float = Query(0, ge=0, le=2000),
    sort: SortMetric = "minutes",
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    return lineups_repo.fetch_lineups(
        db,
        min_minutes=min_minutes,
        team=team,
        sort=sort,
        position=None,
        limit=limit,
        search=None,
    )


@router.get("/lineups/underrated", response_model=list[LineupOut])
def get_lineups_underrated(
    min_minutes: float = Query(DEFAULT_MIN_LINEUP_MINUTES, ge=0, le=2000),
    team: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return lineups_repo.fetch_lineups(
        db,
        min_minutes=min_minutes,
        team=team,
        sort="underrated_lineup_score",
        position=None,
        limit=limit,
        search=None,
    )


@router.post("/simulate-substitution", response_model=SimulateSubstitutionOut)
def post_simulate(body: SimulateSubstitutionIn, db: Session = Depends(get_db)):
    lu = lineups_repo.fetch_lineup_by_id(db, body.lineup_id)
    if not lu:
        raise HTTPException(404, "Lineup not found")
    if lu["team_abbr"].upper() != body.team_abbr.upper():
        raise HTTPException(400, "Team does not match lineup")
    pids = [
        lu.get("player_1_id"),
        lu.get("player_2_id"),
        lu.get("player_3_id"),
        lu.get("player_4_id"),
        lu.get("player_5_id"),
    ]
    if body.player_out_id not in [x for x in pids if x]:
        raise HTTPException(400, "Player to remove is not in this lineup")
    if body.player_in_id in [x for x in pids if x]:
        raise HTTPException(400, "Replacement is already in the lineup")

    removed = lineups_repo.fetch_player(db, body.player_out_id)
    incoming = lineups_repo.fetch_player(db, body.player_in_id)
    if not removed or not incoming:
        raise HTTPException(404, "Player not found")
    if removed["team_abbr"].upper() != body.team_abbr.upper() or incoming["team_abbr"].upper() != body.team_abbr.upper():
        raise HTTPException(400, "Players must belong to the selected team")

    if not lineups_repo.fetch_team(db, body.team_abbr):
        raise HTTPException(404, "Team not found")

    cur_off = float(lu["offensive_rating"])
    cur_def = float(lu["defensive_rating"])

    return simulate_substitution(
        team_abbr=body.team_abbr.upper(),
        lineup_id=body.lineup_id,
        cur_off=cur_off,
        cur_def=cur_def,
        removed=removed,
        incoming=incoming,
    )
