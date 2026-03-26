"""API tests for Module management endpoints.

Traceability:
    BRD-FR-003: Admin-only CRUD
    BRD-FR-009: Course/module structure
    BRD-FR-013: Modules ordered by sort_order
    TASK-010: Module endpoints
"""

from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# POST /api/v1/courses/{course_id}/modules
# ---------------------------------------------------------------------------


async def test_admin_create_module_returns_201(
    client: AsyncClient, admin_user, draft_course
):
    """Admin creates a module, returns 201 with module data. [BRD-FR-003, BRD-FR-009]"""
    payload = {"title": "Module One", "summary": "An intro module.", "sort_order": 0}
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/modules",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Module One"
    assert data["course_id"] == draft_course.id
    assert data["sort_order"] == 0


async def test_learner_cannot_create_module_returns_403(
    client: AsyncClient, learner_user, draft_course
):
    """Learner cannot create a module. [BRD-FR-003]"""
    payload = {"title": "Sneaky Module", "summary": "No permission.", "sort_order": 0}
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/modules",
        json=payload,
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_create_module_nonexistent_course_returns_404(
    client: AsyncClient, admin_user
):
    """Creating a module in a non-existent course returns 404."""
    payload = {"title": "Orphan Module", "summary": "No parent.", "sort_order": 0}
    resp = await client.post(
        "/api/v1/courses/00000000-0000-0000-0000-000000000000/modules",
        json=payload,
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


async def test_create_module_missing_fields_returns_422(
    client: AsyncClient, admin_user, draft_course
):
    """Missing required module fields returns 422."""
    resp = await client.post(
        f"/api/v1/courses/{draft_course.id}/modules",
        json={"title": "Missing Summary"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/courses/{course_id}/modules
# ---------------------------------------------------------------------------


async def test_list_modules_returns_sorted_by_sort_order(
    client: AsyncClient, admin_user, draft_course
):
    """Modules are returned sorted by sort_order. [BRD-FR-013]"""
    for i in [2, 0, 1]:
        await client.post(
            f"/api/v1/courses/{draft_course.id}/modules",
            json={"title": f"Module {i}", "summary": f"Summary {i}", "sort_order": i},
            headers=auth_headers(admin_user["token"]),
        )

    resp = await client.get(
        f"/api/v1/courses/{draft_course.id}/modules",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    modules = resp.json()
    sort_orders = [m["sort_order"] for m in modules]
    assert sort_orders == sorted(sort_orders)


async def test_list_modules_nonexistent_course_returns_404(
    client: AsyncClient, admin_user
):
    """Listing modules for non-existent course returns 404."""
    resp = await client.get(
        "/api/v1/courses/00000000-0000-0000-0000-000000000000/modules",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404


async def test_learner_can_list_modules(
    client: AsyncClient, learner_user, course_with_module
):
    """Learner can list modules (read-only access). [BRD-FR-009]"""
    course = course_with_module["course"]
    resp = await client.get(
        f"/api/v1/courses/{course.id}/modules",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# PATCH /api/v1/courses/{course_id}/modules/{module_id}
# ---------------------------------------------------------------------------


async def test_admin_update_module_returns_updated_data(
    client: AsyncClient, admin_user, course_with_module
):
    """Admin can partially update a module. [BRD-FR-003]"""
    course = course_with_module["course"]
    module = course_with_module["module"]
    resp = await client.patch(
        f"/api/v1/courses/{course.id}/modules/{module.id}",
        json={"title": "Updated Module Title"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Module Title"


async def test_learner_cannot_update_module_returns_403(
    client: AsyncClient, learner_user, course_with_module
):
    """Learner cannot update a module. [BRD-FR-003]"""
    course = course_with_module["course"]
    module = course_with_module["module"]
    resp = await client.patch(
        f"/api/v1/courses/{course.id}/modules/{module.id}",
        json={"title": "Hijack"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_update_nonexistent_module_returns_404(
    client: AsyncClient, admin_user, draft_course
):
    """Updating a non-existent module returns 404."""
    resp = await client.patch(
        f"/api/v1/courses/{draft_course.id}/modules/00000000-0000-0000-0000-000000000000",
        json={"title": "Ghost Module"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 404
