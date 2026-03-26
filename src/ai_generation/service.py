"""AI content generation orchestration service.

Ties together the prompt service and GitHub Models client to manage
the lifecycle of AI-powered course content generation requests.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_generation.github_models_client import generate_with_retry
from src.ai_generation.prompt_service import get_available_templates, render_prompt
from src.ai_generation.schemas import GenerationRequest
from src.database import AsyncSessionLocal
from src.models import ContentGenerationArtifact, ContentGenerationRequest

logger = logging.getLogger(__name__)


async def create_generation_request(
    gen_req: GenerationRequest,
    requester_id: str,
    db: AsyncSession,
) -> ContentGenerationRequest:
    """Create a new content generation request record.

    Renders the course-outline prompt template (PT-001) with the supplied
    parameters and persists a ``ContentGenerationRequest`` with status
    *pending*.  If the template cannot be found the service falls back to
    building a simple prompt string directly.

    Args:
        gen_req: Validated generation request payload.
        requester_id: ID of the admin user initiating the request.
        db: Active async database session.

    Returns:
        The newly created ``ContentGenerationRequest`` ORM instance.
    """

    # Build the prompt --------------------------------------------------------
    template_variables: dict = {
        "topic": gen_req.topic,
        "target_audience": gen_req.target_audience,
        "learning_objectives": "\n".join(gen_req.learning_objectives),
        "difficulty": gen_req.difficulty.value,
        "desired_module_count": gen_req.desired_module_count,
        "preferred_tone": gen_req.preferred_tone,
    }

    try:
        prompt_text: str = render_prompt("PT-001", template_variables)
    except Exception:
        # Fallback: build a simple prompt when the template is unavailable
        logger.warning(
            "PT-001 template unavailable – using fallback prompt for topic=%s",
            gen_req.topic,
        )
        prompt_text = (
            f"Create a comprehensive course outline about '{gen_req.topic}' "
            f"for {gen_req.target_audience} at {gen_req.difficulty.value} level.\n\n"
            f"Learning objectives:\n{template_variables['learning_objectives']}\n\n"
            f"Number of modules: {gen_req.desired_module_count}\n"
            f"Tone: {gen_req.preferred_tone}"
        )

    # Persist the request record ----------------------------------------------
    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    record = ContentGenerationRequest(
        id=request_id,
        prompt=prompt_text,
        model="gpt-4o",
        requester_id=requester_id,
        status="pending",
        created_at=now,
        updated_at=now,
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    logger.info(
        "Generation request created: request_id=%s requester=%s topic=%s",
        request_id,
        requester_id,
        gen_req.topic,
    )

    return record


async def process_generation(request_id: str) -> None:
    """Run AI content generation in the background.

    Intended to be launched via ``asyncio.create_task``.  Opens its own
    database session, updates the request status through its lifecycle,
    calls the GitHub Models API, and persists the resulting artifact.

    Args:
        request_id: Primary key of the ``ContentGenerationRequest`` to process.
    """

    async with AsyncSessionLocal() as db:
        try:
            # Fetch the request -----------------------------------------------
            stmt = select(ContentGenerationRequest).where(
                ContentGenerationRequest.id == request_id
            )
            result = await db.execute(stmt)
            request = result.scalar_one_or_none()

            if request is None:
                logger.error("Generation request not found: %s", request_id)
                return

            # Mark as in-progress ---------------------------------------------
            request.status = "in_progress"
            request.updated_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info("Generation started: request_id=%s", request_id)

            # Call AI model ---------------------------------------------------
            generated_content: str = await generate_with_retry(request.prompt)

            # Store the artifact ----------------------------------------------
            artifact = ContentGenerationArtifact(
                id=str(uuid.uuid4()),
                generated_content=generated_content,
                source_request_id=request_id,
                created_at=datetime.now(timezone.utc),
            )
            db.add(artifact)

            # Mark as completed -----------------------------------------------
            request.status = "completed"
            request.updated_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(
                "Generation completed: request_id=%s artifact_id=%s",
                request_id,
                artifact.id,
            )

        except Exception as exc:
            # Mark as failed --------------------------------------------------
            logger.error(
                "Generation failed: request_id=%s error=%s",
                request_id,
                str(exc),
            )
            try:
                # Re-fetch inside the except block in case the session is dirty
                stmt = select(ContentGenerationRequest).where(
                    ContentGenerationRequest.id == request_id
                )
                result = await db.execute(stmt)
                request = result.scalar_one_or_none()
                if request is not None:
                    request.status = "failed"
                    request.updated_at = datetime.now(timezone.utc)
                    await db.commit()
            except Exception as inner_exc:
                logger.error(
                    "Failed to update status to 'failed': request_id=%s error=%s",
                    request_id,
                    str(inner_exc),
                )


async def get_generation_status(
    request_id: str,
    db: AsyncSession,
) -> Optional[ContentGenerationRequest]:
    """Retrieve a content generation request by its ID.

    Args:
        request_id: Primary key of the generation request.
        db: Active async database session.

    Returns:
        The ``ContentGenerationRequest`` if found, otherwise ``None``.
    """

    stmt = select(ContentGenerationRequest).where(
        ContentGenerationRequest.id == request_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_generation_artifact(
    request_id: str,
    db: AsyncSession,
) -> Optional[ContentGenerationArtifact]:
    """Retrieve the generation artifact linked to a request.

    Args:
        request_id: The ``source_request_id`` of the artifact.
        db: Active async database session.

    Returns:
        The ``ContentGenerationArtifact`` if found, otherwise ``None``.
    """

    stmt = select(ContentGenerationArtifact).where(
        ContentGenerationArtifact.source_request_id == request_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
