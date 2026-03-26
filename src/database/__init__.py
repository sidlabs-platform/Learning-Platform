"""Database package — SQLAlchemy async engine, session, and declarative base.

Exports:
    Base              — Declarative base class; all ORM models inherit from it.
    JSONList          — TypeDecorator that stores ``list[str]`` as a JSON string.
    engine            — Shared ``AsyncEngine`` instance.
    AsyncSessionLocal — ``async_sessionmaker`` factory for creating sessions.
    get_db            — FastAPI dependency that yields a managed ``AsyncSession``.

Example::

    from src.database import Base, get_db, AsyncSessionLocal
"""

from src.database.base import Base, JSONList
from src.database.engine import AsyncSessionLocal, engine
from src.database.session import get_db

__all__ = [
    "Base",
    "JSONList",
    "engine",
    "AsyncSessionLocal",
    "get_db",
]
