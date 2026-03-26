"""
Pydantic v2 schemas for the Course Management service.

Covers the full CRUD surface for Courses, Modules, Lessons, and Quiz Questions.
Validation helpers ensure domain invariants (e.g. ``correct_answer`` must be one
of the provided ``options``) are enforced at the schema layer before data reaches
the service or database.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class CourseStatus(str, Enum):
    """Publication state of a course."""

    draft = "draft"
    published = "published"


class DifficultyLevel(str, Enum):
    """Target skill level of a course."""

    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


# ---------------------------------------------------------------------------
# Course schemas
# ---------------------------------------------------------------------------


class CourseCreate(BaseModel):
    """
    Request body for ``POST /api/v1/courses``.

    New courses always start in ``draft`` status.
    """

    title: str
    description: str
    difficulty: DifficultyLevel
    estimated_duration: int
    tags: list[str] = []


class CourseUpdate(BaseModel):
    """
    Request body for ``PATCH /api/v1/courses/{course_id}``.

    All fields are optional to support partial updates.
    """

    title: str | None = None
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    estimated_duration: int | None = None
    tags: list[str] | None = None


class CourseRead(BaseModel):
    """
    Full course representation returned in API responses.

    ``created_by`` is the UUID string of the admin who created the course.
    """

    id: str
    title: str
    description: str
    status: CourseStatus
    difficulty: DifficultyLevel
    estimated_duration: int
    tags: list[str]
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Module schemas
# ---------------------------------------------------------------------------


class ModuleCreate(BaseModel):
    """Request body for ``POST /api/v1/courses/{course_id}/modules``."""

    title: str
    summary: str
    sort_order: int


class ModuleRead(BaseModel):
    """Module representation returned in API responses."""

    id: str
    course_id: str
    title: str
    summary: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Lesson schemas
# ---------------------------------------------------------------------------


class LessonCreate(BaseModel):
    """Request body for ``POST /api/v1/courses/{course_id}/modules/{module_id}/lessons``."""

    title: str
    markdown_content: str
    estimated_minutes: int
    sort_order: int


class LessonRead(BaseModel):
    """Lesson representation returned in API responses."""

    id: str
    module_id: str
    title: str
    markdown_content: str
    estimated_minutes: int
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Quiz Question schemas
# ---------------------------------------------------------------------------


class QuizQuestionCreate(BaseModel):
    """
    Request body for creating a new quiz question within a module.

    Validation ensures that ``correct_answer`` is one of the provided
    ``options`` so that learners can always select the correct answer.
    """

    question: str
    options: list[str]
    correct_answer: str
    explanation: str

    @field_validator("correct_answer")
    @classmethod
    def correct_must_be_in_options(cls, v: str, info) -> str:
        """Raise ``ValueError`` when ``correct_answer`` is not in ``options``."""
        options = info.data.get("options", [])
        if options and v not in options:
            raise ValueError(
                f"correct_answer '{v}' must be one of the provided options: {options}"
            )
        return v


class QuizQuestionRead(BaseModel):
    """Quiz question representation returned in API responses."""

    id: str
    module_id: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "CourseStatus",
    "DifficultyLevel",
    "CourseCreate",
    "CourseUpdate",
    "CourseRead",
    "ModuleCreate",
    "ModuleRead",
    "LessonCreate",
    "LessonRead",
    "QuizQuestionCreate",
    "QuizQuestionRead",
]
