from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.routers import api

DIST = ROOT / "frontend" / "dist"


def _truthy_env(name: str) -> bool:
    v = os.environ.get(name, "").strip().strip('"').strip("'")
    return v.lower() in ("1", "true", "yes")


SERVE_SPA = _truthy_env("SERVE_SPA")

app = FastAPI(
    title="2025-26 NBA Lineup Intelligence API",
    version="1.0.0",
    description="Regular-season lineup analytics, ULS, and substitution simulation.",
)

_origins = [
    o.strip().strip('"').strip("'")
    for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]

# Optional: allow *.vercel.app / *.vercel.dev (portfolio convenience). Prefer explicit CORS_ORIGINS for custom domains.
_allow_regex: str | None = None
_cav_raw = os.environ.get("CORS_ALLOW_VERCEL", "").strip().strip('"').strip("'")
if _truthy_env("CORS_ALLOW_VERCEL"):
    _allow_regex = r"^https://[a-zA-Z0-9][a-zA-Z0-9.-]*\.vercel\.(app|dev)$"
elif _cav_raw.lower().startswith(("http://", "https://")):
    # Common dashboard mistake: paste Vercel URL into CORS_ALLOW_VERCEL (meant for CORS_ORIGINS or use flag=1).
    _as_origin = _cav_raw.rstrip("/")
    if _as_origin not in _origins:
        _origins.append(_as_origin)
    print(
        "[startup] CORS_ALLOW_VERCEL is a URL, not 1/true/yes — added it to allow_origins. "
        "For all *.vercel.app previews, set CORS_ALLOW_VERCEL=1 instead.",
        flush=True,
    )
elif _cav_raw:
    print(
        f"[startup] WARNING: CORS_ALLOW_VERCEL={_cav_raw!r} is ignored (use 1/true/yes, or put origins in CORS_ORIGINS).",
        flush=True,
    )

_cors_kw: dict = dict(
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
if _allow_regex:
    _cors_kw["allow_origin_regex"] = _allow_regex

app.add_middleware(
    CORSMiddleware,
    **_cors_kw,
)

app.include_router(api.router)


@app.middleware("http")
async def collapse_duplicate_slashes(request: Request, call_next):
    """`//api/health` does not match `/api/health` in Starlette; normalize common paste mistakes."""
    path = request.scope.get("path") or ""
    if "//" in path:
        collapsed = path
        while "//" in collapsed:
            collapsed = collapsed.replace("//", "/")
        request.scope["path"] = collapsed
    return await call_next(request)


def _safe_dist_file(relative: str) -> Path | None:
    """Resolve a path under frontend/dist; reject traversal."""
    if not relative or ".." in relative.split("/"):
        return None
    candidate = (DIST / relative).resolve()
    try:
        candidate.relative_to(DIST.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


if SERVE_SPA and (DIST / "index.html").is_file():
    if (DIST / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=str(DIST / "assets")), name="assets")

    @app.get("/")
    def spa_home():
        return FileResponse(DIST / "index.html")

    @app.get("/{full_path:path}")
    def spa_or_static(full_path: str):
        # /api/* is handled by api.router (registered first). This is a fallback for client-side routes + public files.
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(status_code=404)
        f = _safe_dist_file(full_path)
        if f is not None:
            return FileResponse(f)
        return FileResponse(DIST / "index.html")

else:

    @app.get("/")
    def root():
        return {"message": "See /docs for API", "season": "2025-26 Regular Season"}


# Render / platform logs: confirm SPA + CORS wiring at boot (check Deploy → Logs).
print(
    f"[startup] SERVE_SPA={SERVE_SPA!r} index_html={(DIST / 'index.html').is_file()!r} DIST={DIST} "
    f"CORS_ALLOW_VERCEL_flag={_truthy_env('CORS_ALLOW_VERCEL')!r} cors_vercel_regex={_allow_regex is not None!r} "
    f"cors_allow_origins_count={len(_origins)}",
    flush=True,
)
