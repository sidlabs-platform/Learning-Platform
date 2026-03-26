"""API tests for Course management endpoints.

Covers course CRUD, publish/unpublish, catalog visibility,
and role-based access control.

Traceability:
    BRD-FR-003: Admin-only CRUD
    BRD-FR-005: Learner catalog shows only published courses
    BRD-FR-007: Admin publishes course
    BRD-FR-008: Admin unpublishes course
    BRD-FR-009: Course structure
    BRD-FR-010: Course required fields
    TASK-009: Course management router
"""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# POST /api/v1/courses — Create course
# ---------------------------------------------------------------------------


async def test_admin_create_course_returns_201(client: AsyncClient, admin_user):
    """Admin creating a course returns 201 with course data. [BRD-FR-003, BRD-FR-010]"""
    payload = {
        "title": "GitHub Foundations",
        "description": "Learn GitHub basics.",
        "difficulty": "beginner",
        "estimated_duration": 120,
        "tags": ["github", "beginner"],
    }
    resp = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "GitHub Foundations"
    assert data["status"] == "draft"
    assert data["difficulty"] == "beginner"
    assert data["estimated_duration"] == 120
    assert "github" in data["tags"]
    assert "id" in data


async def test_learner_cannot_create_course_returns_403(
    client: AsyncClient, learner_user
):
    """Learner creating a course gets 403. [BRD-FR-003]"""
    payload = {
        "title": "Forbidden Course",
        "description": "A learner tries to create.",
        "difficulty": "beginner",
        "estimated_duration": 30,
    }
    resp = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_create_course_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated course creation returns 401."""
    payload = {
        "title": "Ghost Course",
        "description": "No auth.",
        "difficulty": "beginner",
        "estimated_duration": 30,
    }
    resp = await client.post("/api/v1/courses/", json=payload)
    assert resp.status_code == 401


async def test_create_course_missing_required_fields_returns_422(
    client: AsyncClient, admin_user
):
    """Missing required fields returns 422. [BRD-FR-010]"""
    resp = await client.post(
        "/api/v1/courses/",
        json={"title": "Incomplete Course"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


async def test_create_course_invalid_difficulty_returns_422(
    client: AsyncClient, admin_user
):
    """Invalid difficulty value returns 422."""
    payload = {
        "title": "Bad Difficulty",
        "description": "Test.",
        "difficulty": "expert",
        "estimated_duration": 30,
    }
    resp = await client.post(
        "/api/v1/courses/",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/courses — List courses
# ---------------------------------------------------------------------------


async def test_admin_list_courses_sees_draft_and_published(
    client: AsyncClient, admin_user, draft_course, published_course
):
    """Admin sees both draft and published courses. [BRD-FR-005]"""
    resp = await client.get(
        "/api/v1/courses/",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert draft_course.id in ids
    assert published_course.id in ids


async def test_learner_list_courses_sees_only_published(
    client: AsyncClient, learner_user, draft_course, published_course
):
    """Learner catalog shows only published courses. [BRD-FR-005]"""
    resp = await client.get(
        "/api/v1/courses/",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert published_course.id in ids
    assert draft_course.id not in ids


async def test_list_courses_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated course listing returns 401."""
    resp = await client.get("/api/v1/courses/")
    assert resp.status_code == 401


async def test_admin_filter_courses_by_status_draft(
    client: AsyncClient, admin_user, draft_course, published_course
):
    """Admin can filter courses by status=draft. [BRD-FR-005]"""
    resp = await client.get(
        "/api/v1/courses/?status=draft",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert draft_course.id in ids
    assert published_course.id not in ids


# ---------------------------------------------------------------------------
# GET /api/v1/courses/{id} — Get course detail
# ---------------------------------------------------------------------------


async def test_get_course_detail_returns_course_with_modules(
    client: AsyncClient, admin_user, course_with_lesson
):
    """Course detail endpoint returns nested modules/lessons. [BRD-FR-009]"""
    course = course_with_lesson["course"]
    resp = await client.get(
        f"/api/v1/courses/{course.id}",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == course.id
    assert "modules" in data
    assert len(data["modules"]) >= 1
    assert "lessons" in data["modules"][0]


async def test_get_nonexistent_course_returns_404(client: AsyncClient, admin_user):
    """Non-existent course ID returns 404."""
    resp = await client.get(
        "/api/v1/courses/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/v1/courses/{id} — Update course
# ---------------------------------------------------------------------------


async def test_admin_update_course_returns_updated_data(
    client: AsyncClient, admin_user, draft_course
):
    """Admin can update course fields. [BRD-FR-003]"""
    resp = await client.patch(
        f"/api/v1/courses/{draft_course.id}",
        json={"title": "Updated Title"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


async def test_learner_cannot_update_course_returns_403(
    client: AsyncClient, learner_user, draft_course
):
    """Learner cannot update course. [BRD-FR-003]"""
    resp = await client.patch(
        f"/api/v1/courses/{draft_course.id}",
        json={"title": "Hijacked Title"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_update_nonexistent_course_returns_404(client: AsyncClient, admin_user):
    """Updating a non-existent course returns 404."""
    resp = await client.patch(
        "/api/v1/courses/00000000-0000-0000-0000-000000000000",
        json={"title": "Ghost Update"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/courses/{id} — Delete course
# ---------------------------------------------------------------------------


async def test_admin_delete_course_returns_204(
    client: AsyncClient, admin_user, draft_course
):
    """Admin can delete a course, returns 204. [BRD-FR-003]"""
    resp = await client.delete(
        f"/api/v1/courses/{draft_course.id}",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 204


async def test_learner_cannot_delete_course_returns_403(
    client: AsyncClient, learner_user, draft_course
):
    """Learner cannot delete a course. [BRD-FR-003]"""
    resp = await client.delete(
        f"/api/v1/courses/{draft_course.id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_delete_nonexistent_course_returns_404(client: AsyncClient, admin_user):
    """Deleting a non-existent course returns 404."""
    resp = await client.delete(
        "/api/v1/courses/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/courses/{id}/publish — Publish course
# ---------------------------------------------------------------------------


async def test_admin_publish_course_changes_status_to_published(
    client: AsyncClient, admin_user, draft_course
):
    """Admin can publish a draft course. [BRD-FR-007]"""
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/publish",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


async def test_learner_cannot_publish_course_returns_403(
    client: AsyncClient, learner_user, draft_course
):
    """Learner cannot publish a course. [BRD-FR-003, BRD-FR-007]"""
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/publish",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_publish_nonexistent_course_returns_404(client: AsyncClient, admin_user):
    """Publishing a non-existent course returns 404."""
    resp = await client.post(
        "/api/v1/courses/00000000-0000-0000-0000-000000000000/publish",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


async def test_publish_already_published_course_returns_409(
    client: AsyncClient, admin_user, published_course
):
    """Publishing an already-published course returns 409. [BRD-FR-007]"""
    resp = await client.post(
        f"/api/v1/courses/{published_course.id}/publish",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# POST /api/v1/courses/{id}/unpublish — Unpublish course
# ---------------------------------------------------------------------------


async def test_admin_unpublish_course_changes_status_to_draft(
    client: AsyncClient, admin_user, published_course
):
    """Admin can unpublish a published course. [BRD-FR-008]"""
    resp = await client.post(
        f"/api/v1/courses/{published_course.id}/unpublish",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"


async def test_unpublish_draft_course_returns_409(
    client: AsyncClient, admin_user, draft_course
):
    """Unpublishing a draft course returns 409. [BRD-FR-008]"""
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/unpublish",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 409


async def test_unpublished_course_not_visible_to_learner(
    client: AsyncClient, admin_user, learner_user, published_course
):
    """After unpublish, course disappears from learner catalog. [BRD-FR-008]"""
    # Unpublish
    await client.post(
        f"/api/v1/courses/{published_course.id}/unpublish",
        headers=auth_headers(admin_user["token"]),
    )
    # Learner catalog
    resp = await client.get(
        "/api/v1/courses/",
        headers=auth_headers(learner_user["token"]),
    )
    ids = [c["id"] for c in resp.json()]
    assert published_course.id not in ids
