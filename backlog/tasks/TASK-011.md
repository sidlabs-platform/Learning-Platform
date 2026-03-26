# Task: Implement Auth Router (Login, Logout, Me Endpoints)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-011             |
| **Story**    | STORY-004            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Implement the auth API router with three endpoints: `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, and `GET /api/v1/auth/me`. The login endpoint sets an HTTP-only JWT cookie; logout clears it; me returns the current user's profile. All auth events must be logged.

## Implementation Details

**Files to create/modify:**
- `src/auth/router.py` — FastAPI `APIRouter` with login, logout, me endpoints

**Approach:**
```python
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.email, request.password)
    token = create_access_token({"sub": user.id, "role": user.role})
    response.set_cookie(
        key="access_token", value=token,
        httponly=True, samesite="strict",
        secure=settings.environment == "production",
        max_age=settings.access_token_expire_minutes * 60
    )
    logger.info(f"Login successful: user_id={user.id} role={user.role}")
    return LoginResponse(user=UserOut.model_validate(user))

@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response):
    response.delete_cookie("access_token")
    return LogoutResponse()

@router.get("/me", response_model=UserOut)
async def me(current_user: TokenPayload = Depends(require_authenticated_user), db: AsyncSession = Depends(get_db)):
    # Fetch full user from DB using current_user.sub
    ...
```

Register `router` in `src/main.py`.

## API Changes

| Endpoint                | Method | Description                                          |
|-------------------------|--------|------------------------------------------------------|
| `/api/v1/auth/login`    | POST   | Authenticate user; set HTTP-only JWT cookie          |
| `/api/v1/auth/logout`   | POST   | Clear JWT cookie                                     |
| `/api/v1/auth/me`       | GET    | Return current authenticated user profile            |

**Request body (login):**
```json
{"email": "user@example.com", "password": "mypassword"}
```

**Response body (login):**
```json
{"message": "Login successful", "user": {"id": "...", "name": "...", "email": "...", "role": "learner", "created_at": "..."}}
```

## Data Model Changes

N/A — reads from `users` table.

## Dependencies

| Prerequisite Task | Reason                                              |
|-------------------|-----------------------------------------------------|
| TASK-009          | Auth service functions required                     |
| TASK-010          | RBAC dependencies required for `me` endpoint        |

**Wave:** 5

## Acceptance Criteria

- [ ] `POST /api/v1/auth/login` with valid credentials returns 200 + JWT cookie
- [ ] Cookie is `HttpOnly`, `SameSite=strict`; `Secure=True` in production environment
- [ ] `POST /api/v1/auth/login` with invalid credentials returns 401
- [ ] `POST /api/v1/auth/logout` clears the cookie
- [ ] `GET /api/v1/auth/me` returns user profile without `password_hash`
- [ ] Successful login creates a log entry; failed login attempt creates a log entry

## Test Requirements

- **Unit tests:** Test login with valid/invalid credentials; test logout clears cookie
- **Integration tests:** Full flow: login → me → logout → me returns 401
- **Edge cases:** Login with non-existent email; login with correct email but wrong password; me without cookie

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-004        |
| Epic     | EPIC-002         |
| BRD      | BRD-FR-001, BRD-NFR-013 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
