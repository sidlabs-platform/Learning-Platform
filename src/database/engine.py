"""
SQLAlchemy async engine and session factory for the Learning Platform.

The engine is created once at module import time using the ``DATABASE_URL``
setting.  ``AsyncSessionLocal`` is the async session factory used by both the
``get_db()`` dependency and the ``init_db()`` startup helper.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Connect args — SQLite requires check_same_thread=False when using threads,
# but the setting is not valid for other drivers (e.g., asyncpg).
# ---------------------------------------------------------------------------
_connect_args: dict = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=(settings.environment == "development"),
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
