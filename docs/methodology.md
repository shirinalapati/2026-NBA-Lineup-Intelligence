# Methodology — 2025-26 NBA Lineup Intelligence

**In-app:** The full narrative plus the same formulas below live at the app root **`/`** (“About” in the nav). This file stays in the repo as a reviewable mirror; if it ever disagrees with the About page or code, **trust the code** until docs are aligned. For a longer **case-study / white-paper** framing (how to interpret findings, demo script, supported vs unsupported claims), see **`docs/white-paper.md`**.

## Scope

- **Season**: 2025-26 NBA **regular season** only. The codebase enforces this in `data_pipeline/config.py` (`SEASON`, `SEASON_TYPE`) and every `nba_api` LeagueDash* call passes `SeasonType=Regular Season`. **Playoffs, play-in, preseason, and All-Star** games are **not** included.
- **Verification**: After ingest, `ingestion_meta` stores `season`, `season_type`, and `source`. The API exposes `GET /api/scope` so the UI can display the same contract.
- **Static snapshot**: The completed regular season is treated as final; the database is a snapshot for analysis and UI demos.

## Data sources

1. **Primary**: NBA.com statistics via the [`nba_api`](https://github.com/swar/nba_api) Python client (`LeagueDashLineups`, `LeagueDashPlayerStats`, `LeagueDashTeamStats`). Load with `python -m data_pipeline.ingest_all` (no `--seed`).
2. **Optional offline demo**: `python -m data_pipeline.ingest_all --seed` uses deterministic **synthetic** team/lineup stats in `data_pipeline/seed_data.py` (random five-man combinations from rosters—not observed NBA lineups). Use only when the API is unreachable; do not present as real league data.

## Qualified lineups

Leaderboards default to a **minimum minutes** threshold (the app uses **50** minutes, aligned with ULS eligibility) to limit extreme small-sample efficiency noise while still surfacing most teams’ scored lineups. Analysts can change the threshold in the UI with the understanding that variance and measurement error increase at very low minutes.

Lineups missing core rating fields are dropped during ingestion.

## Winsorization & normalization

**Lineup fit traits** (spacing, playmaking, etc.): continuous inputs are **winsorized** at the 2nd and 98th percentiles, then min–max scaled to 0–100 (`data_pipeline/config.py`).

**Underrated Lineup Score (ULS)** uses **pure min–max** normalization to 0–100 on the eligible lineup set only (no winsorization for ULS). Defensive rating is **negated** before min–max so lower DRtg maps to higher normalized values. If min equals max on any component, that normalized column is set to **50** for all rows (no divide-by-zero).

## Underrated Lineup Score (ULS)

Only lineups with **minutes ≥ 50** receive a ULS. All components are min–max normalized to 0–100 **within that eligible set**:

```
ULS = 0.35 * norm(net_rating)
    + 0.20 * norm(offensive_rating)
    + 0.20 * norm(inverted_defensive_rating)
    + 0.15 * norm(limited_usage_bonus)
    + 0.10 * norm(possessions)
```

- **inverted_defensive_rating**: `norm(-defensive_rating)` after min–max (lower DRtg is better).
- **limited_usage_bonus (LUB)**: After restricting to minutes ≥ 50,  
  `LUB = 1 - (Minutes - min(Minutes)) / (max(Minutes) - min(Minutes))`,  
  then **LUB** is min–max normalized again to 0–100 across the same eligible set. If all eligible lineups have the same minutes, LUB is 1.0 for everyone before the second normalization (then norms collapse to 50 if that column is constant).

## Pace and rating units

- **ORtg / DRtg / Net (teams & lineups):** From NBA.com advanced feeds using **per-100-possession** scaling in this product’s ingestion—points scored or allowed **per 100 possessions** for that row. **Net** = ORtg − DRtg on the same scale.
- **Pace (teams & lineups):** The league’s **tempo** statistic as returned on that row—conventionally interpreted as **possessions per 48 minutes** (regulation-length basis). Higher = faster estimated play. Pace is **not** the same unit as per-100 ORtg/DRtg; do not compare the numeric magnitudes as if they were identical scales.
- **Possessions (lineup rows):** Stored from the API when present; otherwise approximated in the pipeline for derived fields (e.g. ULS). Always read **minutes** alongside possessions on small samples.

## Lineup fit traits

Descriptive traits (spacing, playmaking, defensive activity, rebounding) are derived from aggregating constituent player shooting, playmaking, steal/block and DBPM (Defensive Box Plus/Minus) proxies, and rebound signals. They are normalized league-wide for display and copy; they do not replace efficiency metrics for ranking.

## League stats vs app-only outputs

- **Lineup / team tables:** `OFF_RATING`, `DEF_RATING`, `NET_RATING`, `PACE`, etc. are ingested from NBA.com for live data—not recomputed by this product for display.
- **ULS:** A composite score defined in this repo (`data_pipeline/scoring.py`); not an NBA-published stat.
- **Substitution simulator:** `ProjOff`, `ProjDef`, and `ProjNet` are heuristic outputs from `backend/app/services/simulation.py` only. `ProjNet` is **not** the same as the stored `NET_RATING` column in lineup rows.

## Substitution simulator

Transparent heuristic: start from the lineup’s current **offensive** and **defensive** ratings, then adjust by player-in vs player-out deltas on **OBPM** (Offensive Box Plus/Minus), **DBPM** (Defensive Box Plus/Minus), **TS%** (True Shooting Percentage), **AST%** (Assist Percentage), **TOV%** (Turnover Percentage), **STL%** (Steal Percentage), and **BLK%** (Block Percentage). The percentage metrics are stored and used as **decimals** (e.g. `0.58`).

Coefficients are in `data_pipeline/config.py` (`SIM_OFF_*`, `SIM_DEF_*`).

```
ProjOff = CurrentOff
        + SIM_OFF_OBPM * (OBPM_in - OBPM_out)
        + SIM_OFF_TS * (TS_in - TS_out)
        + SIM_OFF_AST_PCT * (ASTpct_in - ASTpct_out)
        - SIM_OFF_TOV_PCT * (TOVpct_in - TOVpct_out)

ProjDef = CurrentDef
        - SIM_DEF_DBPM * (DBPM_in - DBPM_out)
        - SIM_DEF_STL_PCT * (STLpct_in - STLpct_out)
        - SIM_DEF_BLK_PCT * (BLKpct_in - BLKpct_out)

ProjNet = ProjOff - ProjDef
```

Output includes projected ORtg, DRtg, net, deltas vs baseline, and a short narrative summary of drivers.

### Limitations

- Public lineup data omits matchup, coaching, injury, and schematic context.
- Player-on/off impact is proxied, not measured with proprietary tracking.
- Do not use synthetic seed outputs for real scouting conclusions.
