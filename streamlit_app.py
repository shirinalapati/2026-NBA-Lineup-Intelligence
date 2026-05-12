"""
Streamlit Cloud entrypoint — mirrors the React Lineup Intelligence UI (dark court theme, same pages).

Deploy: https://streamlit.io/cloud — set **Main file** to `streamlit_app.py`.

Database:
- Default path: `data/nba_lineups.db` (same as FastAPI). Commit a DB for Cloud, **or**
- Set secret / env **`NBA_DB_PATH`** to a writable path (e.g. `/tmp/nba_lineups.db`), **or**
- Set **`STREAMLIT_AUTO_SEED=1`** to run `python -m data_pipeline.ingest_all --seed` on first launch
  (writes to `NBA_DB_PATH` or `/tmp/nba_lineups.db` if unset — required on Streamlit Cloud read-only checkouts).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _db_path() -> Path:
    return Path(os.environ.get("NBA_DB_PATH", str(ROOT / "data" / "nba_lineups.db")))


def _ensure_database(st) -> bool:
    p = _db_path()
    if p.is_file():
        return True
    auto = os.environ.get("STREAMLIT_AUTO_SEED", "").strip().lower() in ("1", "true", "yes")
    if auto:
        if not os.environ.get("NBA_DB_PATH"):
            os.environ["NBA_DB_PATH"] = "/tmp/nba_lineups.db"
            p = _db_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with st.spinner("Building demo SQLite (`ingest_all --seed`) — first run only…"):
            r = subprocess.run(
                [sys.executable, "-m", "data_pipeline.ingest_all", "--seed"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                st.error("Seed ingest failed.")
                st.code(r.stdout + "\n" + r.stderr)
                return False
        return p.is_file()
    return False


def main() -> None:
    import streamlit as st

    from streamlit_ui.data_access import db_session
    from streamlit_ui.pages_impl import render_main
    from streamlit_ui.styling import inject_global_css, render_brand_header, render_footer

    st.set_page_config(
        page_title="Lineup Intelligence",
        page_icon="🏀",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_global_css()

    if "page" not in st.session_state:
        st.session_state.page = "about"

    render_brand_header()

    nav = [
        ("About", "about"),
        ("Overview", "overview"),
        ("Leaderboard", "leaderboard"),
        ("Team explorer", "explorer"),
        ("Underrated", "underrated"),
        ("Simulator", "simulator"),
    ]
    cols = st.columns(len(nav))
    for (label, key), col in zip(nav, cols, strict=True):
        with col:
            active = st.session_state.page == key
            if st.button(label, use_container_width=True, type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()

    st.markdown('<hr class="li-rule"/>', unsafe_allow_html=True)

    if not _ensure_database(st):
        st.error(
            f"No SQLite database at **`{_db_path()}`**. Options: (1) commit `data/nba_lineups.db`, "
            "(2) set env **`NBA_DB_PATH`** to a reachable file, or (3) set **`STREAMLIT_AUTO_SEED=1`** for a synthetic "
            "demo DB under `/tmp` on first load."
        )
        render_main(None)
        render_footer()
        st.stop()

    with db_session() as db:
        render_main(db)

    render_footer()


if __name__ == "__main__":
    main()
