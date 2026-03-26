"""API tests for the Authentication service.

Covers registration, login, logout, profile retrieval, and password change.

Traceability:
    BRD-FR-001: Sign-in with email/password
    BRD-FR-002: Two roles (learner / admin)
    BRD-FR-003: Admin-only endpoint enforcement
    TASK-006: Auth router implementation
"""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register
# ---------------------------------------------------------------------------


async def test_register_returns_201_with_user_data(client: AsyncClient):
    """Successful registration returns 201 with public user fields. [BRD-FR-001]"""
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "SecurePass1!",
        "role": "learner",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["name"] == "Alice"
    assert data["role"] == "learner"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_admin_role_succeeds(client: AsyncClient):
    """Admin role can be set during registration. [BRD-FR-002]"""
    payload = {
        "name": "Bob Admin",
        "email": "bobadmin@example.com",
        "password": "SecurePass1!",
        "role": "admin",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    assert resp.json()["role"] == "admin"


async def test_register_duplicate_email_returns_409(client: AsyncClient):
    """Duplicate email registration returns 409 Conflict. [BRD-FR-001]"""
    payload = {
        "name": "Carol",
        "email": "carol@example.com",
        "password": "SecurePass1!",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


async def test_register_missing_email_returns_422(client: AsyncClient):
    """Missing required email field returns 422 Unprocessable Entity."""
    payload = {"name": "Dan", "password": "SecurePass1!"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_register_invalid_email_format_returns_422(client: AsyncClient):
    """Invalid email format returns 422 Unprocessable Entity."""
    payload = {"name": "Eve", "email": "not-an-email", "password": "SecurePass1!"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_register_invalid_role_returns_422(client: AsyncClient):
    """Unknown role value returns 422 Unprocessable Entity. [BRD-FR-002]"""
    payload = {
        "name": "Frank",
        "email": "frank@example.com",
        "password": "SecurePass1!",
        "role": "superuser",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------


async def test_login_with_valid_credentials_returns_token(client: AsyncClient):
    """Valid credentials return a 200 with access_token. [BRD-FR-001]"""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Grace", "email": "grace@example.com", "password": "Pass123!"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "grace@example.com", "password": "Pass123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_sets_httponly_cookie(client: AsyncClient):
    """Successful login sets an HTTP-only access_token cookie. [BRD-FR-001]"""
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Heidi", "email": "heidi@example.com", "password": "Pass123!"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "heidi@example.com", "password": "Pass123!"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.cookies


async def test_login_wrong_password_returns_401(client: AsyncClient):
    """Wrong password returns 401. [BRD-FR-001]"""
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Ivan", "email": "ivan@example.com", "password": "Pass123!"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "ivan@example.com", "password": "WrongPass!"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(client: AsyncClient):
    """Unknown email returns 401. [BRD-FR-001]"""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Pass123!"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/logout
# ---------------------------------------------------------------------------


async def test_logout_clears_cookie_and_returns_200(client: AsyncClient):
    """Logout returns 200 and clears the access_token cookie."""
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Judy", "email": "judy@example.com", "password": "Pass123!"},
    )
    await client.post(
        "/api/v1/auth/login",
        json={"email": "judy@example.com", "password": "Pass123!"},
    )
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


async def test_logout_without_login_returns_200(client: AsyncClient):
    """Logout is idempotent — works even without a prior login."""
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/auth/me
# ---------------------------------------------------------------------------


async def test_get_me_returns_current_user_profile(client: AsyncClient, learner_user):
    """Authenticated user gets their own profile. [BRD-FR-001]"""
    resp = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == learner_user["user"].id
    assert data["email"] == learner_user["user"].email
    assert "hashed_password" not in data


async def test_get_me_without_token_returns_401(client: AsyncClient):
    """No token returns 401. [BRD-FR-003]"""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_get_me_with_invalid_token_returns_401(client: AsyncClient):
    """Invalid/malformed token returns 401."""
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer this.is.not.valid"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/password
# ---------------------------------------------------------------------------


async def test_change_password_with_correct_current_password_returns_200(
    client: AsyncClient, learner_user
):
    """Valid current password allows password change."""
    resp = await client.post(
        "/api/v1/auth/password",
        json={"current_password": learner_user["password"], "new_password": "NewPass456!"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


async def test_change_password_wrong_current_password_returns_400(
    client: AsyncClient, learner_user
):
    """Wrong current password returns 400 Bad Request."""
    resp = await client.post(
        "/api/v1/auth/password",
        json={"current_password": "WrongPassword!", "new_password": "NewPass456!"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 400


async def test_change_password_unauthenticated_returns_401(client: AsyncClient):
    """Password change without auth token returns 401."""
    resp = await client.post(
        "/api/v1/auth/password",
        json={"current_password": "Old!", "new_password": "New!"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Role-based access — learner vs admin
# ---------------------------------------------------------------------------


async def test_learner_can_access_own_profile(client: AsyncClient, learner_user):
    """Learner role can access protected endpoints. [BRD-FR-002]"""
    resp = await client.get(
        "/api/v1/auth/me", headers=auth_headers(learner_user["token"])
    )
    assert resp.status_code == 200


async def test_admin_can_access_own_profile(client: AsyncClient, admin_user):
    """Admin role can access protected endpoints. [BRD-FR-002]"""
    resp = await client.get(
        "/api/v1/auth/me", headers=auth_headers(admin_user["token"])
    )
    assert resp.status_code == 200
