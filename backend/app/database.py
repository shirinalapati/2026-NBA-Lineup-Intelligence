"""DB session factory — shared path with data_pipeline."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow `python -m uvicorn backend.app.main:app` from repo root
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        db_path = os.environ.get("NBA_DB_PATH", str(ROOT / "data" / "nba_lineups.db"))
        _engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
    return _SessionLocal


def get_db() -> Session:
    sf = get_session_factory()
    db = sf()
    try:
        yield db
    finally:
        db.close()
