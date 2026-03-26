"""Pydantic v2 schemas for authentication and user management.

These models cover:
- Login / token issuance
- User registration and profile responses
- Admin user updates
"""

from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """Role assigned to a platform user."""

    learner = "learner"
    admin = "admin"


class LoginRequest(BaseModel):
    """Request body for the POST /auth/login endpoint."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT access-token response returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until the token expires


class UserCreate(BaseModel):
    """Request body for registering a new user."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = UserRole.learner


class UserResponse(BaseModel):
    """Public-facing user representation returned by API endpoints."""

    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Request body for partially updating an existing user (admin only)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None
