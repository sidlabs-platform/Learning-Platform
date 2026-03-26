"""Authentication router — login, register, me, and logout endpoints.

Provides:
- ``POST /api/v1/auth/login``    — Authenticate with email+password, receive JWT.
- ``POST /api/v1/auth/register`` — Register a new user account (learner by default).
- ``GET  /api/v1/auth/me``       — Return the currently authenticated user's profile.
- ``POST /api/v1/auth/logout``   — Client-side token invalidation (stateless logout).

All routes are thin handlers that delegate business logic to
:mod:`src.services.auth_service`.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_db
from src.dependencies.rbac import get_current_user
from src.models import User
from src.schemas.auth import TokenResponse, UserCreate, UserResponse
from src.services.auth_service import authenticate_user, create_access_token, create_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return JWT token",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user credentials and issue a signed JWT access token.

    Accepts ``application/x-www-form-urlencoded`` (``username`` + ``password``
    fields) as required by the OAuth2 password flow used by ``OAuth2PasswordBearer``.

    Args:
        form_data: URL-encoded login form containing ``username`` (email) and
            ``password`` fields.
        db: Async database session injected by FastAPI.

    Returns:
        :class:`~src.schemas.auth.TokenResponse` containing the signed JWT,
        token type, and expiry in seconds.

    Raises:
        HTTPException: 401 Unauthorized if the credentials are invalid.
        HTTPException: 403 Forbidden if the account is inactive.
    """
    settings = get_settings()
    user = await authenticate_user(db, form_data.username, form_data.password)
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        secret_key=settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
        expires_delta=expires_delta,
    )
    logger.info("User logged in: user_id=%d role=%s", user.id, user.role.value)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new user account.

    The default role is ``learner`` unless explicitly overridden in the
    request body.  Passwords are hashed with bcrypt before storage.

    Args:
        user_in: Validated registration payload from the request body.
        db: Async database session injected by FastAPI.

    Returns:
        :class:`~src.schemas.auth.UserResponse` representing the new account.

    Raises:
        HTTPException: 409 Conflict if the email address is already registered.
    """
    user = await create_user(db, user_in)
    logger.info("New user registered: user_id=%d email=%s role=%s", user.id, user.email, user.role.value)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the currently authenticated user's profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the authenticated user's profile.

    Requires a valid ``Authorization: Bearer <token>`` header.

    Args:
        current_user: The authenticated user resolved from the JWT by
            :func:`~src.dependencies.rbac.get_current_user`.

    Returns:
        :class:`~src.schemas.auth.UserResponse` for the current user.
    """
    return current_user


@router.post(
    "/logout",
    summary="Logout (client-side token invalidation)",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Log the current user out.

    Because the platform uses stateless JWTs there is no server-side session
    to invalidate.  Clients must discard the stored token on receipt of this
    response.

    Args:
        current_user: The authenticated user resolved from the JWT.  Ensures
            the endpoint is protected and only callable with a valid token.

    Returns:
        A confirmation message dict.
    """
    logger.info("User logged out: user_id=%d", current_user.id)
    return {"message": "Logged out successfully"}
