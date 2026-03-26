"""
Lesson service for the Learning Platform MVP.

Provides CRUD operations for :class:`~src.models.Lesson` entities.
All lesson content is sanitised via :func:`~src.course_management.sanitiser.sanitise_markdown`
before being persisted to the database.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.course_management.sanitiser import sanitise_markdown
from src.course_management.schemas import LessonCreate, LessonUpdate
from src.models import Lesson

logger = logging.getLogger(__name__)


async def create_lesson(
    module_id: str,
    lesson_in: LessonCreate,
    db: AsyncSession,
) -> Lesson:
    """Create a new lesson within a module.

    Markdown content is sanitised before storage to prevent XSS.

    Args:
        module_id: UUID string of the parent module.
        lesson_in: Validated creation payload.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.Lesson` instance.
    """
    lesson = Lesson(
        id=str(uuid.uuid4()),
        module_id=module_id,
        title=lesson_in.title,
        markdown_content=sanitise_markdown(lesson_in.markdown_content),
        estimated_minutes=lesson_in.estimated_minutes,
        sort_order=lesson_in.sort_order,
    )
    db.add(lesson)
    await db.flush()
    await db.refresh(lesson)
    logger.info("Created lesson %s in module %s", lesson.id, module_id)
    return lesson


async def get_lesson(lesson_id: str, db: AsyncSession) -> Optional[Lesson]:
    """Fetch a single lesson by its primary key.

    Args:
        lesson_id: UUID string of the lesson.
        db: An open async database session.

    Returns:
        The matching :class:`~src.models.Lesson` or ``None`` if not found.
    """
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    return result.scalars().first()


async def update_lesson(
    lesson_id: str,
    lesson_in: LessonUpdate,
    db: AsyncSession,
) -> Optional[Lesson]:
    """Apply a partial update to an existing lesson.

    When ``markdown_content`` is provided it is sanitised before storage.

    Args:
        lesson_id: UUID string of the lesson to update.
        lesson_in: Validated update payload (all fields optional).
        db: An open async database session.

    Returns:
        The updated :class:`~src.models.Lesson`, or ``None`` if not found.
    """
    lesson = await get_lesson(lesson_id, db)
    if lesson is None:
        return None

    update_data = lesson_in.model_dump(exclude_unset=True)
    if "markdown_content" in update_data:
        update_data["markdown_content"] = sanitise_markdown(update_data["markdown_content"])

    for field, value in update_data.items():
        setattr(lesson, field, value)

    db.add(lesson)
    await db.flush()
    await db.refresh(lesson)
    logger.info("Updated lesson %s", lesson_id)
    return lesson


async def delete_lesson(lesson_id: str, db: AsyncSession) -> bool:
    """Delete a lesson by primary key.

    Args:
        lesson_id: UUID string of the lesson to delete.
        db: An open async database session.

    Returns:
        ``True`` if the lesson was deleted, ``False`` if it was not found.
    """
    lesson = await get_lesson(lesson_id, db)
    if lesson is None:
        return False
    await db.delete(lesson)
    await db.flush()
    logger.info("Deleted lesson %s", lesson_id)
    return True


async def list_module_lessons(module_id: str, db: AsyncSession) -> list[Lesson]:
    """List all lessons for a module, ordered by ``sort_order``.

    Args:
        module_id: UUID string of the parent module.
        db: An open async database session.

    Returns:
        Ordered list of :class:`~src.models.Lesson` instances.
    """
    result = await db.execute(
        select(Lesson)
        .where(Lesson.module_id == module_id)
        .order_by(Lesson.sort_order)
    )
    return list(result.scalars().all())


__all__ = [
    "create_lesson",
    "get_lesson",
    "update_lesson",
    "delete_lesson",
    "list_module_lessons",
]
