from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.routers import api

DIST = ROOT / "frontend" / "dist"
SERVE_SPA = os.environ.get("SERVE_SPA", "").lower() in ("1", "true", "yes")

app = FastAPI(
    title="2025-26 NBA Lineup Intelligence API",
    version="1.0.0",
    description="Regular-season lineup analytics, ULS, and substitution simulation.",
)

_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

# Optional: allow any *.vercel.app preview/production UI (portfolio convenience). Prefer explicit CORS_ORIGINS in production.
_allow_regex: str | None = None
if os.environ.get("CORS_ALLOW_VERCEL", "").lower() in ("1", "true", "yes"):
    _allow_regex = r"^https://[a-zA-Z0-9.-]+\.vercel\.app$"

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
