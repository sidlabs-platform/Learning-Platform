"""
Learning Platform MVP — FastAPI application entry point.

This module bootstraps the FastAPI application:

- Registers middleware (CORS, TrustedHost).
- Mounts static files and configures Jinja2 templates.
- Defines the lifespan handler (database table creation on startup).
- Registers the ``/health`` readiness endpoint.
- Includes service routers (stubbed until each wave's router is implemented).
- Installs global exception handlers for 404 and 500 responses.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config.settings import get_settings
from src.database import init_db

logger = logging.getLogger(__name__)

settings = get_settings()


# ---------------------------------------------------------------------------
# Lifespan handler
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    **Startup**: Creates all database tables that do not yet exist.
    **Shutdown**: Logs a clean shutdown message (connection pools are closed
    automatically by SQLAlchemy when the event loop exits).
    """
    logger.info("Starting up Learning Platform MVP (env=%s)", settings.environment)
    await init_db()
    logger.info("Database tables initialised.")
    yield
    logger.info("Shutting down Learning Platform MVP.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns a fully configured :class:`~fastapi.FastAPI` instance with
    middleware, static file mounts, routers, and exception handlers attached.
    """
    application = FastAPI(
        title="Learning Platform MVP",
        description=(
            "A minimum-viable learning platform where Learners enrol in and "
            "complete courses, and Admins create and manage courses with "
            "AI-assisted content generation via GitHub Models."
        ),
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------ #
    # Middleware                                                           #
    # ------------------------------------------------------------------ #

    # CORS — origins sourced from settings; wildcard "*" is never used.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # TrustedHost — enforced in non-development environments.
    if settings.environment != "development":
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.cors_origins_list or ["*"],
        )

    # ------------------------------------------------------------------ #
    # Static files                                                        #
    # ------------------------------------------------------------------ #
    try:
        application.mount(
            "/static",
            StaticFiles(directory="src/static"),
            name="static",
        )
    except RuntimeError:
        # Directory may not exist during testing; non-fatal.
        logger.warning("Static files directory 'src/static' not found — skipping mount.")

    # ------------------------------------------------------------------ #
    # Service routers                                                     #
    # (Uncomment each include as the corresponding router is implemented) #
    # ------------------------------------------------------------------ #

    # Auth service — TASK-005
    try:
        from src.auth.router import router as auth_router  # noqa: PLC0415

        application.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    except ImportError:
        logger.debug("Auth router not yet available — skipping.")

    # Course management service — TASK-009
    try:
        from src.course_management.router import router as courses_router  # noqa: PLC0415

        application.include_router(courses_router, prefix="/api/v1/courses", tags=["courses"])
    except ImportError:
        logger.debug("Courses router not yet available — skipping.")

    # AI generation service — TASK-018
    try:
        from src.ai_generation.router import router as ai_router  # noqa: PLC0415

        application.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
    except ImportError:
        logger.debug("AI generation router not yet available — skipping.")

    # Progress tracking service — TASK-021
    try:
        from src.progress.router import router as progress_router  # noqa: PLC0415

        application.include_router(progress_router, prefix="/api/v1/progress", tags=["progress"])
    except ImportError:
        logger.debug("Progress router not yet available — skipping.")

    # Reporting service — TASK-025
    try:
        from src.reporting.router import router as reporting_router  # noqa: PLC0415

        application.include_router(reporting_router, prefix="/api/v1/reports", tags=["reporting"])
    except ImportError:
        logger.debug("Reporting router not yet available — skipping.")

    # Frontend page routes — TASK-028+
    try:
        from src.frontend.router import router as frontend_router  # noqa: PLC0415

        application.include_router(frontend_router, tags=["frontend"])
    except ImportError:
        logger.debug("Frontend router not yet available — skipping.")

    # ------------------------------------------------------------------ #
    # Built-in endpoints                                                  #
    # ------------------------------------------------------------------ #

    @application.get(
        "/health",
        tags=["ops"],
        summary="Readiness health check",
        response_description="Service health status",
    )
    async def health_check() -> dict[str, str]:
        """
        Return a simple liveness / readiness indicator.

        Returns ``{"status": "ok", "environment": "<env>"}`` with HTTP 200
        when the application is running and able to serve requests.
        """
        return {"status": "ok", "environment": settings.environment}

    # ------------------------------------------------------------------ #
    # Global exception handlers                                           #
    # ------------------------------------------------------------------ #

    @application.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a JSON 404 response for unmatched routes."""
        return JSONResponse(
            status_code=404,
            content={"detail": "The requested resource was not found."},
        )

    @application.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a JSON 500 response for unhandled server errors."""
        logger.exception("Unhandled server error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."},
        )

    return application


# ---------------------------------------------------------------------------
# Module-level app instance (consumed by Uvicorn / Gunicorn)
# ---------------------------------------------------------------------------

app: FastAPI = create_app()
