"""Enrollment service for the Learning Platform MVP.

Handles learner enrollment in courses, enrollment status transitions, and
enrollment queries.  Duplicate enrollment is detected via the unique
constraint on ``(user_id, course_id)`` and surfaced as an HTTP 400 error
before hitting the database.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Enrollment
from src.progress.schemas import EnrollmentStatus
from src.sanitize import sanitize_log

logger = logging.getLogger(__name__)


async def enroll_user(
    user_id: str,
    course_id: str,
    db: AsyncSession,
) -> Enrollment:
    """Enroll a user in a course.

    Creates a new :class:`~src.models.Enrollment` record with status
    ``not_started``.  Raises ``HTTP 400`` if the user is already enrolled to
    maintain idempotency-friendly semantics at the API layer.

    Args:
        user_id: UUID string of the user to enroll.
        course_id: UUID string of the course to enroll into.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.Enrollment` instance.

    Raises:
        :class:`fastapi.HTTPException` (400) if the user is already enrolled
        in this course.
    """
    # Check for existing enrollment before inserting to give a clear error.
    existing = await get_enrollment(user_id, course_id, db)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user_id}' is already enrolled in course '{course_id}'.",
        )

    enrollment = Enrollment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        course_id=course_id,
        enrolled_at=datetime.utcnow(),
        status="not_started",
        completed_at=None,
    )
    db.add(enrollment)
    await db.flush()
    logger.info(
        "User enrolled: enrollment_id=%s user_id=%s course_id=%s",
        sanitize_log(enrollment.id),
        sanitize_log(user_id),
        sanitize_log(course_id),
    )
    return enrollment


async def get_enrollment(
    user_id: str,
    course_id: str,
    db: AsyncSession,
) -> Optional[Enrollment]:
    """Retrieve the enrollment record for a specific user-course pair.

    Args:
        user_id: UUID string of the user.
        course_id: UUID string of the course.
        db: An open async database session.

    Returns:
        The :class:`~src.models.Enrollment` instance if it exists, otherwise ``None``.
    """
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
    )
    return result.scalar_one_or_none()


async def get_enrollment_by_id(
    enrollment_id: str,
    db: AsyncSession,
) -> Optional[Enrollment]:
    """Retrieve an enrollment record by its primary key.

    Args:
        enrollment_id: UUID string of the enrollment.
        db: An open async database session.

    Returns:
        The :class:`~src.models.Enrollment` instance, or ``None`` if not found.
    """
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    )
    return result.scalar_one_or_none()


async def get_user_enrollments(
    user_id: str,
    db: AsyncSession,
) -> list[Enrollment]:
    """Retrieve all enrollments for a given user.

    Args:
        user_id: UUID string of the user.
        db: An open async database session.

    Returns:
        List of :class:`~src.models.Enrollment` instances ordered by
        ``enrolled_at`` descending.
    """
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == user_id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    return list(result.scalars().all())


async def update_enrollment_status(
    enrollment_id: str,
    status_value: EnrollmentStatus,
    db: AsyncSession,
) -> Optional[Enrollment]:
    """Update the status of an enrollment record.

    Automatically sets ``completed_at`` when transitioning to
    ``EnrollmentStatus.completed``.

    Args:
        enrollment_id: UUID string of the enrollment to update.
        status_value: The new :class:`~src.progress.schemas.EnrollmentStatus`.
        db: An open async database session.

    Returns:
        The updated :class:`~src.models.Enrollment`, or ``None`` if not found.
    """
    enrollment = await get_enrollment_by_id(enrollment_id, db)
    if enrollment is None:
        return None

    enrollment.status = status_value.value
    if status_value == EnrollmentStatus.completed and enrollment.completed_at is None:
        enrollment.completed_at = datetime.utcnow()
    elif status_value != EnrollmentStatus.completed:
        enrollment.completed_at = None

    await db.flush()
    logger.info(
        "Enrollment status updated: enrollment_id=%s status=%s",
        enrollment_id,
        status_value.value,
    )
    return enrollment
