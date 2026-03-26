"""Learning Platform — FastAPI application entry point.

Responsibilities:
- Configure the FastAPI application with a lifespan handler that creates DB
  tables on startup.
- Register CORS middleware using ``settings.cors_origins``.
- Mount ``/static`` for static file serving.
- Configure Jinja2 template engine pointing at ``src/templates/``.
- Expose a ``GET /health`` readiness probe.
- Include all service routers (added progressively as they are implemented).
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
_STATIC_DIR = _HERE / "static"
_TEMPLATES_DIR = _HERE / "templates"

# ---------------------------------------------------------------------------
# Jinja2 templates (module-level so routers can import it)
# ---------------------------------------------------------------------------

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Application lifespan handler.

    On **startup**: ensures all SQLAlchemy-mapped tables exist in the database
    (idempotent — safe to run against an existing schema).

    On **shutdown**: disposes the database engine connection pool.
    """
    from src.database import Base, engine  # local import avoids circular deps

    logger.info("Starting Learning Platform…")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified / created.")

    yield

    await engine.dispose()
    logger.info("Learning Platform shutdown complete.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title="Learning Platform MVP",
    description=(
        "AI-assisted internal learning platform with GitHub Models integration."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------

_cors_origins: list[str] = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Routers — included conditionally so missing router modules don't crash
# startup during incremental wave development.
# ---------------------------------------------------------------------------

try:
    from src.routers.auth import router as auth_router
    app.include_router(auth_router)
    logger.info("Auth router registered.")
except ImportError as exc:
    logger.warning("Auth router not yet available: %s", exc)

# TODO: include courses router
# TODO: include AI generation router
# TODO: include progress router
# TODO: include reporting router
# TODO: include frontend page router

# ---------------------------------------------------------------------------
# Built-in endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_class=JSONResponse, tags=["system"])
async def health(request: Request) -> dict[str, Any]:
    """Readiness probe endpoint.

    Returns a simple JSON payload confirming the service is running and
    exposing the current runtime environment.

    Returns:
        dict: ``{"status": "ok", "environment": "<env>"}``
    """
    return {"status": "ok", "environment": settings.environment}
