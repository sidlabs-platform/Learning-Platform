"""Unit tests for the AI Generation service.

Mocks all external GitHub Models API calls using unittest.mock.

Traceability:
    BRD-INT-001 – BRD-INT-010: GitHub Models integration
    BRD-FR-029: AI generation request creation
    BRD-FR-031: Content stored as draft
    TASK-019: AI generation service
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_generation.schemas import DifficultyLevel, GenerationRequest
from src.ai_generation.service import (
    create_generation_request,
    get_generation_artifact,
    get_generation_status,
)


# ---------------------------------------------------------------------------
# create_generation_request
# ---------------------------------------------------------------------------


async def test_create_generation_request_creates_pending_record(
    db_session: AsyncSession, admin_user
):
    """create_generation_request persists a pending ContentGenerationRequest. [BRD-FR-029]"""
    gen_req = GenerationRequest(
        topic="GitHub Actions",
        target_audience="Developers",
        learning_objectives=["Understand CI/CD", "Write workflows"],
        difficulty=DifficultyLevel.beginner,
    )

    record = await create_generation_request(
        gen_req=gen_req,
        requester_id=admin_user["user"].id,
        db=db_session,
    )

    assert record.id is not None
    assert record.status == "pending"
    assert record.requester_id == admin_user["user"].id
    assert "GitHub Actions" in record.prompt or len(record.prompt) > 0
    assert record.model == "gpt-4o"


async def test_get_generation_status_returns_record(
    db_session: AsyncSession, admin_user
):
    """get_generation_status returns the request record. [BRD-FR-030]"""
    gen_req = GenerationRequest(
        topic="GitHub Actions",
        target_audience="Developers",
        learning_objectives=["Understand CI/CD"],
        difficulty=DifficultyLevel.beginner,
    )

    record = await create_generation_request(
        gen_req=gen_req,
        requester_id=admin_user["user"].id,
        db=db_session,
    )

    found = await get_generation_status(record.id, db_session)
    assert found is not None
    assert found.id == record.id


async def test_get_generation_status_unknown_id_returns_none(
    db_session: AsyncSession,
):
    """get_generation_status returns None for unknown ID."""
    result = await get_generation_status(
        "00000000-0000-0000-0000-000000000000", db_session
    )
    assert result is None


async def test_get_generation_artifact_returns_none_when_not_created(
    db_session: AsyncSession, admin_user
):
    """get_generation_artifact returns None before processing. [BRD-FR-031]"""
    gen_req = GenerationRequest(
        topic="GitHub Security",
        target_audience="Security Engineers",
        learning_objectives=["Understand GHAS"],
        difficulty=DifficultyLevel.advanced,
    )

    record = await create_generation_request(
        gen_req=gen_req,
        requester_id=admin_user["user"].id,
        db=db_session,
    )

    artifact = await get_generation_artifact(record.id, db_session)
    assert artifact is None


# ---------------------------------------------------------------------------
# GitHub Models client — mocked
# ---------------------------------------------------------------------------


async def test_generate_content_calls_github_models_api():
    """generate_content makes an HTTP call to the GitHub Models endpoint. [BRD-INT-001]"""
    from src.ai_generation.github_models_client import generate_content

    mock_response_data = {
        "choices": [{"message": {"content": "Generated course content here."}}]
    }

    with patch("src.ai_generation.github_models_client.httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        result = await generate_content("Create a course about Git.")

    assert result == "Generated course content here."


async def test_generate_content_handles_api_error_raises_503():
    """generate_content raises HTTPException 503 on server error response. [BRD-INT-008]"""
    from fastapi import HTTPException
    from src.ai_generation.github_models_client import generate_content

    with patch("src.ai_generation.github_models_client.httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        # 500 is in _RETRYABLE_STATUS_CODES so _execute_request raises HTTPException(503)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        with pytest.raises(HTTPException) as exc_info:
            await generate_content("Test prompt.")

    assert exc_info.value.status_code == 503


async def test_generate_with_retry_succeeds_after_retry():
    """generate_with_retry retries on HTTPException 503 and succeeds. [BRD-INT-007]"""
    from fastapi import HTTPException as FastAPIHTTPException
    from src.ai_generation.github_models_client import generate_with_retry

    call_count = 0

    async def _mock_generate(prompt, model, settings):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # The retry logic in generate_with_retry catches HTTPException(503)
            raise FastAPIHTTPException(
                status_code=503,
                detail="AI service unavailable",
            )
        return "Generated content after retry."

    with patch(
        "src.ai_generation.github_models_client._execute_request",
        side_effect=_mock_generate,
    ):
        with patch("src.ai_generation.github_models_client.asyncio.sleep", new_callable=AsyncMock):
            result = await generate_with_retry("Test prompt.", max_retries=2)

    assert result == "Generated content after retry."
