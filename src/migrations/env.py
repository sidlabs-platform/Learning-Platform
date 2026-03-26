"""Alembic environment configuration for the Learning Platform MVP.

Configures Alembic to use the async SQLAlchemy engine (aiosqlite) via the
synchronous ``sync_engine`` bridge pattern, which is the recommended approach
when the application uses ``create_async_engine``.

The target metadata is sourced from ``Base.metadata`` after importing all ORM
models so that auto-generate and explicit migration scripts can reflect the full
schema.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to values within alembic.ini.
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import Base and all ORM models so that Base.metadata is fully populated.
# ---------------------------------------------------------------------------
from src.database.base import Base  # noqa: E402
import src.models  # noqa: F401, E402  — registers all 10 ORM models with Base.metadata

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Resolve the database URL from application settings (respects .env).
# ---------------------------------------------------------------------------
from src.config.settings import get_settings  # noqa: E402

_settings = get_settings()
_db_url: str = _settings.database_url


# ---------------------------------------------------------------------------
# Offline migrations (no live DB connection needed).
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine; a DBAPI
    connection is never established.  Calls to ``context.execute()`` emit the
    given string to the script output.
    """
    context.configure(
        url=_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # required for SQLite ALTER TABLE support
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (live DB connection via sync bridge on async engine).
# ---------------------------------------------------------------------------

def do_run_migrations(connection: Connection) -> None:
    """Execute migrations using the provided synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations via the sync bridge."""
    connectable = create_async_engine(
        _db_url,
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False} if _db_url.startswith("sqlite") else {},
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the asyncio event loop."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point — choose offline or online based on Alembic context.
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
