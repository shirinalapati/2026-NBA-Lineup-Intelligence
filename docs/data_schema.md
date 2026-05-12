# Data schema — SQLite (PostgreSQL-compatible)

Database file default: `data/nba_lineups.db` (`NBA_DB_PATH` overrides).

## `teams`

| Column | Type | Description |
|--------|------|-------------|
| team_abbr | TEXT PK | e.g. `BOS` |
| team_name | TEXT | Full franchise name |
| offensive_rating | REAL | Team ORtg (advanced, per 100) |
| defensive_rating | REAL | Team DRtg |
| net_rating | REAL | ORtg − DRtg |
| pace | REAL | Tempo: **possessions per 48 minutes** for that team (NBA.com advanced; not the same scale as per-100 ORtg/DRtg). |

## `players`

| Column | Type | Description |
|--------|------|-------------|
| player_id | INTEGER PK | NBA player id (or synthetic id in seed) |
| player_name | TEXT | |
| team_abbr | TEXT FK → teams.team_abbr | |
| position | TEXT | May be coarse if API omits detail |
| games_played | INTEGER | |
| minutes_played | REAL | Total minutes |
| points_per_game | REAL | Per-game points |
| rebounds_per_game | REAL | |
| assists_per_game | REAL | |
| ts_pct, efg_pct | REAL | Shooting |
| bpm, obpm, dbpm | REAL | Impact proxies (BPM or derived) |
| offensive_rating, defensive_rating | REAL | Player advanced ratings from API |
| usage_rate | REAL | |
| ast_pct, tov_pct, fg3_pct | REAL | |
| stl, blk | REAL | Per-game steals/blocks |
| stl_pct, blk_pct | REAL | Steal/block **percentage** as a decimal rate (e.g. `0.025` for 2.5%) |
| oreb_pct, dreb_pct | REAL | |
| salary | REAL NULL | Not provided by public stats API |
| season | TEXT | `2025-26` |

## `lineups`

| Column | Type | Description |
|--------|------|-------------|
| lineup_id | TEXT PK | Hash of team + sorted player ids (or name fallback) |
| team_abbr | TEXT FK | |
| player_1_id … player_5_id | INTEGER | |
| player_1_name … player_5_name | TEXT | Display names from API |
| minutes | REAL | Lineup minutes together |
| possessions | REAL | Estimated or from API |
| offensive_rating, defensive_rating, net_rating | REAL | Lineup advanced |
| pace | REAL | Tempo for that five-man unit: **possessions per 48 minutes** as returned by NBA.com (see About → Pace & tempo). |
| ast_pct, reb_pct, tov_pct, efg_pct | REAL | Lineup four-factors style fields when available |
| spacing_score, playmaking_score, defensive_activity_score, rebounding_score | REAL | Derived 0–100 traits |
| underrated_lineup_score | REAL | ULS |
| season | TEXT | `2025-26` |

## `ingestion_meta`

Key/value flags (e.g. `source` = `nba_stats_api` or `synthetic_seed_2025_26`).

## PostgreSQL migration

- Replace `sqlite` connection strings with `postgresql+psycopg2://...`.
- SQLite `ON CONFLICT` syntax matches PostgreSQL for these upserts.
- Remove SQLite-specific `executescript` usage in favor of Alembic migrations in production if desired.
