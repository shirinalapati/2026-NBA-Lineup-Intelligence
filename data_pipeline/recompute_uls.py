"""
Recompute lineup trait columns and ULS only (no NBA API calls).

Use after changing ``ULS_MIN_MINUTES`` in ``data_pipeline/config.py`` or if the DB
still has NULL ``underrated_lineup_score`` from an older enrichment run.

  python -m data_pipeline.recompute_uls
"""

from __future__ import annotations

import logging

from data_pipeline.db import get_engine
from data_pipeline.ingest_lineups import enrich_traits_and_uls

logger = logging.getLogger(__name__)


def main() -> None:
    eng = get_engine()
    enrich_traits_and_uls(eng)
    logger.info("Recomputed traits + ULS for all lineups in the current database.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
