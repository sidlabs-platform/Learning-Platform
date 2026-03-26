"""
Database package for the Learning Platform.

Exports the primary database primitives used across all service modules:

- :data:`Base` — SQLAlchemy ``DeclarativeBase`` that all ORM models inherit from.
- :data:`engine` — Async SQLAlchemy engine instance.
- :data:`AsyncSessionLocal` — Async session factory.
- :func:`get_db` — FastAPI ``Depends``-compatible async generator dependency.
- :func:`init_db` — Startup helper that creates all tables defined under ``Base``.
- :class:`JSONList` — TypeDecorator for ``list[str]`` ↔ JSON-string columns.
"""

from src.database.base import Base, JSONList
from src.database.engine import AsyncSessionLocal, engine
from src.database.session import get_db

# Import all ORM models so that Base.metadata discovers them before create_all().
# This import must come AFTER Base is defined to avoid circular-import issues.
import src.models  # noqa: F401, E402


async def init_db() -> None:
    """
    Create all database tables defined in ``Base.metadata``.

    This is called once during application startup (lifespan handler).
    In production, Alembic migrations manage schema changes; this function
    is a safe no-op if tables already exist (``checkfirst`` is implicitly
    True for ``create_all``).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "JSONList",
]
