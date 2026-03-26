"""FastAPI database session dependency.

Use ``get_db`` as a ``Depends`` argument in route handlers to receive an
``AsyncSession`` that is automatically committed on success and rolled back
on any unhandled exception.

Example::

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.database import get_db

    @router.get("/items")
    async def list_items(db: AsyncSession = Depends(get_db)):
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for a single request lifecycle.

    - **Commits** the session automatically when the handler returns normally.
    - **Rolls back** and re-raises if any exception propagates out of the
      handler, ensuring the session is never left in a dirty state.
    - Always **closes** the session in the ``finally`` block.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # Note: the async context manager (``async with AsyncSessionLocal()``)
        # automatically closes the session on exit — no explicit close needed.
