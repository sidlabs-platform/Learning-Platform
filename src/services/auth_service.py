"""Authentication service — password hashing, JWT creation/decoding, and user lookup.

This module provides all authentication business logic for the Learning Platform:

- **Password management**: bcrypt hashing and verification via ``passlib``.
- **JWT tokens**: HS256-signed access tokens created and decoded via ``python-jose``.
- **User queries**: Async helpers to fetch users by email or primary key.
- **Authentication**: Validates email + password credentials and raises appropriate
  ``HTTPException`` responses on failure.
- **Registration**: Creates new user records, enforcing email uniqueness.

All functions are stateless aside from the shared ``pwd_context`` — they receive
the database session and settings as parameters so they remain easily testable.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.schemas.auth import UserCreate

# ---------------------------------------------------------------------------
# Password context — bcrypt with automatic deprecation handling
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        password: The raw plain-text password to hash.

    Returns:
        A bcrypt-hashed string suitable for database storage.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password: The raw password submitted by the user.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        ``True`` if the password matches the hash, ``False`` otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------


def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data: Claims to encode in the token payload (e.g. ``{"sub": "1", "role": "admin"}``).
        secret_key: The HMAC secret used to sign the token.
        algorithm: The signing algorithm (e.g. ``"HS256"``).
        expires_delta: Optional custom expiry window. Defaults to 480 minutes (8 hours).

    Returns:
        A compact JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=480))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_access_token(token: str, secret_key: str, algorithm: str) -> dict:
    """Decode and validate a JWT access token.

    Args:
        token: The compact JWT string to decode.
        secret_key: The HMAC secret used to verify the signature.
        algorithm: The expected signing algorithm (e.g. ``"HS256"``).

    Returns:
        The decoded payload as a plain ``dict``.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, or
            tampered with.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Fetch a User record by email address.

    Args:
        db: An active async SQLAlchemy session.
        email: The email address to search for (case-sensitive).

    Returns:
        The matching ``User`` ORM instance, or ``None`` if not found.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Fetch a User record by primary key.

    Args:
        db: An active async SQLAlchemy session.
        user_id: The integer primary key of the user.

    Returns:
        The matching ``User`` ORM instance, or ``None`` if not found.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Core authentication logic
# ---------------------------------------------------------------------------


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate a user with email and password credentials.

    Queries the database for a user with the given email, verifies the
    bcrypt-hashed password, and confirms the account is active.

    Args:
        db: An active async SQLAlchemy session.
        email: The user's registered email address.
        password: The plain-text password submitted by the user.

    Returns:
        The authenticated ``User`` ORM instance.

    Raises:
        HTTPException: 401 Unauthorized if the email is not found or the
            password does not match.
        HTTPException: 403 Forbidden if the account is marked inactive.
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return user


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user account.

    Checks for an existing account with the same email before inserting.
    The plain-text password is hashed with bcrypt before storage — the raw
    password is never persisted.

    Args:
        db: An active async SQLAlchemy session.
        user_in: Validated registration data from the request body.

    Returns:
        The newly created ``User`` ORM instance (with ``id`` populated after flush).

    Raises:
        HTTPException: 409 Conflict if the email address is already registered.
    """
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user
