"""Course management service — CRUD operations and catalog queries.

Provides all database-backed operations for managing courses, including:

- Creating, reading, updating, and deleting courses.
- Publishing and unpublishing courses.
- Listing all courses (admin) with optional status filter.
- Serving the public catalog (published courses only).
- Loading a full course detail with eagerly loaded modules, lessons, and
  quiz questions.

All functions are ``async`` and accept an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
as their first argument.  Business-logic errors are surfaced as
:class:`~fastapi.HTTPException` instances so they propagate cleanly through
FastAPI route handlers.
"""

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Course, CourseStatus, Lesson, Module, QuizQuestion
from src.schemas.course import CourseCreate, CourseUpdate
from src.utils.sanitiser import sanitise_markdown

logger = logging.getLogger(__name__)


async def create_course(
    db: AsyncSession,
    course_in: CourseCreate,
    created_by: int,
) -> Course:
    """Create a new course in ``draft`` status.

    Args:
        db: Active async SQLAlchemy session.
        course_in: Validated creation payload.
        created_by: Primary key of the admin user creating the course.

    Returns:
        The newly persisted ``Course`` ORM instance.
    """
    course = Course(
        title=course_in.title,
        description=sanitise_markdown(course_in.description) if course_in.description else "",
        status=CourseStatus.draft,
        difficulty=course_in.difficulty.value if hasattr(course_in.difficulty, "value") else course_in.difficulty,
        estimated_duration=course_in.estimated_duration,
        tags=course_in.tags,
        created_by=created_by,
    )
    db.add(course)
    await db.flush()
    await db.refresh(course)
    logger.info("Course created: id=%d title=%r by user_id=%d", course.id, course.title, created_by)
    return course


async def get_course(db: AsyncSession, course_id: int) -> Course:
    """Fetch a course by primary key.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course to retrieve.

    Returns:
        The matching ``Course`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no course with the given ID exists.
    """
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found",
        )
    return course


async def list_courses(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
) -> list[Course]:
    """List courses for admin views with optional status filtering.

    Args:
        db: Active async SQLAlchemy session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        status_filter: Optional ``CourseStatus`` value string to filter by
            (``"draft"`` or ``"published"``).  When ``None``, all statuses
            are returned.

    Returns:
        A list of ``Course`` ORM instances ordered by creation date descending.
    """
    stmt = select(Course).order_by(Course.created_at.desc()).offset(skip).limit(limit)
    if status_filter:
        try:
            status_enum = CourseStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter!r}. Must be 'draft' or 'published'.",
            )
        stmt = stmt.where(Course.status == status_enum)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_course(
    db: AsyncSession,
    course_id: int,
    course_in: CourseUpdate,
) -> Course:
    """Partially update mutable fields on an existing course.

    Only non-``None`` fields in ``course_in`` are applied so this behaves
    as a PATCH operation.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course to update.
        course_in: Validated update payload (fields are all optional).

    Returns:
        The updated ``Course`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no course with the given ID exists.
    """
    course = await get_course(db, course_id)
    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "description" and value is not None:
            value = sanitise_markdown(value)
        if field == "difficulty" and hasattr(value, "value"):
            value = value.value
        if field == "status" and hasattr(value, "value"):
            value = CourseStatus(value.value)
        setattr(course, field, value)
    await db.flush()
    await db.refresh(course)
    logger.info("Course updated: id=%d fields=%s", course_id, list(update_data.keys()))
    return course


async def delete_course(db: AsyncSession, course_id: int) -> None:
    """Permanently delete a course and all its cascaded child records.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course to delete.

    Raises:
        HTTPException: 404 Not Found if no course with the given ID exists.
    """
    course = await get_course(db, course_id)
    await db.delete(course)
    await db.flush()
    logger.info("Course deleted: id=%d", course_id)


async def publish_course(db: AsyncSession, course_id: int) -> Course:
    """Set a course's status to ``published``, making it visible in the catalog.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course to publish.

    Returns:
        The updated ``Course`` ORM instance with ``status == CourseStatus.published``.

    Raises:
        HTTPException: 404 Not Found if no course with the given ID exists.
    """
    course = await get_course(db, course_id)
    course.status = CourseStatus.published
    await db.flush()
    await db.refresh(course)
    logger.info("Course published: id=%d", course_id)
    return course


async def unpublish_course(db: AsyncSession, course_id: int) -> Course:
    """Revert a course's status to ``draft``, hiding it from the learner catalog.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course to unpublish.

    Returns:
        The updated ``Course`` ORM instance with ``status == CourseStatus.draft``.

    Raises:
        HTTPException: 404 Not Found if no course with the given ID exists.
    """
    course = await get_course(db, course_id)
    course.status = CourseStatus.draft
    await db.flush()
    await db.refresh(course)
    logger.info("Course unpublished: id=%d", course_id)
    return course


async def get_catalog(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[Course]:
    """Return published courses for the learner-facing catalog.

    Only courses with ``status == CourseStatus.published`` are included.

    Args:
        db: Active async SQLAlchemy session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of published ``Course`` ORM instances ordered by creation date
        descending.
    """
    stmt = (
        select(Course)
        .where(Course.status == CourseStatus.published)
        .order_by(Course.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_course_detail(db: AsyncSession, course_id: int) -> Course:
    """Fetch a course with all nested content eagerly loaded.

    Eagerly loads the full hierarchy:
    ``Course → Module[] → Lesson[]`` and ``Course → Module[] → QuizQuestion[]``

    This avoids N+1 queries when serialising the full course tree.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course to retrieve.

    Returns:
        The ``Course`` ORM instance with all relationships populated.

    Raises:
        HTTPException: 404 Not Found if no course with the given ID exists.
    """
    stmt = (
        select(Course)
        .where(Course.id == course_id)
        .options(
            selectinload(Course.modules).selectinload(Module.lessons),
            selectinload(Course.modules).selectinload(Module.quiz_questions),
        )
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found",
        )
    return course
