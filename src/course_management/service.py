"""Course Management service for the Learning Platform MVP.

Provides CRUD operations for Courses, Modules, Lessons, and QuizQuestions.
All write paths sanitise Markdown content via :func:`sanitise_markdown` to
prevent XSS injection from user-supplied or AI-generated content.

All database interactions use the async SQLAlchemy ``select()`` API and are
awaited on the provided :class:`~sqlalchemy.ext.asyncio.AsyncSession`.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.course_management.sanitiser import sanitise_markdown
from src.course_management.schemas import (
    CourseCreate,
    CourseStatus,
    CourseUpdate,
    LessonCreate,
    ModuleCreate,
    QuizQuestionCreate,
)
from src.models import Course, Lesson, Module, QuizQuestion
from src.sanitize import sanitize_log

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Course helpers
# ---------------------------------------------------------------------------


async def create_course(
    course_in: CourseCreate,
    created_by: str,
    db: AsyncSession,
) -> Course:
    """Create a new course in ``draft`` status.

    Args:
        course_in: Validated request payload with course metadata.
        created_by: UUID string of the admin creating the course.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.Course` ORM instance.
    """
    now = datetime.utcnow()
    course = Course(
        id=str(uuid.uuid4()),
        title=course_in.title,
        description=course_in.description,
        status="draft",
        difficulty=course_in.difficulty.value,
        estimated_duration=course_in.estimated_duration,
        tags=course_in.tags,
        created_by=created_by,
        created_at=now,
        updated_at=now,
    )
    db.add(course)
    await db.flush()
    logger.info("Course created: course_id=%s created_by=%s", course.id, created_by)
    return course


async def get_course(course_id: str, db: AsyncSession) -> Optional[Course]:
    """Retrieve a course by its primary key.

    Args:
        course_id: UUID string of the course.
        db: An open async database session.

    Returns:
        The :class:`~src.models.Course` instance, or ``None`` if not found.
    """
    result = await db.execute(select(Course).where(Course.id == course_id))
    return result.scalar_one_or_none()


async def update_course(
    course_id: str,
    course_in: CourseUpdate,
    db: AsyncSession,
) -> Optional[Course]:
    """Apply a partial update to an existing course.

    Only fields explicitly set in *course_in* are changed.

    Args:
        course_id: UUID string of the course to update.
        course_in: Validated partial update payload.
        db: An open async database session.

    Returns:
        The updated :class:`~src.models.Course`, or ``None`` if not found.
    """
    course = await get_course(course_id, db)
    if course is None:
        return None

    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "difficulty" and value is not None:
            value = value.value  # unwrap enum to string
        setattr(course, field, value)

    course.updated_at = datetime.utcnow()
    await db.flush()
    logger.info("Course updated: course_id=%s fields=%s", sanitize_log(course_id), list(update_data.keys()))
    return course


async def delete_course(course_id: str, db: AsyncSession) -> bool:
    """Delete a course by primary key.

    Args:
        course_id: UUID string of the course to delete.
        db: An open async database session.

    Returns:
        ``True`` if the course was found and deleted, ``False`` otherwise.
    """
    course = await get_course(course_id, db)
    if course is None:
        return False
    await db.delete(course)
    await db.flush()
    logger.info("Course deleted: course_id=%s", sanitize_log(course_id))
    return True


async def publish_course(course_id: str, db: AsyncSession) -> Optional[Course]:
    """Transition a course from ``draft`` to ``published`` status.

    Args:
        course_id: UUID string of the course to publish.
        db: An open async database session.

    Returns:
        The updated :class:`~src.models.Course`, or ``None`` if not found.

    Raises:
        :class:`fastapi.HTTPException` (409) if the course is already published.
    """
    course = await get_course(course_id, db)
    if course is None:
        return None
    if course.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course is already published.",
        )
    course.status = "published"
    course.updated_at = datetime.utcnow()
    await db.flush()
    logger.info("Course published: course_id=%s", sanitize_log(course_id))
    return course


async def unpublish_course(course_id: str, db: AsyncSession) -> Optional[Course]:
    """Transition a course from ``published`` back to ``draft`` status.

    Args:
        course_id: UUID string of the course to unpublish.
        db: An open async database session.

    Returns:
        The updated :class:`~src.models.Course`, or ``None`` if not found.

    Raises:
        :class:`fastapi.HTTPException` (409) if the course is already a draft.
    """
    course = await get_course(course_id, db)
    if course is None:
        return None
    if course.status == "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course is already in draft status.",
        )
    course.status = "draft"
    course.updated_at = datetime.utcnow()
    await db.flush()
    logger.info("Course unpublished: course_id=%s", sanitize_log(course_id))
    return course


async def list_courses(
    db: AsyncSession,
    status_filter: Optional[CourseStatus] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Course]:
    """List courses with optional status filtering and pagination.

    Args:
        db: An open async database session.
        status_filter: Optional status enum value to filter results.
        skip: Number of records to skip (pagination offset).
        limit: Maximum number of records to return.

    Returns:
        A list of :class:`~src.models.Course` instances.
    """
    stmt = select(Course).order_by(Course.created_at.desc()).offset(skip).limit(limit)
    if status_filter is not None:
        stmt = stmt.where(Course.status == status_filter.value)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_published_courses(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> list[Course]:
    """List all published courses, ordered by creation date descending.

    Args:
        db: An open async database session.
        skip: Number of records to skip (pagination offset).
        limit: Maximum number of records to return.

    Returns:
        A list of published :class:`~src.models.Course` instances.
    """
    return await list_courses(db, status_filter=CourseStatus.published, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Module helpers
# ---------------------------------------------------------------------------


async def create_module(
    course_id: str,
    module_in: ModuleCreate,
    db: AsyncSession,
) -> Module:
    """Create a new module within an existing course.

    Args:
        course_id: UUID string of the parent course.
        module_in: Validated request payload with module metadata.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.Module` ORM instance.

    Raises:
        :class:`fastapi.HTTPException` (404) if the parent course does not exist.
    """
    course = await get_course(course_id, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    module = Module(
        id=str(uuid.uuid4()),
        course_id=course_id,
        title=module_in.title,
        summary=module_in.summary,
        sort_order=module_in.sort_order,
        created_at=datetime.utcnow(),
    )
    db.add(module)
    await db.flush()
    return module


async def get_module(module_id: str, db: AsyncSession) -> Optional[Module]:
    """Retrieve a module by its primary key.

    Args:
        module_id: UUID string of the module.
        db: An open async database session.

    Returns:
        The :class:`~src.models.Module` instance, or ``None`` if not found.
    """
    result = await db.execute(select(Module).where(Module.id == module_id))
    return result.scalar_one_or_none()


async def list_modules(course_id: str, db: AsyncSession) -> list[Module]:
    """List all modules for a course, ordered by sort_order ascending.

    Args:
        course_id: UUID string of the parent course.
        db: An open async database session.

    Returns:
        Ordered list of :class:`~src.models.Module` instances.
    """
    result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.sort_order.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Lesson helpers
# ---------------------------------------------------------------------------


async def create_lesson(
    module_id: str,
    lesson_in: LessonCreate,
    db: AsyncSession,
) -> Lesson:
    """Create a new lesson within a module, sanitising Markdown content.

    The ``markdown_content`` field is passed through :func:`sanitise_markdown`
    before persistence to prevent XSS injection.

    Args:
        module_id: UUID string of the parent module.
        lesson_in: Validated request payload with lesson content.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.Lesson` ORM instance.

    Raises:
        :class:`fastapi.HTTPException` (404) if the parent module does not exist.
    """
    module = await get_module(module_id, db)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found.",
        )
    now = datetime.utcnow()
    lesson = Lesson(
        id=str(uuid.uuid4()),
        module_id=module_id,
        title=lesson_in.title,
        markdown_content=sanitise_markdown(lesson_in.markdown_content),
        estimated_minutes=lesson_in.estimated_minutes,
        sort_order=lesson_in.sort_order,
        created_at=now,
        updated_at=now,
    )
    db.add(lesson)
    await db.flush()
    return lesson


async def get_lesson(lesson_id: str, db: AsyncSession) -> Optional[Lesson]:
    """Retrieve a lesson by its primary key.

    Args:
        lesson_id: UUID string of the lesson.
        db: An open async database session.

    Returns:
        The :class:`~src.models.Lesson` instance, or ``None`` if not found.
    """
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    return result.scalar_one_or_none()


async def list_lessons(module_id: str, db: AsyncSession) -> list[Lesson]:
    """List all lessons in a module, ordered by sort_order ascending.

    Args:
        module_id: UUID string of the parent module.
        db: An open async database session.

    Returns:
        Ordered list of :class:`~src.models.Lesson` instances.
    """
    result = await db.execute(
        select(Lesson)
        .where(Lesson.module_id == module_id)
        .order_by(Lesson.sort_order.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# QuizQuestion helpers
# ---------------------------------------------------------------------------


async def create_quiz_question(
    module_id: str,
    question_in: QuizQuestionCreate,
    db: AsyncSession,
) -> QuizQuestion:
    """Create a new quiz question within a module.

    Args:
        module_id: UUID string of the parent module.
        question_in: Validated request payload with question data.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.QuizQuestion` ORM instance.

    Raises:
        :class:`fastapi.HTTPException` (404) if the parent module does not exist.
    """
    module = await get_module(module_id, db)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found.",
        )
    question = QuizQuestion(
        id=str(uuid.uuid4()),
        module_id=module_id,
        question=question_in.question,
        options=question_in.options,
        correct_answer=question_in.correct_answer,
        explanation=question_in.explanation,
        created_at=datetime.utcnow(),
    )
    db.add(question)
    await db.flush()
    return question


async def get_quiz_question(question_id: str, db: AsyncSession) -> Optional[QuizQuestion]:
    """Retrieve a quiz question by its primary key.

    Args:
        question_id: UUID string of the quiz question.
        db: An open async database session.

    Returns:
        The :class:`~src.models.QuizQuestion` instance, or ``None`` if not found.
    """
    result = await db.execute(select(QuizQuestion).where(QuizQuestion.id == question_id))
    return result.scalar_one_or_none()


async def get_course_with_modules(course_id: str, db: AsyncSession) -> Optional[Course]:
    """Retrieve a course with eagerly loaded modules, lessons, and quiz questions.

    Suitable for the course detail view — avoids N+1 queries.

    Args:
        course_id: UUID string of the course.
        db: An open async database session.

    Returns:
        The :class:`~src.models.Course` with nested relationships populated, or
        ``None`` if not found.
    """
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.modules).selectinload(Module.lessons),
            selectinload(Course.modules).selectinload(Module.quiz_questions),
        )
        .where(Course.id == course_id)
    )
    return result.scalar_one_or_none()
