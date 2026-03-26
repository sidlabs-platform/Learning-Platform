"""Content persistence layer for AI generation requests and artifacts."""

import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import (
    ContentGenerationRequest,
    ContentGenerationArtifact,
    ContentGenerationStatus,
    Course,
    Module,
    Lesson,
    CourseStatus,
)
from src.schemas.ai_generation import GenerationStatusResponse, ContentArtifactResponse
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


async def create_generation_request(
    db: AsyncSession,
    prompt: str,
    model: str,
    requester_id: int,
) -> ContentGenerationRequest:
    """Create a new content generation request in pending status."""
    request = ContentGenerationRequest(
        prompt=prompt,
        model=model,
        requester_id=requester_id,
        status=ContentGenerationStatus.pending,
    )
    db.add(request)
    await db.flush()
    await db.refresh(request)
    return request


async def update_request_status(
    db: AsyncSession,
    request_id: int,
    new_status: ContentGenerationStatus,
    error_message: str | None = None,
) -> ContentGenerationRequest:
    """Update the status of a content generation request."""
    result = await db.execute(
        select(ContentGenerationRequest).where(ContentGenerationRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation request not found")
    request.status = new_status
    if error_message is not None:
        request.error_message = error_message
    await db.flush()
    await db.refresh(request)
    return request


async def save_generation_artifact(
    db: AsyncSession,
    request_id: int,
    generated_content: str,
    course_id: int | None = None,
    module_id: int | None = None,
    lesson_id: int | None = None,
) -> ContentGenerationArtifact:
    """Save generated content as an artifact linked to the request."""
    artifact = ContentGenerationArtifact(
        generated_content=generated_content,
        source_request_id=request_id,
        course_id=course_id,
        module_id=module_id,
        lesson_id=lesson_id,
    )
    db.add(artifact)
    await db.flush()
    await db.refresh(artifact)
    return artifact


async def get_request_status(
    db: AsyncSession,
    request_id: int,
) -> ContentGenerationRequest:
    """Get generation request by ID. Raises 404 if not found."""
    result = await db.execute(
        select(ContentGenerationRequest).where(ContentGenerationRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation request not found")
    return request


async def get_artifact(
    db: AsyncSession,
    artifact_id: int,
) -> ContentGenerationArtifact:
    """Get artifact by ID. Raises 404 if not found."""
    result = await db.execute(
        select(ContentGenerationArtifact).where(ContentGenerationArtifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    return artifact


async def approve_artifact(
    db: AsyncSession,
    artifact_id: int,
    approved_by: int,
) -> ContentGenerationArtifact:
    """Mark artifact as approved by an admin."""
    artifact = await get_artifact(db, artifact_id)
    artifact.approved_by = approved_by
    artifact.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(artifact)
    return artifact


async def apply_artifact_to_course(
    db: AsyncSession,
    artifact_id: int,
    admin_id: int,
) -> dict:
    """
    Parse the generated JSON content from an artifact and apply it to the database.

    Expects JSON structure from PT-001:
    {
      "title": "...",
      "description": "...",
      "modules": [
        {"title": "...", "summary": "...", "lessons": [{"title": "...", "estimated_minutes": 15}]}
      ]
    }

    Returns a summary of what was created.
    """
    artifact = await get_artifact(db, artifact_id)
    try:
        data = json.loads(artifact.generated_content)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Artifact content is not valid JSON: {exc}",
        )

    course_title = data.get("title", "Generated Course")
    course_desc = data.get("description", "")
    modules_data = data.get("modules", [])

    course = Course(
        title=course_title,
        description=course_desc,
        status=CourseStatus.draft,
        difficulty="beginner",
        estimated_duration=0,
        tags=[],
        created_by=admin_id,
    )
    db.add(course)
    await db.flush()

    module_count = 0
    lesson_count = 0

    for sort_idx, mod_data in enumerate(modules_data):
        module = Module(
            course_id=course.id,
            title=mod_data.get("title", f"Module {sort_idx + 1}"),
            summary=mod_data.get("summary", ""),
            sort_order=sort_idx,
        )
        db.add(module)
        await db.flush()
        module_count += 1

        for lesson_idx, lesson_data in enumerate(mod_data.get("lessons", [])):
            lesson = Lesson(
                module_id=module.id,
                title=lesson_data.get("title", f"Lesson {lesson_idx + 1}"),
                markdown_content="",
                estimated_minutes=lesson_data.get("estimated_minutes", 15),
                sort_order=lesson_idx,
            )
            db.add(lesson)
            lesson_count += 1

    artifact.course_id = course.id
    await approve_artifact(db, artifact_id, admin_id)

    logger.info(
        "Applied artifact %d to new course %d (%d modules, %d lessons)",
        artifact_id,
        course.id,
        module_count,
        lesson_count,
    )

    return {
        "course_id": course.id,
        "course_title": course_title,
        "modules_created": module_count,
        "lessons_created": lesson_count,
    }
