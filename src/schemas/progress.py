"""Pydantic v2 schemas for progress tracking.

Covers:
- Course enrollment (request + response)
- Lesson-level progress updates and responses
- Quiz submission and attempt responses
- Aggregated course and module progress responses
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class EnrollmentStatus(str, Enum):
    """Progress status of a learner's enrollment in a course."""

    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


# ---------------------------------------------------------------------------
# Enrollment schemas
# ---------------------------------------------------------------------------


class EnrollRequest(BaseModel):
    """Request body for enrolling the current user in a course."""

    course_id: int


class EnrollmentResponse(BaseModel):
    """Enrollment record returned by API endpoints."""

    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    status: EnrollmentStatus

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Lesson progress schemas
# ---------------------------------------------------------------------------


class LessonProgressUpdate(BaseModel):
    """Request body for recording a learner's progress on a lesson."""

    lesson_id: int
    module_id: int
    completed: bool = False


class LessonProgressResponse(BaseModel):
    """Progress record for a single lesson returned by API endpoints."""

    id: int
    user_id: int
    lesson_id: int
    module_id: int
    completed: bool
    completed_at: Optional[datetime] = None
    last_viewed_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Quiz schemas
# ---------------------------------------------------------------------------


class QuizSubmission(BaseModel):
    """Request body for submitting an answer to a quiz question."""

    quiz_question_id: int
    selected_answer: str = Field(min_length=1)


class QuizAttemptResponse(BaseModel):
    """Quiz attempt record returned by API endpoints."""

    id: int
    user_id: int
    quiz_question_id: int
    selected_answer: str
    is_correct: bool
    attempted_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Aggregated progress schemas
# ---------------------------------------------------------------------------


class ModuleProgressResponse(BaseModel):
    """Aggregated progress summary for a single module."""

    module_id: int
    total_lessons: int
    completed_lessons: int
    progress_percentage: float

    model_config = {"from_attributes": True}


class CourseProgressResponse(BaseModel):
    """Aggregated progress summary for a course enrollment."""

    course_id: int
    enrollment_status: EnrollmentStatus
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    module_progress: List[ModuleProgressResponse] = []

    model_config = {"from_attributes": True}
