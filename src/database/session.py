"""
FastAPI async database session dependency.

Usage in route handlers::

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.database import get_db

    @router.get("/items")
    async def list_items(db: AsyncSession = Depends(get_db)):
        ...

The dependency yields an :class:`~sqlalchemy.ext.asyncio.AsyncSession`, commits
on success, and rolls back on any unhandled exception before closing the session.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an :class:`~sqlalchemy.ext.asyncio.AsyncSession` scoped to the
    current HTTP request.

    - Commits automatically when the request handler returns without error.
    - Rolls back and re-raises on any unhandled exception.
    - Always closes the session (connection returned to pool).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
