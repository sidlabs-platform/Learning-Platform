"""Completion service — auto-completion and enrollment status state machine.

Provides functions that check and update a learner's enrollment status
based on their lesson completion progress.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Enrollment, EnrollmentStatus, Lesson, Module, ProgressRecord
from src.services.enrollment_service import update_enrollment_status

logger = logging.getLogger(__name__)


async def check_and_update_completion(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> bool:
    """Check if a user has completed all lessons in a course.

    If all lessons are completed, mark enrollment as 'completed'.
    If any lesson is completed (progress > 0%), ensure status is 'in_progress'.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        course_id: Primary key of the course.

    Returns:
        True if course is now fully completed, False otherwise.
    """
    # Get all lessons in the course
    total_result = await db.execute(
        select(func.count(Lesson.id))
        .join(Module, Lesson.module_id == Module.id)
        .where(Module.course_id == course_id)
    )
    total_lessons = total_result.scalar() or 0

    if total_lessons == 0:
        return False

    # Get completed lessons count
    completed_result = await db.execute(
        select(func.count(ProgressRecord.id))
        .join(Lesson, ProgressRecord.lesson_id == Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .where(
            ProgressRecord.user_id == user_id,
            Module.course_id == course_id,
            ProgressRecord.completed == True,  # noqa: E712
        )
    )
    completed_lessons = completed_result.scalar() or 0

    if completed_lessons >= total_lessons:
        await update_enrollment_status(db, user_id, course_id, EnrollmentStatus.completed)
        logger.info(
            "Course %d marked completed for user %d (%d/%d lessons)",
            course_id, user_id, completed_lessons, total_lessons,
        )
        return True

    if completed_lessons > 0:
        # Ensure status is at least in_progress
        enrollment_result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if enrollment and enrollment.status == EnrollmentStatus.not_started:
            await update_enrollment_status(db, user_id, course_id, EnrollmentStatus.in_progress)

    return False


async def check_module_completion(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> bool:
    """Check if user has completed all lessons in a module.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        module_id: Primary key of the module.

    Returns:
        True if module is fully completed, False otherwise.
    """
    total_result = await db.execute(
        select(func.count(Lesson.id)).where(Lesson.module_id == module_id)
    )
    total_lessons = total_result.scalar() or 0

    if total_lessons == 0:
        return False

    completed_result = await db.execute(
        select(func.count(ProgressRecord.id)).where(
            ProgressRecord.user_id == user_id,
            ProgressRecord.module_id == module_id,
            ProgressRecord.completed == True,  # noqa: E712
        )
    )
    completed_lessons = completed_result.scalar() or 0

    return completed_lessons >= total_lessons


async def update_enrollment_on_progress(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> None:
    """Update enrollment status after each lesson completion.

    Transitions: not_started -> in_progress -> completed.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        course_id: Primary key of the course.
    """
    await check_and_update_completion(db, user_id, course_id)
