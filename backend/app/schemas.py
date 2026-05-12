from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SeasonScopeOut(BaseModel):
    """Proves pipeline targets 2025-26 NBA regular season only (no playoffs / play-in)."""

    season: str
    season_type: str
    data_source: str
    roster_mode: Optional[str] = None  # e.g. nba_stats_teams vs scrambled_active (synthetic seed)
    nba_stats_contract: str = (
        "All LeagueDash* requests use Season=2025-26 and SeasonType=Regular Season."
    )


class TeamOut(BaseModel):
    team_abbr: str
    team_name: str
    offensive_rating: Optional[float] = None
    defensive_rating: Optional[float] = None
    net_rating: Optional[float] = None
    pace: Optional[float] = None


class PlayerOut(BaseModel):
    player_id: int
    player_name: str
    team_abbr: str
    position: Optional[str] = None
    games_played: Optional[int] = None
    minutes_played: Optional[float] = None
    points_per_game: Optional[float] = None
    rebounds_per_game: Optional[float] = None
    assists_per_game: Optional[float] = None
    ts_pct: Optional[float] = None
    efg_pct: Optional[float] = None
    bpm: Optional[float] = None
    obpm: Optional[float] = None
    dbpm: Optional[float] = None
    offensive_rating: Optional[float] = None
    defensive_rating: Optional[float] = None
    usage_rate: Optional[float] = None
    ast_pct: Optional[float] = None
    tov_pct: Optional[float] = None
    fg3_pct: Optional[float] = None
    stl: Optional[float] = None
    blk: Optional[float] = None
    stl_pct: Optional[float] = None
    blk_pct: Optional[float] = None


class LineupOut(BaseModel):
    lineup_id: str
    team_abbr: str
    player_1_id: Optional[int] = None
    player_1_name: Optional[str] = None
    player_2_id: Optional[int] = None
    player_2_name: Optional[str] = None
    player_3_id: Optional[int] = None
    player_3_name: Optional[str] = None
    player_4_id: Optional[int] = None
    player_4_name: Optional[str] = None
    player_5_id: Optional[int] = None
    player_5_name: Optional[str] = None
    minutes: float
    possessions: Optional[float] = None
    offensive_rating: Optional[float] = None
    defensive_rating: Optional[float] = None
    net_rating: Optional[float] = None
    pace: Optional[float] = None
    ast_pct: Optional[float] = None
    reb_pct: Optional[float] = None
    tov_pct: Optional[float] = None
    efg_pct: Optional[float] = None
    spacing_score: Optional[float] = None
    playmaking_score: Optional[float] = None
    defensive_activity_score: Optional[float] = None
    rebounding_score: Optional[float] = None
    underrated_lineup_score: Optional[float] = None


SortMetric = Literal[
    "net_rating",
    "offensive_rating",
    "defensive_rating",
    "minutes",
    "possessions",
    "underrated_lineup_score",
]


class SimulateSubstitutionIn(BaseModel):
    team_abbr: str = Field(..., min_length=2, max_length=4)
    lineup_id: str
    player_out_id: int = Field(..., gt=0)
    player_in_id: int = Field(..., gt=0)


class SimulateSubstitutionOut(BaseModel):
    team_abbr: str
    lineup_id: str
    baseline_offensive_rating: float
    baseline_defensive_rating: float
    baseline_net_rating: float
    projected_offensive_rating: float
    projected_defensive_rating: float
    projected_net_rating: float
    delta_offensive_rating: float
    delta_defensive_rating: float
    delta_net_rating: float
    summary: str
    removed_player: PlayerOut
    incoming_player: PlayerOut
