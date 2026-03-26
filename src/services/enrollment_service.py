"""Enrollment service — managing learner course enrollments.

Provides all database-backed operations for enrollment management:

- Enrolling a user in a course (with duplicate and 404 guards).
- Fetching a specific enrollment record.
- Listing all enrollments for a user.
- Updating the status of an enrollment.

All functions are ``async`` and accept an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
as their first argument.  Business-logic errors are surfaced as
:class:`~fastapi.HTTPException` instances.
"""

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Course, Enrollment, EnrollmentStatus

logger = logging.getLogger(__name__)


async def enroll_user(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> Enrollment:
    """Enroll a user in a course.

    Validates that the target course exists and that the user is not already
    enrolled before creating the enrollment record.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the user to enroll.
        course_id: Primary key of the course to enroll the user in.

    Returns:
        The newly created ``Enrollment`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if the course does not exist.
        HTTPException: 409 Conflict if the user is already enrolled in the
            course.
    """
    # Verify course exists
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found",
        )

    # Check for duplicate enrollment
    existing = await get_enrollment(db, user_id, course_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already enrolled in this course",
        )

    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        status=EnrollmentStatus.not_started,
    )
    db.add(enrollment)
    await db.flush()
    await db.refresh(enrollment)
    logger.info(
        "User enrolled: user_id=%d course_id=%d enrollment_id=%d",
        user_id,
        course_id,
        enrollment.id,
    )
    return enrollment


async def get_enrollment(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> Optional[Enrollment]:
    """Fetch the enrollment record for a specific user/course pair.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the user.
        course_id: Primary key of the course.

    Returns:
        The matching ``Enrollment`` ORM instance, or ``None`` if not found.
    """
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
    )
    return result.scalar_one_or_none()


async def list_user_enrollments(
    db: AsyncSession,
    user_id: int,
) -> list[Enrollment]:
    """Fetch all enrollment records for a given user.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the user whose enrollments to retrieve.

    Returns:
        A list of ``Enrollment`` ORM instances (may be empty).
    """
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == user_id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    return list(result.scalars().all())


async def update_enrollment_status(
    db: AsyncSession,
    enrollment_id: int,
    new_status: EnrollmentStatus,
) -> Enrollment:
    """Update the status of an enrollment record.

    Args:
        db: Active async SQLAlchemy session.
        enrollment_id: Primary key of the enrollment to update.
        new_status: The new :class:`~src.models.EnrollmentStatus` value.

    Returns:
        The updated ``Enrollment`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no enrollment with the given ID exists.
    """
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    )
    enrollment = result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment {enrollment_id} not found",
        )
    old_status = enrollment.status
    enrollment.status = new_status
    await db.flush()
    await db.refresh(enrollment)
    logger.info(
        "Enrollment status updated: id=%d %s -> %s",
        enrollment_id,
        old_status,
        new_status,
    )
    return enrollment
