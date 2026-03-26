"""API tests for Lesson management endpoints.

Traceability:
    BRD-FR-003: Admin-only write access
    BRD-FR-011: Lesson markdown content and estimated_minutes
    BRD-FR-013: Lesson ordering by sort_order
    TASK-011: Lesson endpoints
    TASK-016: XSS sanitisation of markdown content
"""

from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# POST /api/v1/courses/{course_id}/modules/{module_id}/lessons
# ---------------------------------------------------------------------------


async def test_admin_create_lesson_returns_201(
    client: AsyncClient, admin_user, course_with_module
):
    """Admin creates a lesson, returns 201 with lesson data. [BRD-FR-011]"""
    course = course_with_module["course"]
    module = course_with_module["module"]
    payload = {
        "title": "Intro Lesson",
        "markdown_content": "# Hello\nThis is safe content.",
        "estimated_minutes": 15,
        "sort_order": 0,
    }
    resp = await client.post(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Intro Lesson"
    assert data["module_id"] == module.id
    assert data["estimated_minutes"] == 15
    assert data["sort_order"] == 0


async def test_learner_cannot_create_lesson_returns_403(
    client: AsyncClient, learner_user, course_with_module
):
    """Learner cannot create a lesson. [BRD-FR-003]"""
    course = course_with_module["course"]
    module = course_with_module["module"]
    payload = {
        "title": "Sneaky Lesson",
        "markdown_content": "Forbidden.",
        "estimated_minutes": 5,
        "sort_order": 0,
    }
    resp = await client.post(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons",
        json=payload,
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_create_lesson_nonexistent_module_returns_404(
    client: AsyncClient, admin_user, draft_course
):
    """Creating a lesson in a non-existent module returns 404."""
    payload = {
        "title": "Orphan Lesson",
        "markdown_content": "No module.",
        "estimated_minutes": 5,
        "sort_order": 0,
    }
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/modules/00000000-0000-0000-0000-000000000000/lessons",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


async def test_create_lesson_xss_content_is_sanitised(
    client: AsyncClient, admin_user, course_with_module
):
    """XSS script tags in markdown_content are stripped. [BRD-FR-011, TASK-016]"""
    course = course_with_module["course"]
    module = course_with_module["module"]
    malicious = "<script>alert('xss')</script><p>Safe</p>"
    payload = {
        "title": "XSS Lesson",
        "markdown_content": malicious,
        "estimated_minutes": 5,
        "sort_order": 0,
    }
    resp = await client.post(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 201
    content = resp.json()["markdown_content"]
    assert "<script>" not in content
    assert "alert(" not in content
    # Safe content preserved
    assert "<p>Safe</p>" in content


async def test_create_lesson_missing_fields_returns_422(
    client: AsyncClient, admin_user, course_with_module
):
    """Missing required lesson fields returns 422."""
    course = course_with_module["course"]
    module = course_with_module["module"]
    resp = await client.post(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons",
        json={"title": "Incomplete Lesson"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/courses/{course_id}/modules/{module_id}/lessons
# ---------------------------------------------------------------------------


async def test_list_lessons_returns_200_for_authenticated_user(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Authenticated user can list lessons. [BRD-FR-011]"""
    course = course_with_lesson["course"]
    module = course_with_lesson["module"]
    resp = await client.get(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    lessons = resp.json()
    assert len(lessons) >= 1
    assert lessons[0]["id"] == course_with_lesson["lesson"].id


async def test_list_lessons_nonexistent_module_returns_404(
    client: AsyncClient, admin_user, draft_course
):
    """Listing lessons for a non-existent module returns 404."""
    resp = await client.get(
        f"/api/v1/courses/{draft_course.id}/modules/00000000-0000-0000-0000-000000000000/lessons",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}
# ---------------------------------------------------------------------------


async def test_get_lesson_returns_200_with_lesson_data(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Get a single lesson returns 200 with all fields. [BRD-FR-011]"""
    course = course_with_lesson["course"]
    module = course_with_lesson["module"]
    lesson = course_with_lesson["lesson"]
    resp = await client.get(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons/{lesson.id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == lesson.id
    assert "markdown_content" in data
    assert "estimated_minutes" in data


async def test_get_nonexistent_lesson_returns_404(
    client: AsyncClient, admin_user, course_with_module
):
    """Getting a non-existent lesson returns 404."""
    course = course_with_module["course"]
    module = course_with_module["module"]
    resp = await client.get(
        f"/api/v1/courses/{course.id}/modules/{module.id}/lessons/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404
