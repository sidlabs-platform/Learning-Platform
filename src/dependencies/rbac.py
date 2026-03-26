"""RBAC dependency functions for FastAPI route protection.

Provides three dependency callables that extract and validate the current
user from the Bearer token, and enforce role-based access control:

- :func:`get_current_user` — decodes JWT, fetches user from DB.
- :func:`get_current_active_learner` — allows learners and admins.
- :func:`require_admin` — allows admins only; raises 403 for learners.

Usage example::

    from src.dependencies.rbac import require_admin, get_current_active_learner

    @router.get("/admin-only")
    async def admin_endpoint(current_user: User = Depends(require_admin)):
        ...

    @router.get("/learner")
    async def learner_endpoint(current_user: User = Depends(get_current_active_learner)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_db
from src.models import User, UserRole
from src.services.auth_service import decode_access_token, get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    settings=Depends(get_settings),
) -> User:
    """Extract and validate the JWT Bearer token, then return the current user.

    Args:
        token: The raw JWT string extracted from the ``Authorization: Bearer``
            header by the ``OAuth2PasswordBearer`` scheme.
        db: An active async SQLAlchemy session injected by FastAPI.
        settings: Application settings providing the signing secret and algorithm.

    Returns:
        The authenticated, active ``User`` ORM instance.

    Raises:
        HTTPException: 401 if the token payload has no ``sub`` claim, or if
            the user does not exist or is inactive.
    """
    payload = decode_access_token(
        token,
        settings.secret_key.get_secret_value(),
        settings.algorithm,
    )
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_learner(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require an authenticated user — both learners and admins are permitted.

    Admins can perform all learner actions, so this dependency simply
    forwards the authenticated user without role restriction.

    Args:
        current_user: The authenticated user resolved by :func:`get_current_user`.

    Returns:
        The authenticated ``User`` ORM instance (any role).
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require the ``admin`` role.  Raises 403 Forbidden for learners.

    Args:
        current_user: The authenticated user resolved by :func:`get_current_user`.

    Returns:
        The authenticated ``User`` ORM instance if the role is ``admin``.

    Raises:
        HTTPException: 403 Forbidden if the current user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
