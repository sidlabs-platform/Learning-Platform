"""API tests for the Reporting service.

Traceability:
    BRD-FR-025: Admin dashboard statistics
    BRD-FR-026: CSV export of enrollments
    BRD-FR-027: CSV export of learner progress
    BRD-FR-003: Admin-only access
    TASK-025: Reporting router
"""

from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# GET /api/v1/reports/dashboard
# ---------------------------------------------------------------------------


async def test_admin_get_dashboard_returns_200(client: AsyncClient, admin_user):
    """Admin can access the dashboard endpoint. [BRD-FR-025]"""
    resp = await client.get(
        "/api/v1/reports/dashboard",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "total_courses" in data
    assert "total_enrollments" in data
    assert "overall_completion_rate" in data
    assert "enrollment_stats" in data
    assert "top_learners" in data


async def test_learner_cannot_access_dashboard_returns_403(
    client: AsyncClient, learner_user
):
    """Learner cannot access the admin dashboard. [BRD-FR-003]"""
    resp = await client.get(
        "/api/v1/reports/dashboard",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_dashboard_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated dashboard request returns 401."""
    resp = await client.get("/api/v1/reports/dashboard")
    assert resp.status_code == 401


async def test_dashboard_counts_are_non_negative(
    client: AsyncClient, admin_user, published_course, enrollment
):
    """Dashboard counts reflect actual data. [BRD-FR-025]"""
    resp = await client.get(
        "/api/v1/reports/dashboard",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_courses"] >= 1
    assert data["total_enrollments"] >= 1
    assert 0.0 <= data["overall_completion_rate"] <= 100.0


async def test_dashboard_enrollment_stats_structure(
    client: AsyncClient, admin_user, published_course, enrollment
):
    """Dashboard enrollment_stats has correct per-course structure. [BRD-FR-025]"""
    resp = await client.get(
        "/api/v1/reports/dashboard",
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    stats = resp.json()["enrollment_stats"]
    assert isinstance(stats, list)
    if stats:
        stat = stats[0]
        assert "course_id" in stat
        assert "course_title" in stat
        assert "total_enrollments" in stat
        assert "completion_rate" in stat


# ---------------------------------------------------------------------------
# POST /api/v1/reports/export — CSV export
# ---------------------------------------------------------------------------


async def test_admin_export_enrollments_csv_returns_csv(
    client: AsyncClient, admin_user
):
    """Admin can export enrollments as CSV. [BRD-FR-026]"""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "enrollments"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "Content-Disposition" in resp.headers
    assert "attachment" in resp.headers["Content-Disposition"]


async def test_admin_export_learner_progress_csv_returns_csv(
    client: AsyncClient, admin_user
):
    """Admin can export learner progress as CSV. [BRD-FR-027]"""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "learner_progress"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")


async def test_admin_export_quiz_results_returns_501(
    client: AsyncClient, admin_user
):
    """Quiz results export returns 501 Not Implemented (future feature)."""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "quiz_results"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 501


async def test_learner_cannot_export_csv_returns_403(
    client: AsyncClient, learner_user
):
    """Learner cannot export CSV reports. [BRD-FR-003]"""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "enrollments"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 403


async def test_export_csv_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated CSV export returns 401."""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "enrollments"},
    )
    assert resp.status_code == 401


async def test_export_invalid_report_type_returns_422(
    client: AsyncClient, admin_user
):
    """Invalid report_type returns 422 Unprocessable Entity."""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "nonexistent_type"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 422


async def test_enrollments_csv_has_header_row(
    client: AsyncClient, admin_user, enrollment
):
    """Enrollments CSV export contains a header row. [BRD-FR-026]"""
    resp = await client.post(
        "/api/v1/reports/export",
        json={"report_type": "enrollments"},
        headers=auth_headers(admin_user["token"]),
    )
    assert resp.status_code == 200
    lines = resp.text.strip().splitlines()
    assert len(lines) >= 1
    # First line is the CSV header
    header = lines[0].lower()
    assert "user" in header or "email" in header or "course" in header or "enrollment" in header
