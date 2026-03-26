"""Alembic environment script — async SQLAlchemy configuration.

This module configures Alembic to use our async SQLAlchemy engine and imports
all ORM models so that ``Base.metadata`` contains every table definition for
autogenerate support.

Pattern used: ``run_sync()`` on a live ``AsyncConnection`` so the sync Alembic
migration runner can operate against an async engine.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Alembic config object — provides access to values in alembic.ini
# ---------------------------------------------------------------------------

config = context.config

# Set up loggers as specified in the .ini file (if a config file is present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import all ORM models so Base.metadata is fully populated
# ---------------------------------------------------------------------------

from src.database import Base  # noqa: E402
import src.models  # noqa: E402, F401 — registers all 10 ORM models on Base.metadata

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration (generates SQL script without DB connection)
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the Alembic context with a URL instead of an engine/connection.
    Useful for generating SQL scripts to be reviewed or applied manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (runs against a live database connection)
# ---------------------------------------------------------------------------


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations using a synchronous connection.

    Called from ``run_async_migrations`` via ``connection.run_sync()``.

    Args:
        connection: A synchronous SQLAlchemy ``Connection`` instance.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and drive migrations through a sync wrapper.

    Uses the shared ``engine`` from ``src.database`` so that the same
    ``DATABASE_URL`` environment variable governs both runtime and migrations.
    """
    from src.database import engine  # local import to avoid circular imports

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Entry point for online migration mode.

    Runs the async migration coroutine synchronously via ``asyncio.run()``.
    """
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Dispatch: offline vs. online mode
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
