"""Persist season scope in SQLite for API verification (2025-26 regular season only)."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection

from data_pipeline.config import SEASON, SEASON_TYPE


def write_scope_meta(
    conn: Connection,
    source: str,
    extras: dict[str, str] | None = None,
) -> None:
    """Store source label plus season + season_type so the app can prove NBA requests were RS-only."""
    rows: list[tuple[str, str]] = [
        ("source", source),
        ("season", SEASON),
        ("season_type", SEASON_TYPE),
    ]
    if extras:
        rows.extend(extras.items())
    for k, v in rows:
        conn.execute(
            text(
                "INSERT INTO ingestion_meta (key, value) VALUES (:k,:v) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
            ),
            {"k": k, "v": v},
        )
