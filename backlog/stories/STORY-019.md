# Story: Base Templates, CSS Design System, and Frontend Router

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-019            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** user (Learner or Admin),
**I want** a consistent, responsive visual layout across all pages,
**so that** the platform feels cohesive and I can navigate comfortably on desktop and tablet devices.

## Acceptance Criteria

1. **Given** any page of the platform,
   **When** the page is rendered,
   **Then** it extends `base.html` and displays a consistent navigation bar with the user's name and a logout button.

2. **Given** a viewport width of 768 px (tablet),
   **When** any page is loaded,
   **Then** the layout adapts correctly with no horizontal scrollbar or broken grid.

3. **Given** a user with no active session,
   **When** `GET /` is requested,
   **Then** they are redirected to `/login`.

4. **Given** an authenticated Learner,
   **When** `GET /` is requested,
   **Then** they are redirected to `/dashboard`.

5. **Given** an authenticated Admin,
   **When** `GET /dashboard` is requested,
   **Then** the admin dashboard template is rendered (not the learner dashboard).

## BRD & Design References

| BRD ID        | HLD/LLD Component                                       |
|---------------|---------------------------------------------------------|
| BRD-NFR-008   | COMP-007 Frontend — ≤ 2 clicks to lesson from dashboard |
| BRD-NFR-009   | COMP-007 Frontend — responsive desktop + tablet         |

## Tasks Breakdown

| Task ID  | Description                                                    | Estimate |
|----------|----------------------------------------------------------------|----------|
| TASK-040 | Create base HTML template and CSS files (base.css, layout.css, components.css) | 4h |
| TASK-052 | Implement frontend page router (frontend/router.py)            | 3h       |

## UI/UX Notes

- Navigation bar: logo/brand, nav links (Dashboard, Catalog for Learners; Courses, AI Generate, Reports for Admins), user name + logout
- Color palette: professional blues and grays; accent color for CTAs
- CSS custom properties for theming; mobile-first responsive breakpoints at 768px and 1280px
- Progress bars use `<progress>` element or custom CSS bar component

## Technical Notes

- **Stack:** Jinja2, Vanilla HTML/CSS, FastAPI `Jinja2Templates`
- **Key considerations:** `base.html` checks cookie presence for auth state; role-based nav links rendered via Jinja2 conditionals; `utils.js` shared fetch wrapper must be loaded on all pages

## Dependencies

- STORY-001 (FastAPI app must be running to serve templates)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
