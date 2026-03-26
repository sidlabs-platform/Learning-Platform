# Task: Implement RBAC Dependency Functions

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-010             |
| **Story**    | STORY-005            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Implement the four reusable FastAPI `Depends()` functions for RBAC: `require_authenticated_user`, `require_admin`, `require_learner`, and `require_own_data`. These dependencies are used by every protected route in the system.

## Implementation Details

**Files to create/modify:**
- `src/auth/dependencies.py` — four dependency functions

**Approach:**
```python
from fastapi import Request, HTTPException, status, Depends

async def require_authenticated_user(request: Request) -> TokenPayload:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return decode_access_token(token)
    except (TokenExpiredError, InvalidCredentialsError):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

async def require_admin(user: TokenPayload = Depends(require_authenticated_user)) -> TokenPayload:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def require_learner(user: TokenPayload = Depends(require_authenticated_user)) -> TokenPayload:
    if user.role != "learner":
        raise HTTPException(status_code=403, detail="Learner access required")
    return user

def require_own_data(target_user_id: str, user: TokenPayload = Depends(require_authenticated_user)) -> TokenPayload:
    if user.role != "admin" and user.sub != target_user_id:
        raise HTTPException(status_code=403, detail="Access to other users' data is not permitted")
    return user
```

## API Changes

N/A — dependency injection only, no new endpoints.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                          |
|-------------------|-------------------------------------------------|
| TASK-009          | `decode_access_token()` from auth service required |

**Wave:** 4

## Acceptance Criteria

- [ ] `require_authenticated_user` raises `401` when no cookie is present
- [ ] `require_authenticated_user` raises `401` when token is expired or tampered
- [ ] `require_admin` raises `403` for a valid Learner token
- [ ] `require_admin` succeeds for a valid Admin token
- [ ] `require_own_data` raises `403` when a Learner requests another user's data
- [ ] `require_own_data` succeeds when an Admin requests any user's data (admin bypass)

## Test Requirements

- **Unit tests:** Test each dependency function with mock `Request` objects containing valid/invalid/missing cookies
- **Integration tests:** Test admin-only endpoints with Learner token → 403; with Admin token → 200
- **Edge cases:** Expired token; malformed JWT; missing `role` claim in payload

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-005        |
| Epic     | EPIC-002         |
| BRD      | BRD-FR-003, BRD-FR-004, BRD-NFR-004 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
