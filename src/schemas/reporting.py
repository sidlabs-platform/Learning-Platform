"""Pydantic v2 schemas for admin reporting.

Covers:
- Enrollment statistics summary
- Per-course report rows
- Per-learner report rows
- Admin dashboard aggregation response
- CSV/export row representation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class EnrollmentStats(BaseModel):
    """High-level enrollment statistics across all courses."""

    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    completion_rate: float  # value between 0.0 and 1.0


class CourseReportRow(BaseModel):
    """Enrollment and completion metrics for a single course."""

    course_id: int
    title: str
    enrolled_count: int
    completed_count: int
    completion_rate: float
    avg_progress_percentage: float


class LearnerReportRow(BaseModel):
    """Enrollment and activity metrics for a single learner."""

    user_id: int
    name: str
    email: str
    enrolled_courses: int
    completed_courses: int
    last_active: Optional[datetime] = None


class DashboardResponse(BaseModel):
    """Aggregated data for the admin dashboard overview page."""

    enrollment_stats: EnrollmentStats
    course_breakdown: List[CourseReportRow]
    recent_enrollments: List[Dict[str, Any]]  # lightweight, arbitrary shape
    total_users: int
    total_courses: int
    published_courses: int


class ExportRow(BaseModel):
    """Flat row used for CSV / data-export of enrollment records."""

    user_id: int
    user_name: str
    user_email: str
    course_id: int
    course_title: str
    enrolled_at: datetime
    status: str
    progress_percentage: float
