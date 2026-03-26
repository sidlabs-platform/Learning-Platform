"""Reporting service for the Learning Platform MVP.

Provides aggregate dashboard statistics and CSV export functions for the
admin reporting view.  All queries use SQLAlchemy ``func.count`` and
``group_by`` for efficient server-side aggregation.

CSV exports use Python's built-in ``csv`` module — no external libraries
are required.
"""

import csv
import io
import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Course, Enrollment, User
from src.reporting.schemas import (
    AdminDashboardResponse,
    EnrollmentStat,
    LearnerProgressStat,
)

logger = logging.getLogger(__name__)


async def get_admin_dashboard(db: AsyncSession) -> AdminDashboardResponse:
    """Build the top-level admin dashboard metrics.

    Aggregates platform-wide statistics including total user/course/enrollment
    counts, overall completion rate, per-course enrollment stats, and a list
    of learner progress summaries.

    Args:
        db: An open async database session.

    Returns:
        A populated :class:`~src.reporting.schemas.AdminDashboardResponse`.
    """
    total_users = await db.scalar(
        select(func.count(User.id)).where(User.role == "learner")
    ) or 0

    total_courses = await db.scalar(select(func.count(Course.id))) or 0

    total_enrollments = await db.scalar(select(func.count(Enrollment.id))) or 0

    completed_enrollments = await db.scalar(
        select(func.count(Enrollment.id)).where(Enrollment.status == "completed")
    ) or 0

    overall_completion_rate = (
        round(completed_enrollments / total_enrollments * 100, 2)
        if total_enrollments > 0
        else 0.0
    )

    enrollment_stats = await get_enrollment_stats(db)
    top_learners = await get_learner_progress_stats(db)

    logger.info(
        "Admin dashboard built: users=%d courses=%d enrollments=%d",
        total_users,
        total_courses,
        total_enrollments,
    )

    return AdminDashboardResponse(
        total_users=total_users,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        overall_completion_rate=overall_completion_rate,
        enrollment_stats=enrollment_stats,
        top_learners=top_learners,
    )


async def get_enrollment_stats(db: AsyncSession) -> list[EnrollmentStat]:
    """Compute per-course enrollment and completion statistics.

    Performs a single aggregation query that groups enrollment counts by
    ``(course_id, status)`` and joins with the courses table for the title.

    Args:
        db: An open async database session.

    Returns:
        A list of :class:`~src.reporting.schemas.EnrollmentStat` instances,
        one per course that has at least one enrollment.
    """
    # Aggregate enrollments by course and status in one pass.
    stmt = (
        select(
            Course.id.label("course_id"),
            Course.title.label("course_title"),
            func.count(Enrollment.id).label("total"),
            func.sum(
                func.cast(Enrollment.status == "completed", func.count().type)
            ).label("completed_count"),
            func.sum(
                func.cast(Enrollment.status == "in_progress", func.count().type)
            ).label("in_progress_count"),
            func.sum(
                func.cast(Enrollment.status == "not_started", func.count().type)
            ).label("not_started_count"),
        )
        .join(Enrollment, Enrollment.course_id == Course.id, isouter=True)
        .group_by(Course.id, Course.title)
    )
    rows = (await db.execute(stmt)).all()

    stats: list[EnrollmentStat] = []
    for row in rows:
        course_id, course_title, total, completed, in_progress, not_started = row
        total = total or 0
        completed = int(completed or 0)
        in_progress = int(in_progress or 0)
        not_started = int(not_started or 0)
        completion_rate = round(completed / total * 100, 2) if total > 0 else 0.0
        stats.append(
            EnrollmentStat(
                course_id=course_id,
                course_title=course_title,
                total_enrollments=total,
                completed=completed,
                in_progress=in_progress,
                not_started=not_started,
                completion_rate=completion_rate,
            )
        )

    return stats


async def get_learner_progress_stats(db: AsyncSession) -> list[LearnerProgressStat]:
    """Compute per-learner enrollment summary statistics.

    Returns a list of learner activity summaries including total enrollments
    and counts broken down by completion status.

    Args:
        db: An open async database session.

    Returns:
        A list of :class:`~src.reporting.schemas.LearnerProgressStat` instances.
    """
    stmt = (
        select(
            User.id.label("user_id"),
            User.name.label("user_name"),
            User.email.label("user_email"),
            func.count(Enrollment.id).label("enrollments"),
        )
        .join(Enrollment, Enrollment.user_id == User.id, isouter=True)
        .where(User.role == "learner")
        .group_by(User.id, User.name, User.email)
        .order_by(func.count(Enrollment.id).desc())
    )
    rows = (await db.execute(stmt)).all()

    # Second pass: count completed and in-progress per user.
    # We fetch all enrollments grouped by user_id and status.
    status_stmt = select(
        Enrollment.user_id,
        Enrollment.status,
        func.count(Enrollment.id).label("cnt"),
    ).group_by(Enrollment.user_id, Enrollment.status)
    status_rows = (await db.execute(status_stmt)).all()

    # Build lookup: {user_id: {status: count}}
    status_map: dict[str, dict[str, int]] = {}
    for user_id, enrollment_status, cnt in status_rows:
        if user_id not in status_map:
            status_map[user_id] = {}
        status_map[user_id][enrollment_status] = cnt

    learner_stats: list[LearnerProgressStat] = []
    for row in rows:
        user_id, user_name, user_email, enrollments = row
        user_statuses = status_map.get(user_id, {})
        learner_stats.append(
            LearnerProgressStat(
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                enrollments=enrollments or 0,
                completed_courses=user_statuses.get("completed", 0),
                in_progress_courses=user_statuses.get("in_progress", 0),
            )
        )

    return learner_stats


async def export_enrollments_csv(db: AsyncSession) -> str:
    """Generate a CSV string containing all enrollment records.

    Joins enrollments with users and courses to include human-readable names
    alongside IDs.  Uses Python's built-in ``csv`` module.

    Args:
        db: An open async database session.

    Returns:
        A UTF-8 CSV string with a header row followed by one data row per
        enrollment.  Returns a headers-only CSV when there are no enrollments.
    """
    stmt = (
        select(Enrollment, User, Course)
        .join(User, Enrollment.user_id == User.id)
        .join(Course, Enrollment.course_id == Course.id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["enrollment_id", "user_id", "user_name", "user_email",
         "course_id", "course_title", "status", "enrolled_at", "completed_at"]
    )
    for enrollment, user, course in rows:
        writer.writerow([
            enrollment.id,
            user.id,
            user.name,
            user.email,
            course.id,
            course.title,
            enrollment.status,
            enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else "",
            enrollment.completed_at.isoformat() if enrollment.completed_at else "",
        ])

    return output.getvalue()


async def export_learner_progress_csv(db: AsyncSession) -> str:
    """Generate a CSV string containing per-learner progress summaries.

    Aggregates enrollment counts per user broken down by status.

    Args:
        db: An open async database session.

    Returns:
        A UTF-8 CSV string with a header row followed by one row per learner.
        Returns a headers-only CSV when there are no learner records.
    """
    learner_stats = await get_learner_progress_stats(db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["user_id", "user_name", "user_email",
         "total_enrollments", "completed_courses", "in_progress_courses"]
    )
    for stat in learner_stats:
        writer.writerow([
            stat.user_id,
            stat.user_name,
            stat.user_email,
            stat.enrollments,
            stat.completed_courses,
            stat.in_progress_courses,
        ])

    return output.getvalue()
