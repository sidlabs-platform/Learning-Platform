"""Pydantic v2 schemas for AI content generation.

Covers:
- Course generation requests
- Section regeneration requests
- Generation status polling
- Content artifact responses
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ContentGenerationStatus(str, Enum):
    """Lifecycle status of an AI content-generation request."""

    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class GenerateCourseRequest(BaseModel):
    """Request body for triggering AI generation of a full course outline."""

    topic: str = Field(min_length=3, max_length=200, description="The subject of the course")
    audience: str = Field(
        min_length=3,
        max_length=200,
        description="Intended target audience (e.g. 'junior developers')",
    )
    objectives: List[str] = Field(
        min_length=1, description="Learning objectives the course should cover"
    )
    difficulty: str = Field(
        pattern="^(beginner|intermediate|advanced)$",
        description="Target difficulty level",
    )
    model: str = Field(default="gpt-4o", description="GitHub Models model identifier to use")


class RegenerateSectionRequest(BaseModel):
    """Request body for regenerating a specific section of an existing course."""

    section_type: str = Field(
        pattern="^(lesson|module|quiz)$",
        description="Type of section to regenerate",
    )
    section_id: int = Field(description="Primary key of the section to regenerate")
    instructions: Optional[str] = Field(
        None, description="Optional additional instructions for the regeneration prompt"
    )
    model: str = Field(default="gpt-4o", description="GitHub Models model identifier to use")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class GenerationStatusResponse(BaseModel):
    """Status response for a content-generation request."""

    request_id: int
    status: ContentGenerationStatus
    created_at: datetime
    error_message: Optional[str] = None
    artifact_id: Optional[int] = None

    model_config = {"from_attributes": True}


class ContentArtifactResponse(BaseModel):
    """Representation of a completed AI generation artifact."""

    id: int
    generated_content: str
    source_request_id: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
