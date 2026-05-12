-- 2025-26 NBA Lineup Intelligence — SQLite schema (PostgreSQL-compatible types noted in docs)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    team_abbr TEXT PRIMARY KEY,
    team_name TEXT NOT NULL,
    offensive_rating REAL,
    defensive_rating REAL,
    net_rating REAL,
    pace REAL
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL,
    team_abbr TEXT NOT NULL,
    position TEXT,
    games_played INTEGER,
    minutes_played REAL,
    points_per_game REAL,
    rebounds_per_game REAL,
    assists_per_game REAL,
    ts_pct REAL,
    efg_pct REAL,
    bpm REAL,
    obpm REAL,
    dbpm REAL,
    offensive_rating REAL,
    defensive_rating REAL,
    usage_rate REAL,
    ast_pct REAL,
    tov_pct REAL,
    fg3_pct REAL,
    stl REAL,
    blk REAL,
    stl_pct REAL,
    blk_pct REAL,
    oreb_pct REAL,
    dreb_pct REAL,
    salary REAL,
    season TEXT NOT NULL DEFAULT '2025-26',
    FOREIGN KEY (team_abbr) REFERENCES teams(team_abbr)
);

CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_abbr);

CREATE TABLE IF NOT EXISTS lineups (
    lineup_id TEXT PRIMARY KEY,
    team_abbr TEXT NOT NULL,
    player_1_id INTEGER,
    player_1_name TEXT,
    player_2_id INTEGER,
    player_2_name TEXT,
    player_3_id INTEGER,
    player_3_name TEXT,
    player_4_id INTEGER,
    player_4_name TEXT,
    player_5_id INTEGER,
    player_5_name TEXT,
    minutes REAL NOT NULL,
    possessions REAL,
    offensive_rating REAL,
    defensive_rating REAL,
    net_rating REAL,
    pace REAL,
    ast_pct REAL,
    reb_pct REAL,
    tov_pct REAL,
    efg_pct REAL,
    spacing_score REAL,
    playmaking_score REAL,
    defensive_activity_score REAL,
    rebounding_score REAL,
    underrated_lineup_score REAL,
    season TEXT NOT NULL DEFAULT '2025-26',
    FOREIGN KEY (team_abbr) REFERENCES teams(team_abbr)
);

CREATE INDEX IF NOT EXISTS idx_lineups_team ON lineups(team_abbr);
CREATE INDEX IF NOT EXISTS idx_lineups_minutes ON lineups(minutes);
CREATE INDEX IF NOT EXISTS idx_lineups_net ON lineups(net_rating);

-- Idempotent ingestion: store raw API hash per season
CREATE TABLE IF NOT EXISTS ingestion_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
