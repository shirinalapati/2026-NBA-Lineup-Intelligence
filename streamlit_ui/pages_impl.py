"""All app sections — parity with React routes (About, Overview, Leaderboard, Explorer, Underrated, Simulator)."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from backend.app.services import lineups_repo
from backend.app.services.simulation import simulate_substitution
from streamlit_ui.charts import fig_minutes_net_scatter, fig_off_def_scatter, fig_sim_before_after, fig_top_net_bar
from streamlit_ui.data_access import fetch_scope
from streamlit_ui.formatting import fmt1, fmt2, league_team_rank, lineup_names, rank_slash_total

SORT_OPTIONS: list[tuple[str, str]] = [
    ("net_rating", "Net"),
    ("offensive_rating", "ORtg"),
    ("defensive_rating", "DRtg"),
    ("minutes", "Minutes"),
    ("possessions", "Poss"),
]

RECOMMENDED_MINUTES_FLOOR = 50
SIM_LINEUP_MIN_MINUTES = 30
SIM_LINEUP_FETCH_LIMIT = 100


def _stat_cards_html(cards: list[tuple[str, str, str | None]]) -> str:
    parts = []
    for label, value, rank in cards:
        r = f'<div class="li-stat-rank">{rank}</div>' if rank else ""
        parts.append(
            f'<div class="li-stat-card"><div class="li-stat-label">{label}</div>'
            f'<div class="li-stat-value">{value}</div>{r}</div>'
        )
    return f'<div class="li-card-grid">{"".join(parts)}</div>'


def lineup_dataframe(lineups: list[dict[str, Any]], *, show_uls: bool, show_rank: bool = True) -> pd.DataFrame:
    rows_out: list[dict[str, Any]] = []
    for i, l in enumerate(lineups):
        row: dict[str, Any] = {}
        if show_rank:
            row["#"] = i + 1
        row["Team"] = l.get("team_abbr")
        row["Lineup"] = lineup_names(l)
        row["MIN"] = fmt1(l.get("minutes"))
        row["Poss"] = fmt1(l.get("possessions"))
        row["ORtg"] = fmt1(l.get("offensive_rating"))
        row["DRtg"] = fmt1(l.get("defensive_rating"))
        row["Net"] = fmt2(l.get("net_rating"))
        if show_uls:
            u = l.get("underrated_lineup_score")
            row["ULS"] = fmt1(u) if u is not None else "—"
        rows_out.append(row)
    return pd.DataFrame(rows_out)


def render_about() -> None:
    root = Path(__file__).resolve().parents[1]
    about_path = root / "docs" / "about_project.md"
    if about_path.is_file():
        st.markdown(about_path.read_text(encoding="utf-8"))
    else:
        st.warning(
            f"Missing `{about_path.relative_to(root)}`. Generate it with: "
            "`python scripts/about_tsx_to_markdown.py`"
        )


def render_overview(db: Session) -> None:
    st.markdown("## 2025-26 NBA Lineup Intelligence")
    st.markdown(
        "Evaluate five-man units across the **2025-26 NBA regular season only** (no playoffs or play-in). "
        "Discover the best lineups, surface under-used high-performers with ULS, and prototype substitution decisions."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Open leaderboard", type="primary", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()
    with c2:
        if st.button("Substitution simulator", use_container_width=True):
            st.session_state.page = "simulator"
            st.rerun()
    with c3:
        if st.button("Underrated lineups", use_container_width=True):
            st.session_state.page = "underrated"
            st.rerun()
    st.markdown(
        "The **About** tab has the full project introduction, methodology, limitations, and roadmap (same substance as the React home)."
    )

    teams = lineups_repo.fetch_teams(db)
    top = lineups_repo.fetch_lineups(db, min_minutes=100, sort="net_rating", limit=10)
    scatter = lineups_repo.fetch_lineups(db, min_minutes=0, sort="minutes", fetch_all=True, limit=200)
    scope = fetch_scope(db)

    if scope.get("data_source") != "nba_stats_api":
        st.error(
            f"**Not on live NBA data.** Ingest source is `{scope.get('data_source')}`. "
            "Run `python -m data_pipeline.ingest_all` for real league data."
        )

    avg_net = (
        sum(float(x.get("net_rating") or 0) for x in top) / len(top)
        if top
        else float("nan")
    )
    st.markdown(
        _stat_cards_html(
            [
                ("Teams in scope", str(len(teams)), None),
                ("Top-10 avg net (sample)", f"{avg_net:.1f}" if top else "—", None),
                (
                    "Season scope",
                    f"{scope.get('season')} · {scope.get('season_type')}",
                    f"Ingest: {scope.get('data_source')}",
                ),
            ]
        ),
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns(2)
    with g1:
        if top:
            st.plotly_chart(fig_top_net_bar(top), use_container_width=True)
        else:
            st.info("No lineup rows for charts.")
    with g2:
        if scatter:
            st.plotly_chart(fig_minutes_net_scatter(scatter), use_container_width=True)

    st.markdown("### Featured lineups")
    if top:
        st.dataframe(lineup_dataframe(top, show_uls=True), use_container_width=True, hide_index=True)
    else:
        st.caption("No data.")


def render_leaderboard(db: Session) -> None:
    st.markdown("## Lineup leaderboard")
    st.caption(
        "Minutes slider is a **minimum floor**: lineups need **at least** that many shared minutes. "
        f"Default **{RECOMMENDED_MINUTES_FLOOR}** aligns with ULS eligibility."
    )
    teams = lineups_repo.fetch_teams(db)
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    with col1:
        mn = st.slider("Minutes floor (≥)", 0, 600, RECOMMENDED_MINUTES_FLOOR, step=10)
    with col2:
        team_opts = [""] + [t["team_abbr"] for t in teams]
        team = st.selectbox("Team", team_opts, format_func=lambda x: "All" if x == "" else x)
    with col3:
        sort_labels = dict(SORT_OPTIONS)
        sort_key = st.selectbox("Sort", list(sort_labels.keys()), format_func=lambda k: sort_labels[k])
    with col4:
        q = st.text_input("Search", "")

    lineups = lineups_repo.fetch_lineups(
        db,
        min_minutes=float(mn),
        team=team or None,
        sort=sort_key,  # type: ignore[arg-type]
        limit=300,
        search=q or None,
    )

    csv_buf = io.StringIO()
    w = csv.writer(csv_buf)
    w.writerow(["team", "lineup", "min", "poss", "ortg", "drtg", "net", "uls"])
    for l in lineups:
        w.writerow(
            [
                l.get("team_abbr"),
                " | ".join(
                    p
                    for p in [
                        l.get("player_1_name"),
                        l.get("player_2_name"),
                        l.get("player_3_name"),
                        l.get("player_4_name"),
                        l.get("player_5_name"),
                    ]
                    if p
                ),
                l.get("minutes"),
                l.get("possessions") or "",
                l.get("offensive_rating") or "",
                l.get("defensive_rating") or "",
                l.get("net_rating") or "",
                l.get("underrated_lineup_score") or "",
            ]
        )
    st.download_button(
        "Export CSV",
        data=csv_buf.getvalue().encode(),
        file_name="lineup-leaderboard.csv",
        mime="text/csv",
    )

    st.dataframe(lineup_dataframe(lineups, show_uls=True), use_container_width=True, hide_index=True)


def render_explorer(db: Session) -> None:
    teams = lineups_repo.fetch_teams(db)
    if "explorer_team" not in st.session_state:
        st.session_state.explorer_team = "BOS"
    abbrs = [t["team_abbr"] for t in teams]
    default_i = abbrs.index(st.session_state.explorer_team) if st.session_state.explorer_team in abbrs else 0

    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("## Team lineup explorer")
        st.caption(
            "Compare best-performing, heaviest-minute, and underrated five-man groups in context of team efficiency."
        )
    with h2:
        team = st.selectbox("Team", abbrs, index=default_i, key="explorer_team_sb")
    st.session_state.explorer_team = team

    info = next((x for x in teams if x["team_abbr"] == team), None)
    ranks = None
    if info and teams:

        def _r(getter: Any, hi: bool) -> str | None:
            rr = league_team_rank(teams, team, getter, higher_is_better=hi)
            return rank_slash_total(rr)

        ranks = {
            "ortg": _r(lambda t: t.get("offensive_rating"), True),
            "drtg": _r(lambda t: t.get("defensive_rating"), False),
            "net": _r(lambda t: t.get("net_rating"), True),
            "pace": _r(lambda t: t.get("pace"), True),
        }

    if info and ranks:
        st.markdown(
            _stat_cards_html(
                [
                    ("Team ORtg", fmt2(info.get("offensive_rating")), ranks["ortg"]),
                    ("Team DRtg", fmt2(info.get("defensive_rating")), ranks["drtg"]),
                    ("Team net", fmt2(info.get("net_rating")), ranks["net"]),
                    ("Pace", fmt2(info.get("pace")), ranks["pace"]),
                ]
            ),
            unsafe_allow_html=True,
        )
        st.caption(
            "League rank among teams in scope (typically 30). Higher is better for ORtg, net, and pace; **lower DRtg is better defense**."
        )

    best = lineups_repo.fetch_lineups(db, min_minutes=50, team=team, sort="net_rating", limit=5)
    heavy = lineups_repo.fetch_lineups(db, min_minutes=0, team=team, sort="minutes", limit=5)
    under = lineups_repo.fetch_lineups(
        db, min_minutes=50, team=team, sort="underrated_lineup_score", limit=5
    )
    all_rows = lineups_repo.fetch_lineups(db, min_minutes=40, team=team, sort="net_rating", limit=80)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### Best net (qualified)")
        st.caption("Min ≥ 50 · order: net then minutes.")
        st.dataframe(lineup_dataframe(best, show_uls=False), use_container_width=True, hide_index=True)
    with c2:
        st.markdown("##### Most minutes")
        st.dataframe(lineup_dataframe(heavy, show_uls=False), use_container_width=True, hide_index=True)
    with c3:
        st.markdown("##### Most underrated (ULS)")
        st.dataframe(lineup_dataframe(under, show_uls=True), use_container_width=True, hide_index=True)

    st.markdown("### Team lineups: offensive vs defensive rating")
    if all_rows:
        st.plotly_chart(fig_off_def_scatter(all_rows), use_container_width=True)
    else:
        st.caption("No data.")


def render_underrated(db: Session) -> None:
    st.markdown("## Underrated lineup score")
    st.caption(
        "ULS blends normalized net, offense, inverted defense, limited-minutes bonus, and possessions. "
        "Scores are only defined for lineups with **≥ 50 minutes** together."
    )
    teams = lineups_repo.fetch_teams(db)
    col1, col2 = st.columns([1, 1])
    with col1:
        mn = st.slider("Minutes floor (≥)", 50, 400, 50, step=10)
    with col2:
        team_opts = [""] + [t["team_abbr"] for t in teams]
        team = st.selectbox("Team filter", team_opts, format_func=lambda x: "All teams" if x == "" else x)

    lineups = lineups_repo.fetch_lineups(
        db,
        min_minutes=float(mn),
        team=team or None,
        sort="underrated_lineup_score",
        limit=150,
    )
    st.dataframe(lineup_dataframe(lineups, show_uls=True), use_container_width=True, hide_index=True)


def render_simulator(db: Session) -> None:
    st.markdown("## Substitution simulator")
    st.caption(
        "Prototype decision support: start from an observed lineup’s efficiency, then adjust using player-level "
        "OBPM, DBPM, TS%, AST%, TOV%, STL%, and BLK% deltas (see **About** → methodology)."
    )
    st.info(
        "Lineup numbers describe the **entire five-man unit** while those five shared the floor—small samples and "
        "context still matter.",
    )

    teams = lineups_repo.fetch_teams(db)
    team = st.selectbox("Team", [t["team_abbr"] for t in teams], index=0)
    lineups = lineups_repo.fetch_lineups(
        db,
        min_minutes=SIM_LINEUP_MIN_MINUTES,
        team=team,
        sort="minutes",
        limit=SIM_LINEUP_FETCH_LIMIT,
    )
    players = lineups_repo.fetch_players_by_team(db, team)

    if not lineups:
        st.warning("No lineups for this team at the simulator minute floor.")
        return

    lineup_labels = {
        l["lineup_id"]: f"{lineup_names(l) or team} · {float(l.get('minutes') or 0):.0f} min · net {fmt1(l.get('net_rating'))}"
        for l in lineups
    }
    lineup_id = st.selectbox("Lineup", [l["lineup_id"] for l in lineups], format_func=lambda i: lineup_labels[i])

    lu = next((x for x in lineups if x["lineup_id"] == lineup_id), None)
    if not lu:
        return
    pids = [
        lu.get("player_1_id"),
        lu.get("player_2_id"),
        lu.get("player_3_id"),
        lu.get("player_4_id"),
        lu.get("player_5_id"),
    ]
    pids = [int(x) for x in pids if x]

    in_lineup = {pid: next((p for p in players if int(p["player_id"]) == pid), None) for pid in pids}

    def _name_from_lineup_row(lu_row: dict[str, Any], pid: int) -> str | None:
        for k in range(1, 6):
            if int(lu_row.get(f"player_{k}_id") or 0) == int(pid):
                return lu_row.get(f"player_{k}_name")  # type: ignore[return-value]
        return None

    out_labels = {
        pid: (in_lineup[pid] or {}).get("player_name") or _name_from_lineup_row(lu, pid) or f"Player #{pid}"
        for pid in pids
    }
    out_id = st.selectbox("Player out", pids, format_func=lambda pid: str(out_labels.get(pid)))

    replacement_pool = [p for p in players if int(p["player_id"]) not in pids]
    if not replacement_pool:
        st.warning("No bench players found for this team in the roster table.")
        return

    rep_ids = [int(p["player_id"]) for p in replacement_pool]

    def _rep_label(pid: int) -> str:
        p = next(pl for pl in replacement_pool if int(pl["player_id"]) == pid)
        return f"{p['player_name']} ({p.get('position') or '—'})"

    in_id = st.selectbox("Replacement in", rep_ids, format_func=_rep_label)

    sig = (team, str(lineup_id), int(out_id), int(in_id))
    if st.session_state.get("sim_sig") != sig:
        st.session_state.pop("sim_last", None)
    st.session_state["sim_sig"] = sig

    if st.button("Run simulation", type="primary"):
        removed = lineups_repo.fetch_player(db, int(out_id))
        incoming = lineups_repo.fetch_player(db, int(in_id))
        if not removed or not incoming:
            st.error("Player lookup failed.")
        else:
            try:
                result = simulate_substitution(
                    team_abbr=team.upper(),
                    lineup_id=str(lineup_id),
                    cur_off=float(lu["offensive_rating"]),
                    cur_def=float(lu["defensive_rating"]),
                    removed=removed,
                    incoming=incoming,
                )
            except Exception as e:  # noqa: BLE001
                st.error(str(e))
            else:
                d = result.model_dump()
                st.session_state["sim_last"] = d

    sim = st.session_state.get("sim_last")
    if sim:
        d = sim
        st.success(d.get("summary", "Done"))
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Δ Net", fmt2(d.get("delta_net_rating")))
        with m2:
            st.metric("Δ Offense", fmt2(d.get("delta_offensive_rating")))
        with m3:
            st.metric("Δ Defense", fmt2(d.get("delta_defensive_rating")))

        chart_rows = [
            {"name": "Offense", "before": d["baseline_offensive_rating"], "after": d["projected_offensive_rating"]},
            {"name": "Defense", "before": d["baseline_defensive_rating"], "after": d["projected_defensive_rating"]},
            {"name": "Net", "before": d["baseline_net_rating"], "after": d["projected_net_rating"]},
        ]
        st.plotly_chart(fig_sim_before_after(chart_rows), use_container_width=True)


def render_main(db: Session | None) -> None:
    page = st.session_state.get("page", "about")
    if page == "about":
        render_about()
    elif db is None:
        st.error("Database not available.")
    elif page == "overview":
        render_overview(db)
    elif page == "leaderboard":
        render_leaderboard(db)
    elif page == "explorer":
        render_explorer(db)
    elif page == "underrated":
        render_underrated(db)
    elif page == "simulator":
        render_simulator(db)
    else:
        render_about()
