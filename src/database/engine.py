"""SQLAlchemy async engine and session factory.

The engine is created once at import time using the ``database_url`` from
application settings.  ``echo`` is enabled in *development* to aid debugging.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import os

# Read only database_url / environment from env directly so this module can be
# imported without all required Settings fields (github_models_api_key etc.) — 
# important during Alembic migrations and test collection.
_database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./learning_platform.db",
)
_environment = os.environ.get("ENVIRONMENT", "development")

engine = create_async_engine(
    _database_url,
    echo=_environment == "development",
    future=True,
)
"""Shared async SQLAlchemy engine.  Do **not** replace this in production code —
   use ``AsyncSessionLocal`` or the ``get_db`` dependency instead."""

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
"""Session factory.  Each call returns a new ``AsyncSession`` bound to
   ``engine``."""
