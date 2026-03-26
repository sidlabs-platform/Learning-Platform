"""
FastAPI router for authentication endpoints.

Provides user registration, login (with HTTP-only cookie), logout, profile
retrieval, and password change functionality.  All business logic is delegated
to :mod:`src.auth.service`; this module is a thin wiring layer.

Endpoints (relative — the ``/api/v1/auth`` prefix is applied in ``main.py``):

- ``POST /register`` — create a new user account
- ``POST /login``    — authenticate and set an ``access_token`` cookie
- ``POST /logout``   — clear the ``access_token`` cookie
- ``GET  /me``       — return the current user's profile
- ``POST /password`` — change the current user's password
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.auth.schemas import (
    PasswordChange,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from src.auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    hash_password,
    verify_password,
)
from src.config.settings import get_settings
from src.database import get_db
from src.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Create a new user account.

    Accepts a :class:`~src.auth.schemas.UserCreate` payload, delegates to the
    auth service for persistence, and returns the public user representation.

    Args:
        user_create: Validated registration payload (name, email, password, role).
        db: Async database session injected by FastAPI.

    Returns:
        The newly created user as a :class:`~src.auth.schemas.UserRead`.

    Raises:
        HTTPException (409): If the email address is already registered.
    """
    user = await create_user(user_create, db)
    await db.commit()
    await db.refresh(user)
    logger.info("New user registered: user_id=%s", user.id)
    return UserRead.model_validate(user)


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and obtain a token",
)
async def login(
    user_login: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Authenticate a user and set an HTTP-only access-token cookie.

    Verifies the supplied email/password combination.  On success, creates a
    JWT containing the user's ID and role, sets it as an HTTP-only cookie on
    the response, and returns the token in the JSON body.

    Args:
        user_login: Validated login payload (email, password).
        response: The outgoing :class:`~fastapi.Response` used to set the cookie.
        db: Async database session injected by FastAPI.

    Returns:
        A :class:`~src.auth.schemas.Token` containing the JWT access token.

    Raises:
        HTTPException (401): If the email is not found or the password is wrong.
    """
    user = await authenticate_user(user_login.email, user_login.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    settings = get_settings()
    token = create_access_token(data={"sub": user.id, "role": user.role})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )

    logger.info("User logged in: user_id=%s", user.id)
    return Token(access_token=token)


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------


@router.post(
    "/logout",
    summary="Log out and clear the access-token cookie",
)
async def logout(response: Response) -> dict[str, str]:
    """Clear the ``access_token`` HTTP-only cookie, effectively logging the user out.

    No authentication is required — the endpoint is idempotent and safe to call
    even if the cookie has already expired or been removed.

    Args:
        response: The outgoing :class:`~fastapi.Response` used to delete the cookie.

    Returns:
        A JSON object with a success message.
    """
    response.delete_cookie(key="access_token")
    logger.info("User logged out (cookie cleared).")
    return {"message": "Successfully logged out."}


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    """Return the profile of the currently authenticated user.

    Requires a valid ``access_token`` cookie or ``Authorization: Bearer``
    header.

    Args:
        current_user: The authenticated, active user injected by the
            :func:`~src.auth.dependencies.get_current_active_user` dependency.

    Returns:
        The user's public profile as a :class:`~src.auth.schemas.UserRead`.
    """
    return UserRead.model_validate(current_user)


# ---------------------------------------------------------------------------
# POST /password
# ---------------------------------------------------------------------------


@router.post(
    "/password",
    summary="Change the current user's password",
)
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Change the authenticated user's password.

    The caller must supply the current password for verification as well as the
    desired new password.

    Args:
        payload: Validated :class:`~src.auth.schemas.PasswordChange` body
            (current_password, new_password).
        current_user: The authenticated, active user.
        db: Async database session injected by FastAPI.

    Returns:
        A JSON object confirming the password was changed.

    Raises:
        HTTPException (400): If the current password is incorrect.
    """
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    await db.refresh(current_user)

    logger.info("Password changed: user_id=%s", current_user.id)
    return {"message": "Password updated successfully."}
