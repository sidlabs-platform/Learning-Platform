"""FastAPI router for AI content generation endpoints.

All endpoints require **admin** role and are mounted under the
``/api/v1/ai`` prefix by the application entry-point.
"""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_generation.prompt_service import get_available_templates
from src.ai_generation.schemas import (
    GenerationRequest,
    GenerationResponse,
    GenerationStatus,
    GenerationStatusResponse,
    SectionRegenerationRequest,
)
from src.ai_generation.service import (
    create_generation_request,
    get_generation_artifact,
    get_generation_status,
    process_generation,
)
from src.auth.dependencies import require_admin
from src.database import get_db
from src.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start AI course content generation",
)
async def generate_content(
    payload: GenerationRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> GenerationResponse:
    """Accept a generation request, persist it, and launch background processing.

    The endpoint returns immediately with a ``202 Accepted`` response
    containing the ``request_id``.  Clients should poll
    ``GET /generate/{request_id}`` for progress updates.
    """

    record = await create_generation_request(
        gen_req=payload,
        requester_id=current_user.id,
        db=db,
    )

    # Fire-and-forget background generation
    asyncio.create_task(process_generation(record.id))

    logger.info(
        "Generation task launched: request_id=%s user_id=%s",
        record.id,
        current_user.id,
    )

    return GenerationResponse(
        request_id=record.id,
        status=GenerationStatus.pending,
        message="Generation started",
    )


@router.get(
    "/generate/{request_id}",
    response_model=GenerationStatusResponse,
    summary="Check AI generation status",
)
async def check_generation_status(
    request_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> GenerationStatusResponse:
    """Return the current status of a content generation request.

    If the generation has completed, the response also includes the
    ``course_id`` from the resulting artifact (if one has been linked).
    """

    request = await get_generation_status(request_id, db)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation request '{request_id}' not found",
        )

    # If completed, try to retrieve the artifact for course_id
    course_id: str | None = None
    if request.status == "completed":
        artifact = await get_generation_artifact(request_id, db)
        if artifact is not None:
            course_id = artifact.course_id

    return GenerationStatusResponse(
        request_id=request.id,
        status=GenerationStatus(request.status),
        course_id=course_id,
        error=None,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


@router.post(
    "/regenerate",
    response_model=GenerationResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Regenerate a specific course section",
)
async def regenerate_section(
    payload: SectionRegenerationRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> GenerationResponse:
    """Regenerate a single course section (lesson, quiz, or module summary).

    .. note::
        This endpoint is reserved for a future release and currently
        returns ``501 Not Implemented``.
    """

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Section regeneration is not yet implemented",
    )


@router.get(
    "/templates",
    response_model=list[dict],
    summary="List available prompt templates",
)
async def list_templates(
    current_user: User = Depends(require_admin),
) -> list[dict]:
    """Return the catalogue of prompt templates available for content generation.

    Each entry contains the template ``id`` and human-readable ``name``.
    """

    templates = get_available_templates()
    return templates
