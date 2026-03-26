# Story: User Sign-In and JWT Session Management

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-004            |
| **Epic**     | EPIC-002             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** user (Learner or Admin),
**I want** to sign in with my email and password and receive a secure session,
**so that** I can access the features appropriate to my role without re-authenticating on every page load.

## Acceptance Criteria

1. **Given** a valid email and password,
   **When** `POST /api/v1/auth/login` is called,
   **Then** the response is `200 OK` with `{ "message": "Login successful", "user": {...} }` and an HTTP-only, `SameSite=Strict` cookie named `access_token` is set.

2. **Given** an invalid password or unknown email,
   **When** `POST /api/v1/auth/login` is called,
   **Then** the response is `401 Unauthorized` with `{ "detail": "Invalid credentials" }` and no cookie is set.

3. **Given** an authenticated session,
   **When** `POST /api/v1/auth/logout` is called,
   **Then** the `access_token` cookie is cleared and the response is `200 OK`.

4. **Given** an authenticated session,
   **When** `GET /api/v1/auth/me` is called,
   **Then** the response returns the current user's `id`, `name`, `email`, and `role` (no `passwordHash`).

5. **Given** a failed login attempt,
   **When** the application logs are checked,
   **Then** a structured log entry records the event with the email (not the password) and timestamp.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                 |
|---------------|---------------------------------------------------|
| BRD-FR-001    | COMP-001 Auth Service — login endpoint            |
| BRD-FR-002    | COMP-001 Auth Service — role enum                 |
| BRD-NFR-004   | COMP-001 Auth Service — 401/403 enforcement       |
| BRD-NFR-005   | COMP-001 Auth Service — secrets not in responses  |
| BRD-NFR-013   | COMP-001 Auth Service — auth event logging        |

## Tasks Breakdown

| Task ID  | Description                                                | Estimate |
|----------|------------------------------------------------------------|----------|
| TASK-008 | Implement auth Pydantic models (LoginRequest, TokenPayload, UserOut) | 2h |
| TASK-009 | Implement auth service (password hash, JWT create/decode, authenticate_user) | 4h |
| TASK-011 | Implement auth router (login, logout, me endpoints)        | 3h       |

## UI/UX Notes

Login page is covered in EPIC-007 (STORY-025). This story covers the API only.

## Technical Notes

- **Stack:** FastAPI, python-jose (HMAC-SHA256), passlib (bcrypt), pydantic-settings
- **Key considerations:** JWT stored in HTTP-only cookie; token TTL configurable (default 8h); `create_access_token()` uses `sub=userId` and `role` claims; passwords hashed with `passlib.CryptContext(schemes=["bcrypt"])`
- **Configuration:** `SECRET_KEY` (required), `ACCESS_TOKEN_EXPIRE_MINUTES` (optional, default 480)

## Dependencies

- STORY-002 (users table must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
