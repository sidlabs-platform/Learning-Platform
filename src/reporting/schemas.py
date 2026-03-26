"""
Pydantic v2 schemas for the Reporting service.

Covers the admin dashboard aggregate statistics, per-course enrolment metrics,
per-learner progress statistics, and the CSV export configuration request.
"""

from enum import Enum

from pydantic import BaseModel


class ReportType(str, Enum):
    """
    Supported CSV export report types.

    ``enrollments``      — all enrolment records with timestamps and status.
    ``learner_progress`` — per-learner lesson/module completion breakdown.
    ``quiz_results``     — all quiz attempt records with correctness flags.
    """

    enrollments = "enrollments"
    learner_progress = "learner_progress"
    quiz_results = "quiz_results"


class EnrollmentStat(BaseModel):
    """
    Aggregate enrolment and completion statistics for a single course.

    Returned as part of :class:`AdminDashboardResponse`.
    """

    course_id: str
    course_title: str
    total_enrollments: int
    completed: int
    in_progress: int
    not_started: int
    completion_rate: float


class LearnerProgressStat(BaseModel):
    """
    Summary of a single learner's activity across all their enrolled courses.

    Used in the ``top_learners`` list of :class:`AdminDashboardResponse`.
    """

    user_id: str
    user_name: str
    user_email: str
    enrollments: int
    completed_courses: int
    in_progress_courses: int


class AdminDashboardResponse(BaseModel):
    """
    Top-level payload for ``GET /api/v1/reports/dashboard``.

    Aggregates platform-wide metrics and per-course/per-learner breakdowns
    for the admin reporting view.
    """

    total_users: int
    total_courses: int
    total_enrollments: int
    overall_completion_rate: float
    enrollment_stats: list[EnrollmentStat]
    top_learners: list[LearnerProgressStat]


class CSVExportRequest(BaseModel):
    """
    Request body for ``POST /api/v1/reports/export``.

    ``report_type`` determines which dataset is exported — see :class:`ReportType`
    for the full list of valid values.
    """

    report_type: ReportType = ReportType.enrollments


__all__ = [
    "ReportType",
    "EnrollmentStat",
    "LearnerProgressStat",
    "AdminDashboardResponse",
    "CSVExportRequest",
]
