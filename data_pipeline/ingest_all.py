"""
Run full ingestion: NBA Stats API → SQLite.

Synthetic seed is **opt-in only** (`--seed`) for offline/demo when the API is unavailable.
"""

from __future__ import annotations

import argparse
import logging
import traceback

from data_pipeline.config import validate_season_scope
from data_pipeline.db import clear_tables, get_engine, init_schema
from data_pipeline.ingestion_meta import write_scope_meta
from data_pipeline import seed_data

logger = logging.getLogger(__name__)


def run(*, use_seed: bool = False) -> str:
    """
    Returns a short source label: ``"api"`` or ``"seed"``.

    Default: fetch teams, players, and 5-man lineups from NBA Stats (2025-26 regular season).
    Clears existing rows first so the DB does not mix prior synthetic data with API data.

    Raises on API failure (no silent fallback to demo data).
    """
    validate_season_scope()
    eng = get_engine()
    init_schema(eng)
    if use_seed:
        seed_data.run()
        return "seed"

    from data_pipeline import ingest_teams, ingest_players, ingest_lineups

    clear_tables(eng)
    try:
        ingest_teams.run(eng)
        ingest_players.run(eng)
        ingest_lineups.run(eng)
        with eng.begin() as conn:
            write_scope_meta(conn, "nba_stats_api")
        return "api"
    except Exception:
        logger.error(
            "Live NBA Stats ingestion failed. Fix network/API access or use "
            "`python -m data_pipeline.ingest_all --seed` for offline demo data only.\n%s",
            traceback.format_exc(),
        )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load 2025-26 regular-season NBA Stats into SQLite (live API by default)."
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Load deterministic synthetic data instead of NBA Stats (offline UI demo only).",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    src = run(use_seed=args.seed)
    logger.info("Done: %s", src)
