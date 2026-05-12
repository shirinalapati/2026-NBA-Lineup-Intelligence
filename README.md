# 2025-26 NBA Lineup Intelligence

A portfolio-grade full-stack analytics product for evaluating **five-man lineups** across the completed **2025-26 NBA regular season**: leaderboards, an **Underrated Lineup Score (ULS)**, team exploration views, and a **substitution simulator** with a transparent heuristic projection model.

## Features

- **Lineup leaderboard** — Filter by minimum minutes, team, search, sort (net / ORtg / DRtg / minutes / possessions), CSV export, URL-synced filters.
- **Team explorer** — Best net, most-used minutes, most underrated (ULS), ORtg–DRtg scatter for team lineups vs team baselines.
- **Underrated lineups** — ULS ranking with team filter; minutes floor is **≥ 50** (same threshold as ULS computation).
- **Substitution simulator** — Swap one roster player into an existing lineup; view projected ORtg/DRtg/net with deltas and an auto summary.
- **About (home `/`)** — Full story plus technical spec: problem framing, philosophy, **explicit ULS & substitution formulas**, minute floors, data scope, limitations, and roadmap. Canonical in-app doc; mirror in `docs/methodology.md`.
- **Overview (`/overview`)** — Dashboard with featured charts and lineup samples.

## Stack

| Layer | Technology |
|-------|------------|
| UI | React 19, TypeScript, Vite, Tailwind CSS, Recharts, React Router |
| API | FastAPI, Pydantic, SQLAlchemy |
| Data | Python 3.11+, `pandas`, `nba_api`, SQLite (schema portable to PostgreSQL) |

## Quick start (local)

**1. Python environment**

```bash
cd Basketball_Analytics
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Database**

Populate SQLite from **NBA Stats** (2025-26 regular season). Requires network access to `stats.nba.com` / the `nba_api` endpoints:

```bash
python -m data_pipeline.ingest_all
```

This **replaces** any existing rows in `teams` / `players` / `lineups` so the database is not a mix of old demo and live data. Output: `data/nba_lineups.db` (override with `NBA_DB_PATH`).

To refresh only lineup trait columns and **ULS** after changing `ULS_MIN_MINUTES` in `data_pipeline/config.py` (no NBA API calls):

```bash
python -m data_pipeline.recompute_uls
```

Offline UI demo only (synthetic lineups, not real league minutes):

```bash
python -m data_pipeline.ingest_all --seed
```

**3. API**

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

**4. Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — you land on **About** (introduction + methodology); use **Overview** for charts and featured lineups. The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

**Season contract:** All live NBA Stats pulls use **`Season=2025-26`** and **`SeasonType=Regular Season`** only. Confirm anytime with `GET /api/scope` (returns `season`, `season_type`, `data_source` from `ingestion_meta`).

**Production build**

```bash
cd frontend && npm run build
```

Serve `frontend/dist` behind any static host; set `VITE_API_BASE` to your API origin if the API is on another domain.

### Frontend on Vercel

Vercel hosts the **static UI only** (FastAPI + SQLite still need another host—e.g. Railway or Render—see below).

1. In [Vercel](https://vercel.com), **Import** the GitHub repo.
2. Set **Root Directory** to `frontend` (monorepo).
3. Framework preset **Vite**; build `npm run build`; output `dist` (auto-detected). `frontend/vercel.json` SPA rewrites deep links to `index.html`.
4. **API URL (baked at build):** In Vercel **Environment Variables**, set **either** **`API_UPSTREAM`** or **`VITE_API_BASE`** to your Render API origin (e.g. `https://two026-nba-lineup-intelligence.onrender.com`), **no trailing slash**. Enable for **Production** (and **Preview** if needed). **Redeploy** after every change—`vite build` reads `process.env` and inlines the value into the JS bundle.
5. **CORS on Render:** Set **`CORS_ORIGINS`** to your Vercel UI URL (e.g. `https://2026-nba-lineup-intelligence.vercel.app`), **or** set **`CORS_ALLOW_VERCEL=1`** on the API to allow any `*.vercel.app` origin (portfolio convenience).
6. Include `http://localhost:5173` in **`CORS_ORIGINS`** only if you call the production API from local dev.

## Data sourcing & processing

- **Live path**: `python -m data_pipeline.ingest_all` runs `ingest_teams.py`, `ingest_players.py`, and `ingest_lineups.py` via `nba_api` for **Regular Season** only (`SeasonType`: Regular Season). This is the default; failures surface as errors (no automatic demo fallback).
- **Optional demo**: `python -m data_pipeline.ingest_all --seed` loads `seed_data.py` (synthetic teams/lineups). Use only when the API is unavailable; do not treat output as real NBA statistics.
- **Analytics**: `data_pipeline/scoring.py` implements winsorization + normalization for lineup “fit” traits, and **ULS** (pure min–max on lineups with minutes ≥ 50; formulas on the **About** home page and in `docs/methodology.md`).
- **Schema**: `data_pipeline/schema.sql` — see `docs/data_schema.md`.

## Tests

```bash
pytest
```

## Case study (white paper)

For a narrative interpretation guide—lineup vs player inference, ULS as a relative composite, simulator limits, and a suggested demo script—see [`docs/white-paper.md`](docs/white-paper.md).

## Screenshots

_Add screenshots of Home, Leaderboard, Team Explorer, Underrated, and Simulator here for README/portfolio use._

## Deploying with real NBA data (production path)

For a public deploy, treat **live NBA Stats ingestion** as part of your release—not optional demo seed.

1. **Build the database once** (needs outbound HTTPS to `stats.nba.com`; same Python env as the app):

   ```bash
   python -m data_pipeline.ingest_all
   ```

   Do **not** use `--seed` in production. That path is for offline UI demos only.

2. **Persist `data/nba_lineups.db`** (or set **`NBA_DB_PATH`** to a file on durable storage). Serverless hosts that wipe disk on each deploy must re-run ingestion in a **release phase** or attach a **volume**.

3. **Run the API** with `uvicorn backend.app.main:app` (or your host’s equivalent). Point **`CORS_ORIGINS`** at your real frontend origin(s), comma-separated (no trailing slash issues—match what the browser sends).

4. **Build the frontend** with **`VITE_API_BASE`** set to the public API base URL if the UI is not served from the same origin (e.g. `https://api.yourdomain.com` with no trailing slash).

5. **Verify after deploy:** open **`GET /api/scope`** on the API. **`data_source`** / `ingestion_meta` **`source`** should reflect **`nba_stats_api`**, not synthetic seed.

**Caveats for real data**

- `LeagueDashLineups` returns a **capped number of rows** (on the order of thousands), so the DB may not include every theoretical five-man unit league-wide—only what the NBA Stats endpoint returns for the configured season/type.
- Respect **NBA / STATS.COM terms of use** for your use case (portfolio vs commercial).

## Deployment notes

- **Backend**: Any ASGI host (e.g. Railway, Render, Fly) running `uvicorn backend.app.main:app`. Set `CORS_ORIGINS` to your frontend origin(s).
- **Database**: Point `NBA_DB_PATH` at a persistent volume. For PostgreSQL, swap the SQLAlchemy URL in `backend/app/database.py` and `data_pipeline/db.py` (schema is ANSI SQL with minor SQLite-specific PRAGMA).
- **Frontend**: Static hosting (Vercel, Netlify, S3+CloudFront) with `VITE_API_BASE` if API is cross-origin.

## License

Educational / portfolio use. Not affiliated with the NBA. Synthetic seed data must not be presented as real league statistics.
