"""Lesson service — CRUD operations for modules and lessons.

Provides all database-backed operations for managing course content
at the module and lesson level:

- Creating, reading, updating, and deleting modules within a course.
- Creating, reading, updating, and deleting lessons within a module.
- Sanitising lesson Markdown content before persistence to prevent XSS.

All functions are ``async`` and accept an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
as their first argument.  Business-logic errors are surfaced as
:class:`~fastapi.HTTPException` instances so they propagate cleanly through
FastAPI route handlers.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Lesson, Module
from src.schemas.course import LessonCreate, LessonUpdate, ModuleCreate, ModuleUpdate
from src.utils.sanitiser import sanitise_markdown

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module CRUD
# ---------------------------------------------------------------------------


async def create_module(
    db: AsyncSession,
    course_id: int,
    module_in: ModuleCreate,
) -> Module:
    """Create a new module within a course.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the parent course.
        module_in: Validated creation payload.

    Returns:
        The newly persisted ``Module`` ORM instance.
    """
    module = Module(
        course_id=course_id,
        title=module_in.title,
        summary=module_in.summary,
        sort_order=module_in.sort_order,
    )
    db.add(module)
    await db.flush()
    await db.refresh(module)
    logger.info(
        "Module created: id=%d course_id=%d title=%r",
        module.id,
        course_id,
        module.title,
    )
    return module


async def get_module(db: AsyncSession, module_id: int) -> Module:
    """Fetch a module by primary key.

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the module to retrieve.

    Returns:
        The matching ``Module`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no module with the given ID exists.
    """
    result = await db.execute(
        select(Module)
        .where(Module.id == module_id)
        .options(
            selectinload(Module.lessons),
            selectinload(Module.quiz_questions),
        )
    )
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} not found",
        )
    return module


async def list_modules(db: AsyncSession, course_id: int) -> list[Module]:
    """List all modules for a course, ordered by ``sort_order`` ascending.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the parent course.

    Returns:
        An ordered list of ``Module`` ORM instances (may be empty).
    """
    result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .options(
            selectinload(Module.lessons),
            selectinload(Module.quiz_questions),
        )
        .order_by(Module.sort_order.asc())
    )
    return list(result.scalars().all())


async def update_module(
    db: AsyncSession,
    module_id: int,
    module_in: ModuleUpdate,
) -> Module:
    """Partially update a module's mutable fields.

    Only fields explicitly set in ``module_in`` are applied (PATCH semantics).

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the module to update.
        module_in: Validated update payload (all fields optional).

    Returns:
        The updated ``Module`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no module with the given ID exists.
    """
    module = await get_module(db, module_id)
    update_data = module_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)
    await db.flush()
    await db.refresh(module)
    logger.info("Module updated: id=%d fields=%s", module_id, list(update_data.keys()))
    return module


async def delete_module(db: AsyncSession, module_id: int) -> None:
    """Delete a module and all its child lessons and quiz questions.

    Deletion cascades to lessons and quiz questions via the ``CASCADE``
    foreign-key constraint on the ORM relationship.

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the module to delete.

    Raises:
        HTTPException: 404 Not Found if no module with the given ID exists.
    """
    module = await get_module(db, module_id)
    await db.delete(module)
    await db.flush()
    logger.info("Module deleted: id=%d", module_id)


# ---------------------------------------------------------------------------
# Lesson CRUD
# ---------------------------------------------------------------------------


async def create_lesson(
    db: AsyncSession,
    module_id: int,
    lesson_in: LessonCreate,
) -> Lesson:
    """Create a new lesson within a module.

    The ``markdown_content`` is sanitised via :func:`~src.utils.sanitiser.sanitise_markdown`
    before being persisted to prevent XSS when the content is later rendered
    in a browser.

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the parent module.
        lesson_in: Validated creation payload.

    Returns:
        The newly persisted ``Lesson`` ORM instance.
    """
    sanitised_content = sanitise_markdown(lesson_in.markdown_content)
    lesson = Lesson(
        module_id=module_id,
        title=lesson_in.title,
        markdown_content=sanitised_content,
        estimated_minutes=lesson_in.estimated_minutes,
        sort_order=lesson_in.sort_order,
    )
    db.add(lesson)
    await db.flush()
    await db.refresh(lesson)
    logger.info(
        "Lesson created: id=%d module_id=%d title=%r",
        lesson.id,
        module_id,
        lesson.title,
    )
    return lesson


async def get_lesson(db: AsyncSession, lesson_id: int) -> Lesson:
    """Fetch a lesson by primary key.

    Args:
        db: Active async SQLAlchemy session.
        lesson_id: Primary key of the lesson to retrieve.

    Returns:
        The matching ``Lesson`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no lesson with the given ID exists.
    """
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson {lesson_id} not found",
        )
    return lesson


async def list_lessons(db: AsyncSession, module_id: int) -> list[Lesson]:
    """List all lessons for a module, ordered by ``sort_order`` ascending.

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the parent module.

    Returns:
        An ordered list of ``Lesson`` ORM instances (may be empty).
    """
    result = await db.execute(
        select(Lesson)
        .where(Lesson.module_id == module_id)
        .order_by(Lesson.sort_order.asc())
    )
    return list(result.scalars().all())


async def update_lesson(
    db: AsyncSession,
    lesson_id: int,
    lesson_in: LessonUpdate,
) -> Lesson:
    """Partially update a lesson's mutable fields.

    If ``markdown_content`` is provided it is sanitised before storage.
    Only fields explicitly set in ``lesson_in`` are applied (PATCH semantics).

    Args:
        db: Active async SQLAlchemy session.
        lesson_id: Primary key of the lesson to update.
        lesson_in: Validated update payload (all fields optional).

    Returns:
        The updated ``Lesson`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no lesson with the given ID exists.
    """
    lesson = await get_lesson(db, lesson_id)
    update_data = lesson_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "markdown_content" and value is not None:
            value = sanitise_markdown(value)
        setattr(lesson, field, value)
    await db.flush()
    await db.refresh(lesson)
    logger.info("Lesson updated: id=%d fields=%s", lesson_id, list(update_data.keys()))
    return lesson


async def delete_lesson(db: AsyncSession, lesson_id: int) -> None:
    """Delete a lesson.

    Args:
        db: Active async SQLAlchemy session.
        lesson_id: Primary key of the lesson to delete.

    Raises:
        HTTPException: 404 Not Found if no lesson with the given ID exists.
    """
    lesson = await get_lesson(db, lesson_id)
    await db.delete(lesson)
    await db.flush()
    logger.info("Lesson deleted: id=%d", lesson_id)
