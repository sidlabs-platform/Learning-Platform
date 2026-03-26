"""
Module service for the Learning Platform MVP.

Provides CRUD operations for :class:`~src.models.Module` entities, including
ordered listing by ``sort_order`` within a course.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.course_management.schemas import ModuleCreate, ModuleUpdate
from src.models import Module

logger = logging.getLogger(__name__)


async def create_module(
    course_id: str,
    module_in: ModuleCreate,
    db: AsyncSession,
) -> Module:
    """Create a new module within a course.

    Args:
        course_id: UUID string of the parent course.
        module_in: Validated creation payload.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.Module` instance.
    """
    module = Module(
        id=str(uuid.uuid4()),
        course_id=course_id,
        title=module_in.title,
        summary=module_in.summary,
        sort_order=module_in.sort_order,
    )
    db.add(module)
    await db.flush()
    await db.refresh(module)
    logger.info("Created module %s in course %s", module.id, course_id)
    return module


async def get_module(module_id: str, db: AsyncSession) -> Optional[Module]:
    """Fetch a single module by its primary key.

    Args:
        module_id: UUID string of the module.
        db: An open async database session.

    Returns:
        The matching :class:`~src.models.Module` or ``None`` if not found.
    """
    result = await db.execute(select(Module).where(Module.id == module_id))
    return result.scalars().first()


async def update_module(
    module_id: str,
    module_in: ModuleUpdate,
    db: AsyncSession,
) -> Optional[Module]:
    """Apply a partial update to an existing module.

    Args:
        module_id: UUID string of the module to update.
        module_in: Validated update payload (all fields optional).
        db: An open async database session.

    Returns:
        The updated :class:`~src.models.Module`, or ``None`` if not found.
    """
    module = await get_module(module_id, db)
    if module is None:
        return None

    update_data = module_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)

    db.add(module)
    await db.flush()
    await db.refresh(module)
    logger.info("Updated module %s", module_id)
    return module


async def delete_module(module_id: str, db: AsyncSession) -> bool:
    """Delete a module by primary key.

    Args:
        module_id: UUID string of the module to delete.
        db: An open async database session.

    Returns:
        ``True`` if the module was deleted, ``False`` if it was not found.
    """
    module = await get_module(module_id, db)
    if module is None:
        return False
    await db.delete(module)
    await db.flush()
    logger.info("Deleted module %s", module_id)
    return True


async def list_course_modules(course_id: str, db: AsyncSession) -> list[Module]:
    """List all modules for a course, ordered by ``sort_order``.

    Args:
        course_id: UUID string of the parent course.
        db: An open async database session.

    Returns:
        Ordered list of :class:`~src.models.Module` instances.
    """
    result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.sort_order)
    )
    return list(result.scalars().all())


__all__ = [
    "create_module",
    "get_module",
    "update_module",
    "delete_module",
    "list_course_modules",
]
