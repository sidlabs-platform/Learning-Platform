# Task: Implement Auth Service (Password, JWT, User Authentication)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-009             |
| **Story**    | STORY-004            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the core authentication business logic: password hashing and verification with bcrypt, JWT token creation and decoding with HMAC-SHA256, and the `authenticate_user()` function that queries the database and validates credentials.

## Implementation Details

**Files to create/modify:**
- `src/auth/service.py` — `verify_password()`, `hash_password()`, `create_access_token()`, `decode_access_token()`, `authenticate_user()`

**Approach:**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")

def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except JWTError:
        raise InvalidCredentialsError("Invalid token")

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Invalid email or password")
    return user
```

## API Changes

N/A — service layer only.

## Data Model Changes

N/A — reads from `users` table.

## Dependencies

| Prerequisite Task | Reason                                       |
|-------------------|----------------------------------------------|
| TASK-005          | User ORM model required for `authenticate_user()` |
| TASK-008          | Auth Pydantic models (TokenPayload, exceptions) required |

**Wave:** 3

## Acceptance Criteria

- [ ] `verify_password("correct", hash_password("correct"))` returns `True`
- [ ] `verify_password("wrong", hash_password("correct"))` returns `False`
- [ ] `decode_access_token(create_access_token({"sub": "id", "role": "learner"}))` returns `TokenPayload`
- [ ] `decode_access_token(expired_token)` raises `TokenExpiredError`
- [ ] `authenticate_user()` raises `InvalidCredentialsError` for unknown email or wrong password
- [ ] Raw password is never stored; only bcrypt hash written to DB

## Test Requirements

- **Unit tests:** Test `verify_password`, `hash_password`, `create_access_token`, `decode_access_token` with valid/expired/tampered tokens
- **Integration tests:** Test `authenticate_user()` with a test DB containing a seeded user
- **Edge cases:** Token with tampered payload; expired token; missing `sub` or `role` claim

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-004        |
| Epic     | EPIC-002         |
| BRD      | BRD-FR-001, BRD-NFR-004 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
