"""Database helpers: paths work for local dev and deployment."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "data" / "nba_lineups.db"


def get_db_path() -> Path:
    return Path(os.environ.get("NBA_DB_PATH", DEFAULT_DB_PATH))


def ensure_data_dir() -> None:
    get_db_path().parent.mkdir(parents=True, exist_ok=True)


def get_engine() -> Engine:
    ensure_data_dir()
    path = get_db_path()
    return create_engine(f"sqlite:///{path}", echo=False, future=True)


def init_schema(engine: Engine | None = None) -> None:
    eng = engine or get_engine()
    schema_file = Path(__file__).parent / "schema.sql"
    sql = schema_file.read_text()
    with eng.raw_connection() as raw:
        raw.executescript(sql)
    _ensure_players_pct_columns(eng)


def _ensure_players_pct_columns(engine: Engine) -> None:
    """Idempotent ALTER for existing SQLite DBs created before stl_pct/blk_pct existed."""
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(players)")).fetchall()
        cols = {r[1] for r in rows}
        if "stl_pct" not in cols:
            conn.execute(text("ALTER TABLE players ADD COLUMN stl_pct REAL"))
        if "blk_pct" not in cols:
            conn.execute(text("ALTER TABLE players ADD COLUMN blk_pct REAL"))


def clear_tables(engine: Engine | None = None) -> None:
    eng = engine or get_engine()
    with eng.begin() as conn:
        conn.execute(text("DELETE FROM lineups"))
        conn.execute(text("DELETE FROM players"))
        conn.execute(text("DELETE FROM teams"))
        conn.execute(text("DELETE FROM ingestion_meta"))
