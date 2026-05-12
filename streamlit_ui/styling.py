"""Global CSS to approximate the React + Tailwind “court” dark UI."""

from __future__ import annotations

import streamlit as st

COURT_BG = "#0a0f14"
COURT_PANEL = "#131d28"
COURT_BORDER = "#243044"
ACCENT = "#3d9a7a"
LINE = "#c9a227"
MUTED = "#94a3b8"


def inject_global_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [data-testid="stAppViewContainer"] {{
            font-family: "DM Sans", system-ui, sans-serif !important;
            background: {COURT_BG} !important;
        }}
        h1, h2, h3, h4 {{
            font-family: "Instrument Serif", Georgia, serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }}
        code, .stMarkdown code {{
            font-family: "JetBrains Mono", monospace !important;
            font-size: 0.85em !important;
            background: rgba(0,0,0,0.35) !important;
            padding: 0.1em 0.35em !important;
            border-radius: 4px !important;
        }}
        [data-testid="stHeader"] {{
            background: rgba(15, 23, 32, 0.92) !important;
            border-bottom: 1px solid {COURT_BORDER} !important;
        }}
        [data-testid="stSidebar"] {{
            background: #0f1720 !important;
        }}
        div[data-testid="stVerticalBlock"] > div:has(> label > div[data-baseweb="radio"]) {{
            padding: 0.35rem 0 !important;
        }}
        .li-nav-hint {{
            font-family: "JetBrains Mono", monospace;
            font-size: 10px;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: {LINE};
            margin-bottom: 0.35rem;
        }}
        .li-brand-row {{
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }}
        .li-brand-title {{
            font-family: "Instrument Serif", Georgia, serif;
            font-size: 1.65rem;
            color: #fff;
        }}
        .li-brand-sub {{
            font-family: "JetBrains Mono", monospace;
            font-size: 10px;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: rgba(201, 162, 39, 0.95);
        }}
        .li-footer {{
            text-align: center;
            font-size: 11px;
            color: {MUTED};
            padding: 1.5rem 0 2rem;
            border-top: 1px solid {COURT_BORDER};
            margin-top: 2rem;
        }}
        .li-card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        .li-stat-card {{
            border: 1px solid {COURT_BORDER};
            background: {COURT_PANEL};
            border-radius: 12px;
            padding: 1rem 1.1rem;
        }}
        .li-stat-label {{
            font-family: "JetBrains Mono", monospace;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: {MUTED};
        }}
        .li-stat-value {{
            font-family: "Instrument Serif", Georgia, serif;
            font-size: 1.75rem;
            color: #fff;
            margin-top: 0.35rem;
        }}
        .li-stat-rank {{
            font-size: 0.9rem;
            color: {ACCENT};
            margin-top: 0.25rem;
            font-weight: 600;
        }}
        hr.li-rule {{
            border: none;
            border-top: 1px solid {COURT_BORDER};
            margin: 1.25rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    st.markdown(
        f"""
        <div class="li-nav-hint">Portfolio analytics product</div>
        <div class="li-brand-row">
          <span class="li-brand-title">Lineup Intelligence</span>
          <span class="li-brand-sub">2025-26 NBA</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="li-footer">
          2025-26 NBA regular season only (no playoffs / play-in) · Data via ingestion pipeline · Streamlit UI
        </div>
        """,
        unsafe_allow_html=True,
    )
