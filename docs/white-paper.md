# White Paper — Case Study: 2025-26 NBA Lineup Intelligence

**Subtitle:** Interpreting five-man unit efficiency, composite “underrated” scoring, and substitution heuristics in a transparent analytics stack.

**Document type:** Technical case study / interpretation guide for the repository at the same path level as `docs/methodology.md`.

**Scope note:** Statistics cited in NBA.com feeds are authoritative for *observed* ORtg, DRtg, net, and minutes. This paper explains **how this product structures and extends** those inputs—not new league truth tables.

---

## Abstract

Modern NBA analysis increasingly operates at the **lineup** level: coaches deploy five-man groups, and public advanced feeds report efficiency for those units. Yet lineup tables are easy to misread. Small samples, confounded teammates, and **sorting by net rating** invite the false conclusion that “Player A’s lineup is worse than Player B’s lineup” means “Player A is worse than Player B.”

This project implements a **read-only analytics layer** on top of 2025-26 **regular-season** NBA Stats data: leaderboards, team exploration, an **Underrated Lineup Score (ULS)**, and a **substitution simulator** with published coefficients. This white paper frames the work as a **case study**: what an analyst should expect to see, how to interpret apparent paradoxes, and where the stack intentionally stops short of causal player impact.

---

## 1. Introduction

### 1.1 Motivation

Five-man lineup rows answer a narrow question well: *When these five players shared the floor, how did the team perform on a per-possession basis?* They do **not** automatically answer: *How much did each player cause that performance?*

Portfolio and teaching-oriented tools often collapse that distinction. Users bounce when the UI “looks wrong”—for example, a reserve-heavy unit out-netting a star-heavy unit on the same team. The product’s **About** page, **methodology** mirror, and in-app disclaimers exist to prevent that misread. This document extends that story into a single narrative suitable for stakeholders, reviewers, or hiring managers who want the “so what” in one place.

### 1.2 What this repository ships

| Layer | Role |
|-------|------|
| **Data pipeline** (`data_pipeline/`) | Ingest teams, players, and `LeagueDashLineups` / player advanced rows; enrich trait columns; compute ULS; persist SQLite. |
| **API** (`backend/`) | FastAPI read models, substitution projection (`simulation.py`), `GET /api/scope` for season contract verification. |
| **Frontend** (`frontend/`) | React + Vite UI: leaderboard, team explorer, underrated view, simulator, charts, CSV export. |

Canonical formulas and minute-floor rules live in-app at route **`/`** and in `docs/methodology.md`. **If code and prose diverge, treat code as source of truth** until docs are reconciled.

---

## 2. Problem framing (the case for lineup discipline)

### 2.1 The attribution gap

Lineup net rating aggregates **outcomes** for a joint treatment: five players, opponents, scheme, game state, and luck. **On-off** and **RAPM-style** models exist precisely because raw lineup splits confound those factors. This product does **not** ship a shrinkage estimator or matchup-adjusted RAPM; it surfaces **NBA-reported lineup efficiency** and adds **transparent composites** (ULS, traits) and a **swap heuristic** (simulator).

**Finding (interpretive):** Any UI that sorts lineups by net without a paragraph of context will produce “counterintuitive” rows. That is less often a data bug than a **category error** (unit vs player).

### 2.2 Sample size and selection

Even with a **minimum minutes floor** (leaderboards default to **50** minutes aligned with ULS eligibility; the simulator uses a lower floor so teams still have menu options), residual variance remains. Heavier-minute lineups are also **selected** by coaching staff for roles the table does not label.

**Finding:** Raising the minutes floor trades **coverage** for **stability**. Lowering it surfaces more units but increases the chance that a few possessions drive rank order.

### 2.3 Coverage limits of public lineup feeds

`LeagueDashLineups` returns a **large but capped** set of rows for a season. The database may omit some theoretical five-tuples that never met reporting thresholds or never appeared in the feed slice the client retrieved. **Finding:** League-wide completeness is not guaranteed; conclusions should be phrased as “among lineups present in this snapshot.”

---

## 3. Data and season contract

- **Season:** `2025-26` (`data_pipeline/config.py`, `SEASON`).
- **Games:** **Regular season only** (`SEASON_TYPE = "Regular Season"`). Playoffs, play-in, preseason, and All-Star are excluded by design.
- **Synthetic path:** `ingest_all --seed` is for **offline UI demos only**; it must not be presented as NBA reality.

After deploy or ingest, **`GET /api/scope`** should report metadata consistent with live pulls (`nba_stats_api`), not seed, for any public “real data” narrative.

---

## 4. Methodological pillars

### 4.1 Observed efficiency (ORtg, DRtg, net)

Ingested lineup and team ratings are interpreted as **per-100-possession** style advanced numbers from the feed, with **net = ORtg − DRtg** on the same basis. **Pace** is a tempo concept (possessions per 48 in the league’s convention); it is **not** interchangeable with per-100 efficiency numerically.

**Case-study takeaway:** When comparing two lineups, always read **minutes and possessions** next to net. A +12 net on 40 minutes is not commensurate with a +6 net on 400 minutes without additional modeling.

### 4.2 Underrated Lineup Score (ULS)

ULS is an **app-defined composite**, not an NBA stat. Only lineups with **minutes ≥ `ULS_MIN_MINUTES` (50)** participate. Components are **pure min–max to 0–100 on the eligible set** for that enrichment run; defensive rating enters after **sign inversion** so lower allowed efficiency maps to higher contribution. Weights (see `config.py`) are:

| Ingredient | Weight |
|------------|--------|
| Net rating (normalized) | 0.35 |
| Offensive rating | 0.20 |
| Inverted defensive rating | 0.20 |
| Limited usage bonus (LUB) | 0.15 |
| Possessions | 0.10 |

LUB rewards **less-used** lineups within the eligible minute band after its own normalization pipeline (see `docs/methodology.md` for the exact two-step construction).

**Findings:**

1. **ULS is inherently relative.** A score of “78” means “high within this database’s eligible lineups,” not “78% chance of winning a title.”
2. **Changing `ULS_MIN_MINUTES` or re-ingesting changes norms.** Stored ULS must be recomputed (`python -m data_pipeline.recompute_uls`) after threshold changes or stale enrichment; otherwise the UI can show “—” even when the slider suggests scores should exist.
3. **LUB injects a deliberate “low minutes together” preference** among already-qualified units. High-net, ultra-heavy minute groups may rank below slightly lower-net but rarer units—by construction.

### 4.3 Lineup “fit” traits

Spacing, playmaking, defensive activity, and rebounding traits are **descriptive blends** of roster player inputs with winsorization and min–max scaling for display. They **do not** replace efficiency for causal claims.

**Finding:** Trait columns help tell a *shape* story (shooting vs turnover vs activity) orthogonal to a single net sort. They should be read as complementary, not authoritative.

### 4.4 Substitution simulator

The simulator starts from the **selected lineup’s** observed offensive and defensive ratings, then applies **fixed linear deltas** from player-in vs player-out differences on OBPM, DBPM, TS%, AST%, TOV%, STL%, and BLK% (coefficients in `config.py`, e.g. `SIM_OFF_OBPM`, `SIM_DEF_DBPM`, …). **Projected net** is `ProjOff − ProjDef` from those heuristics.

**Findings:**

1. The tool is **transparently not calibrated** as a forecasting model; it is a **decision-support sketch** for “what if we swapped one roster piece in this exact five?”
2. Large role mismatches (e.g. replacing a high-usage creator with a specialist) stretch the linearity assumption; the UI states this through prototype / limitation copy.
3. **Roster table lag vs lineup rows** (trades, two-way minutes) can cause temporary name/ID mismatches; the UI falls back to lineup-embedded names where possible so the experience stays legible.

---

## 5. Synthesis: how to present “results” responsibly

When writing a portfolio blurb, README screenshot caption, or interview walkthrough, the following **claims are well supported** by this codebase:

- “We ingest regular-season lineup and player advanced stats and expose them through a typed API and React UI.”
- “We define a documented ULS composite with explicit weights and eligibility rules.”
- “We expose a substitution heuristic with coefficients visible in config and methodology.”

The following **claims require extra work not in this repo**:

- “This ranking proves which players drive winning.”
- “This simulator predicts post-trade performance within X points.”
- “This database contains every NBA five-man unit for the season.”

**Recommended demo script (case-study style):**

1. Open **Team explorer** → show **best net** vs **most minutes** vs **ULS** slices disagreeing by design.  
2. Open **Leaderboard** → change minutes floor and note rank churn.  
3. Open **Simulator** → pick a high-minute lineup, swap one player, show deltas while quoting the disclaimer that **lineup net is a unit stat**.  
4. Hit **`/api/scope`** → restate season and source contract.

---

## 6. Limitations (non-exhaustive)

- **No matchup, injury, or travel adjustment** on observed lineup efficiency.
- **No play-by-play event model** (pick-and-roll coverage, switch rules, etc.).
- **No licensing substitute** for NBA / STATS.COM terms of use; commercial use needs independent legal review.
- **Single-season snapshot** framing: the product is not a live trading engine.

---

## 7. Conclusion

This project is **deployment-ready as a portfolio-grade system** when the database is built from live ingest (or a deliberately labeled demo), CORS and API base URLs are set for the target hosts, and presenters adopt the **lineup-unit discipline** described here. The main “finding” of the case study is methodological: **transparency and correct object of inference** matter as much as the formulas. The formulas themselves are versioned in code and mirrored in `docs/methodology.md` for auditability.

---

## Appendix A — Reproduction commands

```bash
# Real data (requires network to NBA Stats)
python -m data_pipeline.ingest_all

# Refresh traits + ULS only (e.g. after changing ULS_MIN_MINUTES)
python -m data_pipeline.recompute_uls

# API
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Frontend production build
cd frontend && npm run build
```

Environment variables referenced in README: `NBA_DB_PATH`, `CORS_ORIGINS`, `VITE_API_BASE`.

---

## Appendix B — Document control

| Artifact | Purpose |
|----------|---------|
| `docs/methodology.md` | Spec mirror; formula reference. |
| `docs/white-paper.md` | This file; narrative + interpretation + case-study framing. |
| `frontend/src/pages/AboutProject.tsx` | In-app canonical copy and anchors. |

**Version:** Written to match the repository’s 2025-26 regular-season product scope as encoded in `data_pipeline/config.py` at the time of authorship.
