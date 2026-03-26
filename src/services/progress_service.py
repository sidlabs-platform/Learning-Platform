"""Progress tracking service — lesson views, completions, and aggregated progress.

Provides all database-backed operations for tracking learner progress:

- Recording that a user viewed a lesson (upsert on ``ProgressRecord``).
- Marking a lesson as completed.
- Fetching the raw progress record for a user/lesson pair.
- Computing aggregated progress percentages at module and course level.

Progress is stored per-lesson in :class:`~src.models.ProgressRecord` rows.
Aggregate progress is derived on the fly by counting completed lessons and
dividing by total lessons in the relevant scope.

All functions are ``async`` and accept an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
as their first argument.  Business-logic errors are surfaced as
:class:`~fastapi.HTTPException` instances.
"""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Enrollment, EnrollmentStatus, Lesson, Module, ProgressRecord
from src.schemas.progress import CourseProgressResponse, ModuleProgressResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _get_or_create_progress_record(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    module_id: int,
) -> ProgressRecord:
    """Fetch an existing progress record or create a new one.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        lesson_id: Primary key of the lesson.
        module_id: Primary key of the containing module.

    Returns:
        The existing or newly created ``ProgressRecord`` ORM instance.
    """
    result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.lesson_id == lesson_id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = ProgressRecord(
            user_id=user_id,
            lesson_id=lesson_id,
            module_id=module_id,
            completed=False,
            last_viewed_at=datetime.now(timezone.utc),
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------


async def record_lesson_view(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    module_id: int,
) -> ProgressRecord:
    """Record that a user viewed a lesson.

    Creates a new ``ProgressRecord`` on first view, or updates
    ``last_viewed_at`` if one already exists.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        lesson_id: Primary key of the viewed lesson.
        module_id: Primary key of the containing module.

    Returns:
        The created or updated ``ProgressRecord`` ORM instance.
    """
    record = await _get_or_create_progress_record(db, user_id, lesson_id, module_id)
    record.last_viewed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(record)
    logger.info(
        "Lesson view recorded: user_id=%d lesson_id=%d", user_id, lesson_id
    )
    return record


async def complete_lesson(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    module_id: int,
) -> ProgressRecord:
    """Mark a lesson as completed by the learner.

    Sets ``completed=True`` and records ``completed_at`` with the current UTC
    timestamp.  If the lesson was already marked complete, the completion
    timestamp is preserved (idempotent).

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        lesson_id: Primary key of the lesson to mark complete.
        module_id: Primary key of the containing module.

    Returns:
        The updated ``ProgressRecord`` ORM instance.
    """
    record = await _get_or_create_progress_record(db, user_id, lesson_id, module_id)
    now = datetime.now(timezone.utc)
    record.last_viewed_at = now
    if not record.completed:
        record.completed = True
        record.completed_at = now
    await db.flush()
    await db.refresh(record)
    logger.info(
        "Lesson completed: user_id=%d lesson_id=%d", user_id, lesson_id
    )
    return record


async def get_lesson_progress(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
) -> ProgressRecord | None:
    """Retrieve the progress record for a user/lesson pair.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        lesson_id: Primary key of the lesson.

    Returns:
        The matching ``ProgressRecord``, or ``None`` if the lesson has never
        been viewed.
    """
    result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.lesson_id == lesson_id,
        )
    )
    return result.scalar_one_or_none()


async def get_module_progress(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> ModuleProgressResponse:
    """Calculate the learner's aggregated progress within a single module.

    Counts the total number of lessons in the module and how many the user
    has completed to derive a progress percentage.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        module_id: Primary key of the module.

    Returns:
        :class:`~src.schemas.progress.ModuleProgressResponse` with totals and
        a ``progress_percentage`` in the range ``[0.0, 100.0]``.

    Raises:
        HTTPException: 404 Not Found if the module does not exist.
    """
    # Verify module exists
    module_result = await db.execute(select(Module).where(Module.id == module_id))
    if module_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} not found",
        )

    # Total lessons in this module
    lessons_result = await db.execute(
        select(Lesson).where(Lesson.module_id == module_id)
    )
    total_lessons = len(lessons_result.scalars().all())

    # Completed lessons for this user in this module
    completed_result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.module_id == module_id,
            ProgressRecord.completed.is_(True),
        )
    )
    completed_lessons = len(completed_result.scalars().all())

    progress_pct = (completed_lessons / total_lessons * 100.0) if total_lessons > 0 else 0.0

    return ModuleProgressResponse(
        module_id=module_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percentage=round(progress_pct, 2),
    )


async def get_course_progress(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> CourseProgressResponse:
    """Calculate the learner's aggregated progress across an entire course.

    Retrieves all modules and lessons in the course, counts the user's
    completed lessons, and computes a percentage.  Also returns a per-module
    breakdown for detailed progress views.

    The enrollment record's status is included in the response; the status
    is automatically advanced from ``not_started`` → ``in_progress`` when at
    least one lesson has been completed.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        course_id: Primary key of the course.

    Returns:
        :class:`~src.schemas.progress.CourseProgressResponse` with overall
        totals, a progress percentage, and per-module breakdowns.

    Raises:
        HTTPException: 404 Not Found if the user is not enrolled in the course.
    """
    # Verify enrollment exists
    enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} is not enrolled in course {course_id}",
        )

    # Fetch all modules for the course
    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.sort_order.asc())
    )
    modules = list(modules_result.scalars().all())

    if not modules:
        return CourseProgressResponse(
            course_id=course_id,
            enrollment_status=enrollment.status,
            total_lessons=0,
            completed_lessons=0,
            progress_percentage=0.0,
            module_progress=[],
        )

    module_ids = [m.id for m in modules]

    # Fetch all lessons in the course
    all_lessons_result = await db.execute(
        select(Lesson).where(Lesson.module_id.in_(module_ids))
    )
    all_lessons = list(all_lessons_result.scalars().all())
    total_lessons = len(all_lessons)

    # Fetch all completed progress records for this user in this course
    completed_records_result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.module_id.in_(module_ids),
            ProgressRecord.completed.is_(True),
        )
    )
    completed_records = list(completed_records_result.scalars().all())
    completed_lessons = len(completed_records)

    # Build set of (module_id → completed lesson IDs) for per-module breakdown
    completed_by_module: dict[int, int] = {}
    for rec in completed_records:
        completed_by_module[rec.module_id] = completed_by_module.get(rec.module_id, 0) + 1

    # Count lessons per module
    lessons_by_module: dict[int, int] = {}
    for lesson in all_lessons:
        lessons_by_module[lesson.module_id] = lessons_by_module.get(lesson.module_id, 0) + 1

    # Build per-module progress
    module_progress: list[ModuleProgressResponse] = []
    for module in modules:
        mod_total = lessons_by_module.get(module.id, 0)
        mod_completed = completed_by_module.get(module.id, 0)
        mod_pct = (mod_completed / mod_total * 100.0) if mod_total > 0 else 0.0
        module_progress.append(
            ModuleProgressResponse(
                module_id=module.id,
                total_lessons=mod_total,
                completed_lessons=mod_completed,
                progress_percentage=round(mod_pct, 2),
            )
        )

    # Compute overall progress percentage
    overall_pct = (completed_lessons / total_lessons * 100.0) if total_lessons > 0 else 0.0

    # Auto-advance enrollment status if progress has been made
    if completed_lessons > 0 and enrollment.status == EnrollmentStatus.not_started:
        enrollment.status = EnrollmentStatus.in_progress
        await db.flush()
        await db.refresh(enrollment)
        logger.info(
            "Enrollment status advanced to in_progress: user_id=%d course_id=%d",
            user_id,
            course_id,
        )
    if total_lessons > 0 and completed_lessons == total_lessons:
        enrollment.status = EnrollmentStatus.completed
        await db.flush()
        await db.refresh(enrollment)
        logger.info(
            "Enrollment completed: user_id=%d course_id=%d",
            user_id,
            course_id,
        )

    return CourseProgressResponse(
        course_id=course_id,
        enrollment_status=enrollment.status,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percentage=round(overall_pct, 2),
        module_progress=module_progress,
    )
