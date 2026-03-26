"""
Pydantic v2 schemas for the Progress Tracking service.

Covers enrolment management, lesson progress records, quiz submissions/attempts,
and the aggregate course-progress summary used by the learner dashboard.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class EnrollmentStatus(str, Enum):
    """
    Lifecycle state of a learner's course enrolment.

    ``not_started``  — enrolled but no lessons viewed yet.
    ``in_progress``  — at least one lesson viewed or completed.
    ``completed``    — all lessons marked complete.
    """

    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


# ---------------------------------------------------------------------------
# Enrollment schemas
# ---------------------------------------------------------------------------


class EnrollmentCreate(BaseModel):
    """Request body for ``POST /api/v1/progress/enroll``."""

    course_id: str


class EnrollmentRead(BaseModel):
    """Enrolment record returned in API responses."""

    id: str
    user_id: str
    course_id: str
    enrolled_at: datetime
    status: EnrollmentStatus
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Progress record schemas
# ---------------------------------------------------------------------------


class ProgressRecordCreate(BaseModel):
    """
    Request body for recording a lesson view or completion.

    ``POST /api/v1/progress/lessons/{lesson_id}/complete``
    """

    lesson_id: str
    module_id: str


class ProgressRecordRead(BaseModel):
    """Lesson progress record returned in API responses."""

    id: str
    user_id: str
    lesson_id: str
    module_id: str
    completed: bool
    completed_at: datetime | None
    last_viewed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Quiz schemas
# ---------------------------------------------------------------------------


class QuizSubmission(BaseModel):
    """
    Request body for submitting a quiz answer.

    ``POST /api/v1/progress/quiz``
    """

    quiz_question_id: str
    selected_answer: str


class QuizAttemptRead(BaseModel):
    """Quiz attempt record returned in API responses."""

    id: str
    user_id: str
    quiz_question_id: str
    selected_answer: str
    is_correct: bool
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Aggregate progress summary
# ---------------------------------------------------------------------------


class CourseProgressSummary(BaseModel):
    """
    Aggregate progress statistics for a learner within a single course.

    Returned by ``GET /api/v1/progress/courses/{course_id}``.
    """

    course_id: str
    enrollment_status: EnrollmentStatus
    total_lessons: int
    completed_lessons: int
    progress_percentage: float


__all__ = [
    "EnrollmentStatus",
    "EnrollmentCreate",
    "EnrollmentRead",
    "ProgressRecordCreate",
    "ProgressRecordRead",
    "QuizSubmission",
    "QuizAttemptRead",
    "CourseProgressSummary",
]
