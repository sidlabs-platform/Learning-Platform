# Task: Implement Auth Pydantic Models

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-008             |
| **Story**    | STORY-004            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement all Pydantic v2 request/response models for the Auth service: `LoginRequest`, `TokenPayload`, `UserOut`, `LoginResponse`, and `LogoutResponse`. These schemas enforce input validation and define the API contract for authentication endpoints.

## Implementation Details

**Files to create/modify:**
- `src/auth/__init__.py` — empty package marker
- `src/auth/models.py` — Pydantic models: `LoginRequest`, `TokenPayload`, `UserOut`, `LoginResponse`, `LogoutResponse`
- `src/auth/exceptions.py` — `InvalidCredentialsError`, `InsufficientPermissionsError`, `TokenExpiredError` as custom exception classes

**Approach:**
```python
# models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class TokenPayload(BaseModel):
    sub: str          # User UUID
    role: Literal["learner", "admin"]
    exp: int

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Literal["learner", "admin"]
    created_at: datetime
    model_config = {"from_attributes": True}

class LoginResponse(BaseModel):
    message: str = "Login successful"
    user: UserOut

class LogoutResponse(BaseModel):
    message: str = "Logout successful"
```

## API Changes

N/A — models only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                              |
|-------------------|-------------------------------------|
| TASK-003          | FastAPI app must exist (for imports)|

**Wave:** 2

## Acceptance Criteria

- [ ] `LoginRequest` rejects emails without `@` and passwords shorter than 8 chars
- [ ] `TokenPayload.role` only accepts `"learner"` or `"admin"` (Literal validation)
- [ ] `UserOut` does not include `password_hash` field
- [ ] `UserOut` can be created from SQLAlchemy ORM `User` object (`from_attributes=True`)
- [ ] All exception classes are importable from `src.auth.exceptions`

## Test Requirements

- **Unit tests:** Test `LoginRequest` with valid and invalid email/password combos; test `TokenPayload` with invalid role
- **Integration tests:** N/A
- **Edge cases:** `LoginRequest` with exactly 8-char password (boundary); `TokenPayload` with role=`"superadmin"` fails

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-004        |
| Epic     | EPIC-002         |
| BRD      | BRD-FR-001, BRD-FR-002 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
