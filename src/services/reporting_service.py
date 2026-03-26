"""Reporting service — admin dashboard statistics and data export.

Provides read-only aggregate queries for admin reporting:

- :func:`get_dashboard_stats` — Collects enrollment stats, per-course breakdown,
  recent enrollments, and platform-wide totals for the admin dashboard.
- :func:`get_learner_report` — Per-learner enrollment and completion summary.
- :func:`export_enrollments_csv` — Full enrollment export as a CSV string for
  download by admins.

All functions are ``async`` and accept an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
as their first argument.  Progress percentages are calculated dynamically
as ``completed_lessons / total_lessons * 100`` for each enrollment.
"""

import csv
import io
import logging
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import (
    Course,
    CourseStatus,
    Enrollment,
    EnrollmentStatus,
    Lesson,
    Module,
    ProgressRecord,
    User,
)
from src.schemas.reporting import (
    CourseReportRow,
    DashboardResponse,
    EnrollmentStats,
    ExportRow,
    LearnerReportRow,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _count_total_lessons_for_course(db: AsyncSession, course_id: int) -> int:
    """Return the number of lessons belonging to a course across all modules.

    Args:
        db: Active async SQLAlchemy session.
        course_id: Primary key of the course.

    Returns:
        Integer lesson count (0 if course has no lessons).
    """
    stmt = (
        select(func.count(Lesson.id))
        .join(Module, Lesson.module_id == Module.id)
        .where(Module.course_id == course_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one() or 0


async def _count_completed_lessons_for_enrollment(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> int:
    """Return the number of lessons a learner has completed for a course.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        course_id: Primary key of the course.

    Returns:
        Integer count of completed progress records for lessons in the course.
    """
    stmt = (
        select(func.count(ProgressRecord.id))
        .join(Lesson, ProgressRecord.lesson_id == Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .where(
            Module.course_id == course_id,
            ProgressRecord.user_id == user_id,
            ProgressRecord.completed == True,  # noqa: E712
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one() or 0


async def _calc_progress_percentage(
    db: AsyncSession,
    user_id: int,
    course_id: int,
) -> float:
    """Calculate a learner's progress percentage for a single enrollment.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Learner primary key.
        course_id: Course primary key.

    Returns:
        A float between 0.0 and 100.0 (0.0 when course has no lessons).
    """
    total = await _count_total_lessons_for_course(db, course_id)
    if total == 0:
        return 0.0
    completed = await _count_completed_lessons_for_enrollment(db, user_id, course_id)
    return round(completed / total * 100, 2)


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------


async def get_dashboard_stats(db: AsyncSession) -> DashboardResponse:
    """Compute aggregate statistics for the admin dashboard.

    Queries include:
    - Total and published course counts.
    - Total user count.
    - Enrollment breakdown (total / active / completed).
    - Per-course enrollment and completion counts.
    - The 10 most recent enrollment events.

    Args:
        db: Active async SQLAlchemy session.

    Returns:
        A populated :class:`~src.schemas.reporting.DashboardResponse`.
    """
    # Total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users: int = total_users_result.scalar_one() or 0

    # Course counts
    total_courses_result = await db.execute(select(func.count(Course.id)))
    total_courses: int = total_courses_result.scalar_one() or 0

    published_courses_result = await db.execute(
        select(func.count(Course.id)).where(Course.status == CourseStatus.published)
    )
    published_courses: int = published_courses_result.scalar_one() or 0

    # Enrollment stats
    total_enrollments_result = await db.execute(select(func.count(Enrollment.id)))
    total_enrollments: int = total_enrollments_result.scalar_one() or 0

    active_result = await db.execute(
        select(func.count(Enrollment.id)).where(
            Enrollment.status == EnrollmentStatus.in_progress
        )
    )
    active_enrollments: int = active_result.scalar_one() or 0

    completed_result = await db.execute(
        select(func.count(Enrollment.id)).where(
            Enrollment.status == EnrollmentStatus.completed
        )
    )
    completed_enrollments: int = completed_result.scalar_one() or 0

    completion_rate = (
        round(completed_enrollments / total_enrollments, 4) if total_enrollments else 0.0
    )

    enrollment_stats = EnrollmentStats(
        total_enrollments=total_enrollments,
        active_enrollments=active_enrollments,
        completed_enrollments=completed_enrollments,
        completion_rate=completion_rate,
    )

    # Per-course breakdown
    courses_result = await db.execute(select(Course).order_by(Course.created_at.desc()))
    courses = list(courses_result.scalars().all())

    course_breakdown: list[CourseReportRow] = []
    for course in courses:
        enrolled_count_result = await db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id)
        )
        enrolled_count: int = enrolled_count_result.scalar_one() or 0

        completed_count_result = await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id == course.id,
                Enrollment.status == EnrollmentStatus.completed,
            )
        )
        completed_count: int = completed_count_result.scalar_one() or 0

        course_completion_rate = (
            round(completed_count / enrolled_count, 4) if enrolled_count else 0.0
        )

        # Average progress across all enrollments for this course
        enrollments_result = await db.execute(
            select(Enrollment).where(Enrollment.course_id == course.id)
        )
        course_enrollments = list(enrollments_result.scalars().all())
        if course_enrollments:
            progress_values = [
                await _calc_progress_percentage(db, e.user_id, course.id)
                for e in course_enrollments
            ]
            avg_progress = round(sum(progress_values) / len(progress_values), 2)
        else:
            avg_progress = 0.0

        course_breakdown.append(
            CourseReportRow(
                course_id=course.id,
                title=course.title,
                enrolled_count=enrolled_count,
                completed_count=completed_count,
                completion_rate=course_completion_rate,
                avg_progress_percentage=avg_progress,
            )
        )

    # Recent enrollments (last 10)
    recent_result = await db.execute(
        select(Enrollment, User, Course)
        .join(User, Enrollment.user_id == User.id)
        .join(Course, Enrollment.course_id == Course.id)
        .order_by(Enrollment.enrolled_at.desc())
        .limit(10)
    )
    recent_rows = recent_result.all()
    recent_enrollments = [
        {
            "enrollment_id": row.Enrollment.id,
            "user_id": row.User.id,
            "user_name": row.User.name,
            "course_id": row.Course.id,
            "course_title": row.Course.title,
            "enrolled_at": row.Enrollment.enrolled_at.isoformat(),
            "status": row.Enrollment.status.value,
        }
        for row in recent_rows
    ]

    logger.info(
        "Dashboard stats computed: total_users=%d total_courses=%d total_enrollments=%d",
        total_users,
        total_courses,
        total_enrollments,
    )

    return DashboardResponse(
        enrollment_stats=enrollment_stats,
        course_breakdown=course_breakdown,
        recent_enrollments=recent_enrollments,
        total_users=total_users,
        total_courses=total_courses,
        published_courses=published_courses,
    )


async def get_learner_report(db: AsyncSession) -> list[LearnerReportRow]:
    """Build a per-learner enrollment and completion summary.

    Args:
        db: Active async SQLAlchemy session.

    Returns:
        A list of :class:`~src.schemas.reporting.LearnerReportRow` instances,
        one per user (including users with zero enrollments).
    """
    users_result = await db.execute(select(User).order_by(User.name))
    users = list(users_result.scalars().all())

    rows: list[LearnerReportRow] = []
    for user in users:
        enrollments_result = await db.execute(
            select(Enrollment).where(Enrollment.user_id == user.id)
        )
        enrollments = list(enrollments_result.scalars().all())
        enrolled_courses = len(enrollments)
        completed_courses = sum(
            1 for e in enrollments if e.status == EnrollmentStatus.completed
        )

        # Last activity — most recent ProgressRecord.last_viewed_at
        last_active_result = await db.execute(
            select(func.max(ProgressRecord.last_viewed_at)).where(
                ProgressRecord.user_id == user.id
            )
        )
        last_active: datetime | None = last_active_result.scalar_one_or_none()

        rows.append(
            LearnerReportRow(
                user_id=user.id,
                name=user.name,
                email=user.email,
                enrolled_courses=enrolled_courses,
                completed_courses=completed_courses,
                last_active=last_active,
            )
        )

    logger.info("Learner report generated: %d learner rows", len(rows))
    return rows


async def export_enrollments_csv(db: AsyncSession) -> str:
    """Export all enrollment records as a CSV string.

    Columns: user_id, user_name, user_email, course_id, course_title,
    enrolled_at, status, progress_percentage.

    Progress percentage is computed dynamically from completed lesson records.

    Args:
        db: Active async SQLAlchemy session.

    Returns:
        A UTF-8 CSV string suitable for direct HTTP download.
    """
    result = await db.execute(
        select(Enrollment, User, Course)
        .join(User, Enrollment.user_id == User.id)
        .join(Course, Enrollment.course_id == Course.id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "user_id",
            "user_name",
            "user_email",
            "course_id",
            "course_title",
            "enrolled_at",
            "status",
            "progress_percentage",
        ]
    )

    for row in rows:
        enrollment: Enrollment = row.Enrollment
        user: User = row.User
        course: Course = row.Course
        progress_pct = await _calc_progress_percentage(db, user.id, course.id)
        writer.writerow(
            [
                user.id,
                user.name,
                user.email,
                course.id,
                course.title,
                enrollment.enrolled_at.isoformat(),
                enrollment.status.value,
                f"{progress_pct:.2f}",
            ]
        )

    csv_content = output.getvalue()
    logger.info("CSV export generated: %d enrollment rows", len(rows))
    return csv_content
