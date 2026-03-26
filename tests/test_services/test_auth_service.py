"""Unit tests for the Auth service functions.

Traceability:
    BRD-FR-001: Password hashing/verification
    BRD-FR-002: Role enforcement
    TASK-007: Auth service implementation
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserCreate, UserRole
from src.auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    decode_access_token,
    get_user_by_email,
    get_user_by_id,
    hash_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def test_hash_password_returns_non_plaintext():
    """Hashed password is not the same as plaintext. [BRD-FR-001]"""
    plain = "MySecurePassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert len(hashed) > 0


def test_verify_password_correct_password_returns_true():
    """Correct password verifies successfully. [BRD-FR-001]"""
    plain = "MySecurePassword123!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong_password_returns_false():
    """Wrong password fails verification. [BRD-FR-001]"""
    hashed = hash_password("CorrectPassword!")
    assert verify_password("WrongPassword!", hashed) is False


def test_hash_password_same_input_produces_different_hashes():
    """bcrypt salting produces different hashes for the same plaintext."""
    plain = "SamePassword!"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)
    assert hash1 != hash2


# ---------------------------------------------------------------------------
# JWT token creation/decoding
# ---------------------------------------------------------------------------


def test_create_and_decode_access_token_round_trip():
    """Token round-trip preserves user_id and role claims. [BRD-FR-001]"""
    user_id = "test-user-123"
    role = "admin"
    token = create_access_token(data={"sub": user_id, "role": role})
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.user_id == user_id
    assert decoded.role == UserRole.admin


def test_decode_invalid_token_returns_none():
    """Malformed token decodes to None. [BRD-FR-001]"""
    decoded = decode_access_token("this.is.not.a.token")
    assert decoded is None


def test_decode_empty_token_returns_none():
    """Empty token decodes to None."""
    decoded = decode_access_token("")
    assert decoded is None


def test_create_token_with_learner_role():
    """Token with learner role decodes correctly. [BRD-FR-002]"""
    token = create_access_token(data={"sub": "user-456", "role": "learner"})
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.role == UserRole.learner


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


async def test_create_user_persists_to_db(db_session: AsyncSession):
    """create_user inserts a user record with hashed password. [BRD-FR-001]"""
    user_create = UserCreate(
        name="Test User",
        email="testuser@example.com",
        password="TestPass123!",
        role=UserRole.learner,
    )
    user = await create_user(user_create, db_session)
    await db_session.flush()

    assert user.id is not None
    assert user.email == "testuser@example.com"
    assert user.hashed_password != "TestPass123!"
    assert user.role == "learner"
    assert user.is_active is True


async def test_create_user_duplicate_email_raises_409(db_session: AsyncSession):
    """Duplicate email raises HTTPException 409. [BRD-FR-001]"""
    from fastapi import HTTPException

    user_create = UserCreate(
        name="Dup User",
        email="dup@example.com",
        password="TestPass123!",
    )
    await create_user(user_create, db_session)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await create_user(user_create, db_session)
    assert exc_info.value.status_code == 409


async def test_get_user_by_email_returns_user(db_session: AsyncSession):
    """get_user_by_email returns the user for a known email."""
    user_create = UserCreate(
        name="Lookup User",
        email="lookup@example.com",
        password="TestPass123!",
    )
    created = await create_user(user_create, db_session)
    await db_session.flush()

    found = await get_user_by_email("lookup@example.com", db_session)
    assert found is not None
    assert found.id == created.id


async def test_get_user_by_email_unknown_email_returns_none(db_session: AsyncSession):
    """get_user_by_email returns None for an unknown email."""
    result = await get_user_by_email("unknown@example.com", db_session)
    assert result is None


async def test_get_user_by_id_returns_user(db_session: AsyncSession):
    """get_user_by_id returns the correct user."""
    user_create = UserCreate(
        name="ID User",
        email="iduser@example.com",
        password="TestPass123!",
    )
    created = await create_user(user_create, db_session)
    await db_session.flush()

    found = await get_user_by_id(created.id, db_session)
    assert found is not None
    assert found.email == "iduser@example.com"


async def test_authenticate_user_valid_credentials(db_session: AsyncSession):
    """authenticate_user returns user for valid credentials. [BRD-FR-001]"""
    user_create = UserCreate(
        name="Auth User",
        email="authuser@example.com",
        password="Pass123!",
    )
    await create_user(user_create, db_session)
    await db_session.flush()

    user = await authenticate_user("authuser@example.com", "Pass123!", db_session)
    assert user is not None
    assert user.email == "authuser@example.com"


async def test_authenticate_user_wrong_password_returns_none(db_session: AsyncSession):
    """authenticate_user returns None for wrong password. [BRD-FR-001]"""
    user_create = UserCreate(
        name="Wrong Pass User",
        email="wrongpass@example.com",
        password="CorrectPass!",
    )
    await create_user(user_create, db_session)
    await db_session.flush()

    user = await authenticate_user("wrongpass@example.com", "WrongPass!", db_session)
    assert user is None


async def test_authenticate_user_unknown_email_returns_none(db_session: AsyncSession):
    """authenticate_user returns None for unknown email."""
    user = await authenticate_user("ghost@example.com", "AnyPass!", db_session)
    assert user is None


async def test_authenticate_inactive_user_returns_none(db_session: AsyncSession):
    """authenticate_user returns None for an inactive user. [BRD-FR-001]"""
    from src.models import User
    from src.auth.service import hash_password
    import uuid
    from datetime import datetime

    inactive = User(
        id=str(uuid.uuid4()),
        name="Inactive User",
        email="inactive@example.com",
        hashed_password=hash_password("Pass123!"),
        role="learner",
        created_at=datetime.utcnow(),
        is_active=False,
    )
    db_session.add(inactive)
    await db_session.flush()

    user = await authenticate_user("inactive@example.com", "Pass123!", db_session)
    assert user is None
