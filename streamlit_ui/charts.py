"""Plotly charts matching React/Recharts styling (dark court palette)."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

from streamlit_ui.formatting import lineup_names

_BG = "#0a0f14"
_PANEL = "#131d28"
_GRID = "rgba(51, 65, 85, 0.35)"
_AXIS = "#64748b"
_ACCENT = "#3d9a7a"
_LINE = "#c9a227"
_PURPLE = "#8b5cf6"
_MUTED = "#8b9aad"


def _base_layout(title: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = dict(
        template="plotly_dark",
        paper_bgcolor=_BG,
        plot_bgcolor=_PANEL,
        font=dict(color="#cbd5e1", size=12),
        margin=dict(l=48, r=16, t=56 if title else 28, b=72),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    if title:
        out["title"] = dict(text=title, font=dict(family="Instrument Serif, Georgia, serif", size=18))
    return out


def fig_top_net_bar(lineups: list[dict[str, Any]]) -> go.Figure:
    data = lineups[:10]
    names = [f"{l.get('team_abbr', '')}" for l in data]
    nets = [float(l.get("net_rating") or 0) for l in data]
    hovers = [lineup_names(l)[:120] for l in data]
    colors = [_LINE if i < 3 else _ACCENT for i in range(len(data))]
    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=nets,
                marker_color=colors,
                marker_line_width=0,
                text=[f"{n:.2f}" for n in nets],
                textposition="outside",
                hovertext=hovers,
                hoverinfo="text+y",
            )
        ]
    )
    fig.update_layout(
        **_base_layout("Top 10 lineups by net rating"),
        xaxis=dict(showgrid=False, tickfont=dict(color=_AXIS, size=11)),
        yaxis=dict(gridcolor=_GRID, tickfont=dict(color=_AXIS, size=11), title="Net"),
        showlegend=False,
    )
    return fig


def fig_minutes_net_scatter(lineups: list[dict[str, Any]]) -> go.Figure:
    xs = [float(l.get("minutes") or 0) for l in lineups]
    ys = [float(l.get("net_rating") or 0) for l in lineups]
    texts = [f"{l.get('team_abbr','')}: {lineup_names(l)[:80]}" for l in lineups]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(color=_PURPLE, size=7, opacity=0.75, line=dict(width=0)),
                text=texts,
                hoverinfo="text+x+y",
            )
        ]
    )
    fig.update_layout(
        **_base_layout("Minutes vs net rating"),
        xaxis=dict(
            gridcolor=_GRID,
            title="Minutes — time this five-man unit played together",
            tickfont=dict(color=_AXIS, size=11),
            title_font=dict(size=11, color=_AXIS),
        ),
        yaxis=dict(
            gridcolor=_GRID,
            title="Net rating (per 100 poss.)",
            tickfont=dict(color=_AXIS, size=11),
            title_font=dict(size=11, color=_AXIS),
        ),
        showlegend=False,
    )
    return fig


def fig_off_def_scatter(lineups: list[dict[str, Any]]) -> go.Figure:
    xs = [float(l.get("offensive_rating") or 0) for l in lineups]
    ys = [float(l.get("defensive_rating") or 0) for l in lineups]
    texts = [f"{l.get('team_abbr','')}: ORtg {l.get('offensive_rating')} DRtg {l.get('defensive_rating')} Net {l.get('net_rating')}" for l in lineups]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(color=_ACCENT, size=8, opacity=0.72, line=dict(width=0)),
                text=texts,
                hoverinfo="text+x+y",
            )
        ]
    )
    fig.update_layout(
        **_base_layout("Team lineups: offensive vs defensive rating"),
        xaxis=dict(gridcolor=_GRID, title="ORtg (per 100 poss.)", tickfont=dict(color=_AXIS, size=11)),
        yaxis=dict(gridcolor=_GRID, title="DRtg (per 100 poss.)", tickfont=dict(color=_AXIS, size=11)),
        showlegend=False,
    )
    return fig


def fig_sim_before_after(rows: list[dict[str, Any]]) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Bar(name="Before", x=[r["name"] for r in rows], y=[r["before"] for r in rows], marker_color=_MUTED),
            go.Bar(name="Projected", x=[r["name"] for r in rows], y=[r["after"] for r in rows], marker_color=_ACCENT),
        ]
    )
    fig.update_layout(
        **_base_layout(),
        barmode="group",
        xaxis=dict(showgrid=False, tickfont=dict(color=_AXIS, size=11)),
        yaxis=dict(gridcolor=_GRID, tickfont=dict(color=_AXIS, size=11)),
    )
    return fig
