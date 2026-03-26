"""Pydantic v2 schemas for course management.

Covers:
- Course CRUD (create / update / response)
- Module CRUD
- Lesson CRUD (with sanitised HTML content)
- Quiz question CRUD
- Nested detail and catalog responses
- Paginated list responses
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CourseStatus(str, Enum):
    """Publication status of a course."""

    draft = "draft"
    published = "published"


class CourseDifficulty(str, Enum):
    """Target difficulty level of a course."""

    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


# ---------------------------------------------------------------------------
# Quiz Question schemas
# ---------------------------------------------------------------------------


class QuizQuestionCreate(BaseModel):
    """Request body for creating a quiz question within a module."""

    question: str = Field(min_length=1)
    options: List[str] = Field(min_length=2, description="At least 2 answer options required")
    correct_answer: str = Field(min_length=1)
    explanation: Optional[str] = None


class QuizQuestionUpdate(BaseModel):
    """Request body for partially updating a quiz question."""

    question: Optional[str] = Field(None, min_length=1)
    options: Optional[List[str]] = Field(None, min_length=2)
    correct_answer: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = None


class QuizQuestionResponse(BaseModel):
    """Quiz question representation returned by API endpoints."""

    id: int
    module_id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Lesson schemas
# ---------------------------------------------------------------------------


class LessonCreate(BaseModel):
    """Request body for creating a lesson within a module."""

    title: str = Field(min_length=1, max_length=255)
    markdown_content: str = Field(default="")
    estimated_minutes: int = Field(default=0, ge=0)
    sort_order: int = Field(default=0, ge=0)


class LessonUpdate(BaseModel):
    """Request body for partially updating a lesson."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    markdown_content: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    sort_order: Optional[int] = Field(None, ge=0)


class LessonResponse(BaseModel):
    """Lesson representation returned by API endpoints.

    ``sanitised_html`` contains the lesson content rendered from Markdown
    and sanitised to prevent XSS — safe to inject directly into the DOM.
    """

    id: int
    module_id: int
    title: str
    markdown_content: str
    sanitised_html: Optional[str] = None
    estimated_minutes: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Module schemas
# ---------------------------------------------------------------------------


class ModuleCreate(BaseModel):
    """Request body for creating a module within a course."""

    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(default="")
    sort_order: int = Field(default=0, ge=0)


class ModuleUpdate(BaseModel):
    """Request body for partially updating a module."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)


class ModuleResponse(BaseModel):
    """Module representation returned by API endpoints."""

    id: int
    course_id: int
    title: str
    summary: str
    sort_order: int
    created_at: datetime
    lessons: List[LessonResponse] = []
    quiz_questions: List[QuizQuestionResponse] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Course schemas
# ---------------------------------------------------------------------------


class CourseCreate(BaseModel):
    """Request body for creating a new course."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="")
    difficulty: CourseDifficulty = CourseDifficulty.beginner
    estimated_duration: int = Field(default=0, ge=0, description="Estimated duration in minutes")
    tags: Optional[List[str]] = None


class CourseUpdate(BaseModel):
    """Request body for partially updating a course."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[CourseStatus] = None
    difficulty: Optional[CourseDifficulty] = None
    estimated_duration: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None


class CourseResponse(BaseModel):
    """Course representation returned by API endpoints (without nested content)."""

    id: int
    title: str
    description: str
    status: CourseStatus
    difficulty: str
    estimated_duration: int
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    modules: List[ModuleResponse] = []

    model_config = {"from_attributes": True}


class CourseListResponse(BaseModel):
    """Paginated list of courses."""

    items: List[CourseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"from_attributes": True}


class CourseDetailResponse(BaseModel):
    """Full course detail including all nested modules, lessons, and quiz questions."""

    id: int
    title: str
    description: str
    status: CourseStatus
    difficulty: str
    estimated_duration: int
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    modules: List[ModuleResponse] = []

    model_config = {"from_attributes": True}


class CatalogResponse(BaseModel):
    """Lightweight course entry shown in the public catalog for learners.

    Only published courses appear in the catalog.
    """

    id: int
    title: str
    description: str
    difficulty: str
    estimated_duration: int
    tags: Optional[List[str]] = None
    module_count: int = 0

    model_config = {"from_attributes": True}
