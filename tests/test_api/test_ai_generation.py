"""API tests for the AI Generation service.

Mocks all external GitHub Models API calls using unittest.mock.

Traceability:
    BRD-INT-001 – BRD-INT-010: GitHub Models integration requirements
    BRD-FR-029: Admin triggers AI generation
    BRD-FR-030: Generation request status polling
    BRD-FR-031: Content stored as draft
    TASK-018: AI generation router
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# POST /api/v1/ai/generate
# ---------------------------------------------------------------------------


async def test_admin_trigger_generation_returns_202(
    client: AsyncClient, admin_user
):
    """Admin triggering generation returns 202 Accepted. [BRD-FR-029]"""
    payload = {
        "topic": "GitHub Actions",
        "target_audience": "Developers",
        "learning_objectives": ["Understand CI/CD", "Write workflows"],
        "difficulty": "beginner",
        "desired_module_count": 3,
        "preferred_tone": "professional",
    }
    # Patch process_generation so it doesn't try to call GitHub Models.
    # We only patch process_generation; asyncio.create_task is left as-is so it
    # can schedule the (now harmless) AsyncMock coroutine without breaking the
    # event loop.
    with patch(
        "src.ai_generation.router.process_generation",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            "/api/v1/ai/generate",
            json=payload,
            headers=auth_headers(admin_user["token"]),
        )

    assert resp.status_code == 202
    data = resp.json()
    assert "request_id" in data
    assert data["status"] == "pending"
    assert "message" in data


async def test_learner_cannot_trigger_generation_returns_403(
    client: AsyncClient, learner_user
):
    """Learner cannot trigger AI generation. [BRD-FR-003]"""
    payload = {
        "topic": "GitHub Actions",
        "target_audience": "Developers",
        "learning_objectives": ["Understand CI/CD"],
        "difficulty": "beginner",
    }
    resp = await client.post(
        "/api/v1/ai/generate",
        json=payload,
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_trigger_generation_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated AI generation request returns 401."""
    payload = {
        "topic": "GitHub Actions",
        "target_audience": "Developers",
        "learning_objectives": ["Understand CI/CD"],
        "difficulty": "beginner",
    }
    resp = await client.post("/api/v1/ai/generate", json=payload)
    assert resp.status_code == 401


async def test_trigger_generation_missing_required_field_returns_422(
    client: AsyncClient, admin_user
):
    """Missing required field in generation request returns 422."""
    # Missing learning_objectives
    payload = {
        "topic": "GitHub Actions",
        "target_audience": "Developers",
        "difficulty": "beginner",
    }
    resp = await client.post(
        "/api/v1/ai/generate",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


async def test_trigger_generation_invalid_difficulty_returns_422(
    client: AsyncClient, admin_user
):
    """Invalid difficulty in generation request returns 422."""
    payload = {
        "topic": "GitHub Actions",
        "target_audience": "Developers",
        "learning_objectives": ["Learn CI/CD"],
        "difficulty": "ultra-hard",
    }
    resp = await client.post(
        "/api/v1/ai/generate",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/ai/generate/{request_id}
# ---------------------------------------------------------------------------


async def test_get_generation_status_returns_status_object(
    client: AsyncClient, admin_user
):
    """Polling a valid request ID returns the status. [BRD-FR-030]"""
    payload = {
        "topic": "GitHub Actions",
        "target_audience": "Developers",
        "learning_objectives": ["Understand CI/CD"],
        "difficulty": "beginner",
    }
    with patch(
        "src.ai_generation.router.process_generation",
        new_callable=AsyncMock,
        return_value=None,
    ):
        create_resp = await client.post(
            "/api/v1/ai/generate",
            json=payload,
            headers=auth_headers(admin_user["token"]),
        )

    request_id = create_resp.json()["request_id"]

    resp = await client.get(
        f"/api/v1/ai/generate/{request_id}",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["request_id"] == request_id
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_generation_status_nonexistent_returns_404(
    client: AsyncClient, admin_user
):
    """Polling a non-existent request ID returns 404."""
    resp = await client.get(
        "/api/v1/ai/generate/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


async def test_learner_cannot_poll_generation_status_returns_403(
    client: AsyncClient, learner_user
):
    """Learner cannot poll AI generation status. [BRD-FR-003]"""
    resp = await client.get(
        "/api/v1/ai/generate/some-request-id",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/v1/ai/regenerate
# ---------------------------------------------------------------------------


async def test_regenerate_section_returns_501(client: AsyncClient, admin_user):
    """Section regeneration returns 501 Not Implemented (future feature)."""
    payload = {
        "section_type": "lesson",
        "section_id": "00000000-0000-0000-0000-000000000001",
        "additional_instructions": "",
    }
    resp = await client.post(
        "/api/v1/ai/regenerate",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 501


# ---------------------------------------------------------------------------
# GET /api/v1/ai/templates
# ---------------------------------------------------------------------------


async def test_list_templates_returns_list(client: AsyncClient, admin_user):
    """Admin can list available prompt templates."""
    resp = await client.get(
        "/api/v1/ai/templates",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


async def test_learner_cannot_list_templates_returns_403(
    client: AsyncClient, learner_user
):
    """Learner cannot list AI templates. [BRD-FR-003]"""
    resp = await client.get(
        "/api/v1/ai/templates",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403
