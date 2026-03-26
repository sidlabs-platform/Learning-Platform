# Story: Authentication Pages (Login)

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-020            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 3 points             |
| **Priority** | P0                   |

## User Story

**As a** user (Learner or Admin),
**I want** a clean login page where I can enter my email and password,
**so that** I can authenticate and be redirected to my role-appropriate dashboard.

## Acceptance Criteria

1. **Given** `GET /login` is requested,
   **When** the page loads,
   **Then** a form with `email` and `password` fields and a "Sign In" button is displayed.

2. **Given** valid credentials are submitted,
   **When** the form is submitted via `POST /api/v1/auth/login`,
   **Then** the JWT cookie is set and the user is redirected to `/dashboard`.

3. **Given** invalid credentials are submitted,
   **When** the API returns `401`,
   **Then** an error message is displayed on the login page without a page reload.

4. **Given** an already-authenticated user,
   **When** `GET /login` is requested,
   **Then** they are redirected to `/dashboard`.

## BRD & Design References

| BRD ID        | HLD/LLD Component                         |
|---------------|-------------------------------------------|
| BRD-FR-001    | COMP-001 Auth Service — sign-in           |
| BRD-NFR-009   | COMP-007 Frontend — responsive layout     |

## Tasks Breakdown

| Task ID  | Description                                              | Estimate |
|----------|----------------------------------------------------------|----------|
| TASK-041 | Create login.html template and auth page styling         | 3h       |

## UI/UX Notes

- Centered card layout with platform logo above the form
- Show/hide password toggle
- Inline error message in red below the submit button on 401
- "Forgot password?" link shown but leads to a "Contact your administrator" message (no reset flow in MVP)

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch API
- **Key considerations:** Form submits via `fetch()` to `/api/v1/auth/login` (not native form POST) to handle JSON response and show inline errors; on success, `window.location.href = "/dashboard"`

## Dependencies

- STORY-019 (base template must exist)
- STORY-004 (auth login endpoint must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
