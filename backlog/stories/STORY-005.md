# Story: Role-Based Access Control (RBAC) Dependencies

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-005            |
| **Epic**     | EPIC-002             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3 points             |
| **Priority** | P0                   |

## User Story

**As a** backend developer,
**I want** reusable FastAPI `Depends()` functions for authentication and role enforcement,
**so that** any route can be secured with a single dependency declaration and no role logic is duplicated across handlers.

## Acceptance Criteria

1. **Given** a request with no `access_token` cookie,
   **When** any protected endpoint with `Depends(require_authenticated_user)` is called,
   **Then** the response is `401 Unauthorized`.

2. **Given** a valid Learner JWT cookie,
   **When** an Admin-only endpoint with `Depends(require_admin)` is called,
   **Then** the response is `403 Forbidden`.

3. **Given** a valid Admin JWT cookie,
   **When** an Admin-only endpoint is called,
   **Then** the request proceeds normally.

4. **Given** a Learner requesting another Learner's data (e.g., progress records for userId != own),
   **When** `require_own_data()` is applied,
   **Then** the response is `403 Forbidden`.

## BRD & Design References

| BRD ID        | HLD/LLD Component                               |
|---------------|-------------------------------------------------|
| BRD-FR-003    | COMP-001 Auth Service — admin-only restriction  |
| BRD-FR-004    | COMP-001 Auth Service — own data isolation      |
| BRD-NFR-004   | COMP-001 Auth Service — RBAC on every endpoint  |

## Tasks Breakdown

| Task ID  | Description                                                         | Estimate |
|----------|---------------------------------------------------------------------|----------|
| TASK-010 | Implement RBAC dependency functions (require_authenticated_user, require_admin, require_learner, require_own_data) | 3h |

## UI/UX Notes

N/A — pure backend dependency injection.

## Technical Notes

- **Stack:** FastAPI `Depends()`, python-jose JWT decode
- **Key considerations:** `require_authenticated_user()` extracts JWT from `request.cookies["access_token"]`; raises `HTTP_401` if missing or expired; `require_admin()` delegates to `require_authenticated_user()` then checks `role == "admin"`; `require_own_data()` accepts `target_user_id` and checks it matches `TokenPayload.sub`

## Dependencies

- STORY-004 (auth service with `decode_access_token()` must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
