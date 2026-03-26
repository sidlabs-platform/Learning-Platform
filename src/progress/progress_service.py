"""
Progress recording service for the Learning Platform MVP.

Handles lesson view tracking, lesson completion, and course progress summaries.
Uses upsert-style logic (SELECT then INSERT/UPDATE) for idempotent progress recording.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Enrollment, Lesson, Module, ProgressRecord
from src.progress.schemas import CourseProgressSummary, EnrollmentStatus

logger = logging.getLogger(__name__)


async def record_lesson_view(
    user_id: str,
    lesson_id: str,
    module_id: str,
    db: AsyncSession,
) -> ProgressRecord:
    """Record or update a lesson view for a learner.

    Uses an upsert pattern: if a :class:`~src.models.ProgressRecord` already
    exists for the ``(user_id, lesson_id)`` pair it is updated with the current
    timestamp; otherwise a new record is created.

    Args:
        user_id: UUID string of the learner.
        lesson_id: UUID string of the lesson being viewed.
        module_id: UUID string of the parent module (stored denormalised).
        db: An open async database session.

    Returns:
        The created or updated :class:`~src.models.ProgressRecord`.
    """
    result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.lesson_id == lesson_id,
        )
    )
    record: Optional[ProgressRecord] = result.scalars().first()

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if record is not None:
        record.last_viewed_at = now
    else:
        record = ProgressRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            lesson_id=lesson_id,
            module_id=module_id,
            completed=False,
            completed_at=None,
            last_viewed_at=now,
        )
        db.add(record)

    await db.flush()
    await db.refresh(record)
    logger.info("Recorded lesson view for user %s, lesson %s", user_id, lesson_id)
    return record


async def complete_lesson(
    user_id: str,
    lesson_id: str,
    db: AsyncSession,
) -> ProgressRecord:
    """Mark a lesson as completed for a learner.

    If no :class:`~src.models.ProgressRecord` exists yet, a new one is created
    with ``completed=True``.  The ``completed_at`` timestamp is only set once
    (on first completion).

    Args:
        user_id: UUID string of the learner.
        lesson_id: UUID string of the lesson to complete.
        db: An open async database session.

    Returns:
        The updated or created :class:`~src.models.ProgressRecord`.
    """
    result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.lesson_id == lesson_id,
        )
    )
    record: Optional[ProgressRecord] = result.scalars().first()

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if record is not None:
        record.last_viewed_at = now
        if not record.completed:
            record.completed = True
            record.completed_at = now
    else:
        # Need the module_id — fetch from lesson row
        lesson_result = await db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        lesson = lesson_result.scalars().first()
        module_id = lesson.module_id if lesson is not None else ""

        record = ProgressRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            lesson_id=lesson_id,
            module_id=module_id,
            completed=True,
            completed_at=now,
            last_viewed_at=now,
        )
        db.add(record)

    await db.flush()
    await db.refresh(record)
    logger.info("Completed lesson %s for user %s", lesson_id, user_id)
    return record


async def get_lesson_progress(
    user_id: str,
    lesson_id: str,
    db: AsyncSession,
) -> Optional[ProgressRecord]:
    """Retrieve a learner's progress record for a specific lesson.

    Args:
        user_id: UUID string of the learner.
        lesson_id: UUID string of the lesson.
        db: An open async database session.

    Returns:
        The :class:`~src.models.ProgressRecord` or ``None`` if the lesson has
        not been viewed.
    """
    result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.lesson_id == lesson_id,
        )
    )
    return result.scalars().first()


async def get_module_progress(
    user_id: str,
    module_id: str,
    db: AsyncSession,
) -> list[ProgressRecord]:
    """Retrieve all progress records for a learner within a module.

    Args:
        user_id: UUID string of the learner.
        module_id: UUID string of the module.
        db: An open async database session.

    Returns:
        List of :class:`~src.models.ProgressRecord` instances for the module.
    """
    result = await db.execute(
        select(ProgressRecord).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.module_id == module_id,
        )
    )
    return list(result.scalars().all())


async def get_course_progress_summary(
    user_id: str,
    course_id: str,
    db: AsyncSession,
) -> CourseProgressSummary:
    """Calculate an aggregate progress summary for a learner within a course.

    Counts all lessons across every module in the course, then counts how many
    have been marked completed by the learner.  Also reads the current
    enrolment status.

    Args:
        user_id: UUID string of the learner.
        course_id: UUID string of the course.
        db: An open async database session.

    Returns:
        A :class:`~src.progress.schemas.CourseProgressSummary` with totals and
        percentage.
    """
    # Count total lessons in the course via module join
    total_result = await db.execute(
        select(func.count(Lesson.id))
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.course_id == course_id)
    )
    total_lessons: int = total_result.scalar_one() or 0

    # Count completed lessons for this user in the course
    completed_result = await db.execute(
        select(func.count(ProgressRecord.id))
        .join(Lesson, Lesson.id == ProgressRecord.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(
            Module.course_id == course_id,
            ProgressRecord.user_id == user_id,
            ProgressRecord.completed.is_(True),
        )
    )
    completed_lessons: int = completed_result.scalar_one() or 0

    # Get enrollment status
    enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
    )
    enrollment = enrollment_result.scalars().first()
    enrollment_status = (
        EnrollmentStatus(enrollment.status) if enrollment is not None
        else EnrollmentStatus.not_started
    )

    progress_percentage = (
        (completed_lessons / total_lessons * 100.0) if total_lessons > 0 else 0.0
    )

    return CourseProgressSummary(
        course_id=course_id,
        enrollment_status=enrollment_status,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percentage=round(progress_percentage, 2),
    )


__all__ = [
    "record_lesson_view",
    "complete_lesson",
    "get_lesson_progress",
    "get_module_progress",
    "get_course_progress_summary",
]
