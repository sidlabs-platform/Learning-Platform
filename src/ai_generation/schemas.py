"""
Pydantic v2 schemas for the AI Generation service.

Covers the full lifecycle of an AI content generation request:
initiation, status polling, and targeted section regeneration.

The ``DifficultyLevel`` enum is re-exported here from the course management
schemas to avoid circular imports while keeping the generation request
self-contained.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from src.course_management.schemas import DifficultyLevel


class GenerationStatus(str, Enum):
    """
    Lifecycle state of an AI content generation request.

    ``pending``     — queued but not yet picked up by the worker.
    ``in_progress`` — actively being processed by GitHub Models.
    ``completed``   — generation succeeded; artifact(s) available.
    ``failed``      — generation encountered an unrecoverable error.
    """

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class GenerationRequest(BaseModel):
    """
    Request body for ``POST /api/v1/ai/generate``.

    All fields drive the prompt template used to instruct GPT-4o.
    ``learning_objectives`` must be a non-empty list of plain-text strings.
    """

    topic: str
    target_audience: str
    learning_objectives: list[str]
    difficulty: DifficultyLevel
    desired_module_count: int = 3
    preferred_tone: str = "professional"


class GenerationResponse(BaseModel):
    """
    Immediate response body for ``POST /api/v1/ai/generate``.

    The generation request is accepted and processed asynchronously; use
    ``request_id`` to poll for completion via
    ``GET /api/v1/ai/generate/{request_id}``.
    """

    request_id: str
    status: GenerationStatus
    message: str


class GenerationStatusResponse(BaseModel):
    """
    Detailed status payload returned by ``GET /api/v1/ai/generate/{request_id}``.

    ``course_id`` is populated once generation completes and the draft course
    has been persisted.  ``error`` contains a human-readable message if
    ``status`` is ``failed``.
    """

    request_id: str
    status: GenerationStatus
    course_id: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime


class SectionType(str, Enum):
    """
    Valid section types that can be targeted for individual regeneration.

    ``lesson``         — regenerate the Markdown content of a single lesson.
    ``quiz``           — regenerate quiz questions for a module.
    ``module_summary`` — regenerate the summary paragraph of a module.
    """

    lesson = "lesson"
    quiz = "quiz"
    module_summary = "module_summary"


class SectionRegenerationRequest(BaseModel):
    """
    Request body for ``POST /api/v1/ai/regenerate``.

    Allows targeted regeneration of a single course section without
    triggering a full course rebuild.

    ``section_type`` must be a :class:`SectionType` value.
    ``section_id`` is the UUID of the resource to regenerate.
    ``additional_instructions`` is an optional free-text field that is
    appended to the generation prompt.
    """

    section_type: SectionType
    section_id: str
    additional_instructions: str = ""


__all__ = [
    "DifficultyLevel",
    "GenerationStatus",
    "SectionType",
    "GenerationRequest",
    "GenerationResponse",
    "GenerationStatusResponse",
    "SectionRegenerationRequest",
]
