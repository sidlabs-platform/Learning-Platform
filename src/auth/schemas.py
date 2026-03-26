"""
Pydantic v2 schemas for the Auth service.

Covers registration, login, JWT token representation, and password management.
All schemas use :pydantic:`ConfigDict(from_attributes=True)` where ORM instances
need to be serialised directly.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    """
    Supported platform roles.

    ``learner`` — can consume courses and track own progress.
    ``admin``   — can create/publish courses, manage learners, view reports.
    """

    learner = "learner"
    admin = "admin"


class Token(BaseModel):
    """JWT access token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Claims extracted from a decoded JWT.

    Used internally by FastAPI dependency functions to propagate identity.
    """

    user_id: str | None = None
    role: UserRole | None = None


class UserCreate(BaseModel):
    """
    Request body for ``POST /api/v1/auth/register``.

    ``password`` is accepted in plain-text here; the auth service hashes it
    before persisting.  The field is intentionally not a ``SecretStr`` so that
    Pydantic can validate minimum-length constraints easily.
    """

    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.learner


class UserRead(BaseModel):
    """
    Public representation of a user, safe to return in API responses.

    ``hashed_password`` is deliberately excluded.
    """

    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Request body for ``POST /api/v1/auth/login``."""

    email: str
    password: str


class PasswordChange(BaseModel):
    """Request body for ``POST /api/v1/auth/password``."""

    current_password: str
    new_password: str


__all__ = [
    "UserRole",
    "Token",
    "TokenData",
    "UserCreate",
    "UserRead",
    "UserLogin",
    "PasswordChange",
]
