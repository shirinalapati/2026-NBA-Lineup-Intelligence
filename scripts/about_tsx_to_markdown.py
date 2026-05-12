#!/usr/bin/env python3
"""Export frontend/src/pages/AboutProject.tsx → docs/about_project.md (Streamlit About = React About)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TSX = ROOT / "frontend" / "src" / "pages" / "AboutProject.tsx"
OUT = ROOT / "docs" / "about_project.md"


def _code_blocks(s: str) -> str:
    def repl(m: re.Match[str]) -> str:
        body = m.group(1).strip()
        return f"\n\n```\n{body}\n```\n\n"

    return re.sub(r"<CodeBlock>\{`([\s\S]*?)`\}</CodeBlock>", repl, s)


def _links(s: str) -> str:
    return re.sub(
        r'<a\s+href="([^"]+)"[^>]*>([\s\S]*?)</a>',
        lambda m: f"[{re.sub(r"<[^>]+>", "", m.group(2)).strip()}]({m.group(1)})",
        s,
    )


def _simple_tags(s: str) -> str:
    s = re.sub(r"\{/\*[\s\S]*?\*/\}", "", s)
    s = s.replace("&amp;", "&")
    s = re.sub(r"<code[^>]*>", "`", s)
    s = re.sub(r"</code>", "`", s)
    s = re.sub(r"<strong[^>]*>", "**", s)
    s = re.sub(r"</strong>", "**", s)
    s = re.sub(r"<em>", "_", s)
    s = re.sub(r"</em>", "_", s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    return s


def _block(s: str, tag: str, prefix: str) -> str:
    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        inner = _simple_tags(inner)
        inner = re.sub(r"<[^>]+>", "", inner)
        inner = re.sub(r"\s+", " ", inner).strip()
        return f"\n\n{prefix}{inner}\n\n"

    return re.sub(rf"<{tag}[^>]*>([\s\S]*?)</{tag}>", repl, s)


def _lists(s: str) -> str:
    s = re.sub(r"<ul[^>]*>", "\n", s)
    s = re.sub(r"</ul>", "\n", s)
    s = re.sub(r"<ol[^>]*>", "\n", s)
    s = re.sub(r"</ol>", "\n", s)
    s = re.sub(r"<li[^>]*>", "\n- ", s)
    s = re.sub(r"</li>", "", s)
    return s


def _paragraphs(s: str) -> str:
    s = re.sub(r"<p[^>]*>", "\n\n", s)
    s = re.sub(r"</p>", "\n\n", s)
    return s


def _strip_remaining_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\{\s*'\s*'\s*\}", "", s)
    return s


def _dl(s: str) -> str:
    def repl(m: re.Match[str]) -> str:
        block = m.group(1)
        parts = re.findall(r"<dt[^>]*>([\s\S]*?)</dt>\s*<dd>([\s\S]*?)</dd>", block)
        lines = []
        for dt, dd in parts:
            dt = re.sub(r"<[^>]+>", "", dt).strip()
            dd = re.sub(r"<[^>]+>", "", dd).strip()
            lines.append(f"\n- **{dt}** — {dd}")
        return "\n" + "\n".join(lines) + "\n\n"

    return re.sub(r"<dl[^>]*>([\s\S]*?)</dl>", repl, s)


def main() -> None:
    raw = TSX.read_text(encoding="utf-8")
    m = re.search(r"<article[^>]*>([\s\S]*)</article>", raw)
    if not m:
        raise SystemExit("No <article> in AboutProject.tsx")
    inner = m.group(1)
    inner = _code_blocks(inner)
    inner = _links(inner)
    inner = re.sub(r"<header[^>]*>([\s\S]*?)</header>", r"\1", inner)
    inner = _block(inner, "h1", "# ")
    inner = _block(inner, "h2", "## ")
    inner = _block(inner, "h3", "### ")
    inner = _paragraphs(inner)
    inner = _lists(inner)
    inner = _dl(inner)
    inner = re.sub(r"<section[^>]*>", "\n", inner)
    inner = re.sub(r"</section>", "\n", inner)
    inner = re.sub(r"<div[^>]*>", "\n", inner)
    inner = re.sub(r"</div>", "\n", inner)
    inner = _simple_tags(inner)
    inner = _strip_remaining_tags(inner)
    inner = re.sub(r"\n-\s*\n+\s*", "\n- ", inner)
    inner = re.sub(r"[ \t]{2,}", " ", inner)
    inner = re.sub(r"[ \t]+\n", "\n", inner)
    inner = re.sub(r"\n{3,}", "\n\n", inner)
    inner = inner.strip() + "\n"
    OUT.write_text(inner, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
