"""SQLAlchemy async engine and session factory.

The engine is created once at import time using the ``database_url`` from
application settings.  ``echo`` is enabled in *development* to aid debugging.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    echo=_settings.environment == "development",
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
