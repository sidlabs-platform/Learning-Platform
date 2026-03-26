"""Authentication service for the Learning Platform MVP.

Provides password hashing and verification (bcrypt via passlib), JWT token
creation and decoding (python-jose with HMAC-SHA256), and user management
functions that interact with the database.

Security notes:
- Passwords are never stored in plaintext; only bcrypt hashes are persisted.
- JWT secrets are loaded from ``settings.secret_key`` (a ``SecretStr``).
- Tokens and passwords are never written to log output.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import TokenData, UserCreate, UserRole
from src.config.settings import get_settings
from src.models import User

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Password hashing context (bcrypt)
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Public helpers — password
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        password: The plain-text password to hash.

    Returns:
        A bcrypt-hashed string safe for database storage.
    """
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain: The candidate plain-text password.
        hashed: The stored bcrypt hash.

    Returns:
        ``True`` if the password matches the hash, ``False`` otherwise.
    """
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# Public helpers — JWT
# ---------------------------------------------------------------------------


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data: Claims to embed in the token payload.  Must include ``"sub"``
            (user ID string) and ``"role"`` fields.
        expires_delta: Optional custom expiry duration.  Defaults to
            ``settings.access_token_expire_minutes``.

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT access token.

    Args:
        token: The raw JWT string to decode.

    Returns:
        A :class:`~src.auth.schemas.TokenData` instance with ``user_id`` and
        ``role`` extracted from the token claims, or ``None`` if the token is
        invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=["HS256"],
        )
        user_id: Optional[str] = payload.get("sub")
        role_str: Optional[str] = payload.get("role")
        if user_id is None:
            return None
        role = UserRole(role_str) if role_str else None
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Async database helpers
# ---------------------------------------------------------------------------


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """Fetch a :class:`~src.models.User` by e-mail address.

    Args:
        email: The e-mail address to look up (case-sensitive).
        db: An open async database session.

    Returns:
        The matching :class:`~src.models.User` instance, or ``None`` if not found.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: str, db: AsyncSession) -> Optional[User]:
    """Fetch a :class:`~src.models.User` by primary key.

    Args:
        user_id: The UUID string of the user.
        db: An open async database session.

    Returns:
        The matching :class:`~src.models.User` instance, or ``None`` if not found.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession,
) -> Optional[User]:
    """Verify credentials and return the matching user.

    Queries the database for a user with the given e-mail address and verifies
    the supplied plain-text password against the stored bcrypt hash.

    Args:
        email: The candidate e-mail address.
        password: The candidate plain-text password.
        db: An open async database session.

    Returns:
        The authenticated :class:`~src.models.User` if credentials are valid,
        or ``None`` if the e-mail is not found or the password is incorrect.
    """
    user = await get_user_by_email(email, db)
    if user is None:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    logger.info("User authenticated: user_id=%s", user.id)
    return user


async def create_user(user_create: UserCreate, db: AsyncSession) -> User:
    """Create and persist a new :class:`~src.models.User`.

    Args:
        user_create: The validated :class:`~src.auth.schemas.UserCreate` payload.
        db: An open async database session.

    Returns:
        The newly created :class:`~src.models.User` instance.

    Raises:
        :class:`fastapi.HTTPException` (409) if the e-mail address is already
        registered.
    """
    existing = await get_user_by_email(user_create.email, db)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    user = User(
        id=str(uuid.uuid4()),
        name=user_create.name,
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        role=user_create.role.value,
        created_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(user)
    await db.flush()
    logger.info("User registered: user_id=%s role=%s", user.id, user.role)
    return user
