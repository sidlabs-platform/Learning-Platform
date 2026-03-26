"""
FastAPI dependency functions for authentication and role-based access control.

Provides ``get_current_user`` (extracts JWT from cookie or Authorization header),
``get_current_active_user`` (checks ``is_active``), and role-specific guards
``require_learner`` and ``require_admin``.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import decode_access_token
from src.database import get_db
from src.models import User

logger = logging.getLogger(__name__)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate a JWT token, returning the authenticated user.

    Checks for the token in:
    1. HTTP-only cookie named ``access_token``.
    2. ``Authorization: Bearer <token>`` header as a fallback.

    Args:
        request: The incoming HTTP request.
        db: An open async database session.

    Returns:
        The :class:`~src.models.User` identified by the token.

    Raises:
        :class:`fastapi.HTTPException` (401) if the token is missing, invalid,
        or the user does not exist in the database.
    """
    token: Optional[str] = request.cookies.get("access_token")

    if token is None:
        auth_header: Optional[str] = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_data = decode_access_token(token)
    if token_data is None or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user: Optional[User] = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify that the authenticated user account is active.

    Args:
        current_user: The user returned by :func:`get_current_user`.

    Returns:
        The same :class:`~src.models.User` if active.

    Raises:
        :class:`fastapi.HTTPException` (401) if the user's ``is_active`` flag
        is ``False``.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return current_user


async def require_learner(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require the current user to have the ``learner`` or ``admin`` role.

    Args:
        current_user: The active authenticated user.

    Returns:
        The :class:`~src.models.User` if role check passes.

    Raises:
        :class:`fastapi.HTTPException` (403) if the user is not a learner or admin.
    """
    if current_user.role not in ("learner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Learner access required",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require the current user to have the ``admin`` role.

    Args:
        current_user: The active authenticated user.

    Returns:
        The :class:`~src.models.User` if role check passes.

    Raises:
        :class:`fastapi.HTTPException` (403) if the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


__all__ = [
    "get_current_user",
    "get_current_active_user",
    "require_learner",
    "require_admin",
]
