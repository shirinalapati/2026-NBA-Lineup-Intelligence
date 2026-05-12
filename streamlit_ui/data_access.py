"""DB session + scope metadata (mirrors API /scope)."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database import get_session_factory


@contextmanager
def db_session() -> Any:
    sf = get_session_factory()
    db = sf()
    try:
        yield db
    finally:
        db.close()


def fetch_scope(db: Session) -> dict[str, Any]:
    rows = db.execute(text("SELECT key, value FROM ingestion_meta")).mappings().all()
    meta = {r["key"]: r["value"] for r in rows}
    from data_pipeline.config import SEASON, SEASON_TYPE

    return {
        "season": str(meta.get("season", SEASON)),
        "season_type": str(meta.get("season_type", SEASON_TYPE)),
        "data_source": str(meta.get("source", "unknown")),
        "roster_mode": meta.get("roster_mode"),
    }


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
