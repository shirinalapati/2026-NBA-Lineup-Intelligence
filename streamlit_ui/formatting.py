"""Display helpers mirroring frontend/src/lib/format.ts."""

from __future__ import annotations

from typing import Any, Callable


def fmt1(n: float | int | None) -> str:
    if n is None:
        return "—"
    try:
        return f"{float(n):.1f}"
    except (TypeError, ValueError):
        return "—"


def fmt2(n: float | int | None) -> str:
    if n is None:
        return "—"
    try:
        return f"{float(n):.2f}"
    except (TypeError, ValueError):
        return "—"


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return {1: f"{n}st", 2: f"{n}nd", 3: f"{n}rd"}.get(n % 10, f"{n}th")


def league_team_rank(
    teams: list[dict[str, Any]],
    team_abbr: str,
    get_value: Callable[[dict[str, Any]], float | int | None],
    *,
    higher_is_better: bool,
) -> tuple[int, int] | None:
    rows: list[tuple[str, float]] = []
    for t in teams:
        abbr = str(t.get("team_abbr", ""))
        v = get_value(t)
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv:  # NaN
            continue
        rows.append((abbr, fv))
    if not rows:
        return None
    rows.sort(key=lambda x: x[1], reverse=higher_is_better)
    ranks: dict[str, int] = {}
    for i, (abbr, val) in enumerate(rows):
        if i == 0 or val != rows[i - 1][1]:
            r = i + 1
        else:
            r = ranks.get(rows[i - 1][0], i + 1)
        ranks[abbr] = r
    r = ranks.get(team_abbr.upper())
    if r is None:
        return None
    return r, len(rows)


def rank_slash_total(r: tuple[int, int] | None) -> str | None:
    if not r:
        return None
    rank, total = r
    return f"{ordinal(rank)} / {total}"


def lineup_names(l: dict[str, Any]) -> str:
    parts = [
        l.get("player_1_name"),
        l.get("player_2_name"),
        l.get("player_3_name"),
        l.get("player_4_name"),
        l.get("player_5_name"),
    ]
    return " · ".join(p for p in parts if p)
