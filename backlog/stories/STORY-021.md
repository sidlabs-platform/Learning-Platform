# Story: Learner Dashboard and Course Catalog Pages

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-021            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** Learner,
**I want** a dashboard showing my enrolled courses with completion progress, and a catalog page where I can browse and filter published courses,
**so that** I can quickly see where I am in my learning journey and discover new courses to enroll in.

## Acceptance Criteria

1. **Given** an authenticated Learner,
   **When** `/dashboard` is loaded,
   **Then** all enrolled courses are shown as cards with title, completion percentage bar, and a "Continue" or "Start" button.

2. **Given** the "Continue" button on an in-progress course,
   **When** clicked,
   **Then** the Learner is taken directly to the last-accessed lesson (≤ 2 clicks from dashboard to lesson).

3. **Given** `/catalog` is loaded,
   **When** difficulty and tag filters are changed,
   **Then** the course list updates dynamically (or via form submit) to show only matching courses.

4. **Given** a published course in the catalog,
   **When** the "Enroll" button is clicked,
   **Then** a self-enrollment request is sent and the user is redirected to the course detail page.

5. **Given** a Learner who has no enrollments,
   **When** `/dashboard` is loaded,
   **Then** an empty state message with a "Browse Catalog" link is displayed.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                        |
|---------------|----------------------------------------------------------|
| BRD-FR-005    | COMP-002 Course Management — published catalog           |
| BRD-FR-006    | COMP-002 Course Management — filter by tag/difficulty    |
| BRD-FR-015    | COMP-004 Progress Tracking — self-enrollment             |
| BRD-NFR-008   | COMP-007 Frontend — ≤ 2 clicks to lesson                 |
| BRD-NFR-009   | COMP-007 Frontend — responsive layout                    |

## Tasks Breakdown

| Task ID  | Description                                                       | Estimate |
|----------|-------------------------------------------------------------------|----------|
| TASK-042 | Create learner dashboard (dashboard.html) and catalog (catalog.html) templates | 5h |

## UI/UX Notes

- Dashboard: Course cards in a responsive grid (2-col desktop, 1-col mobile); each card shows title, difficulty badge, completion % as progress bar, and CTA button
- Catalog: Filter sidebar/top-bar with difficulty dropdown and tag chips; course card grid; "Enroll" CTA
- Empty state: illustration + prompt to visit catalog

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch, CSS grid
- **Key considerations:** Dashboard data fetched from `GET /api/v1/enrollments?userId={self}` + `GET /api/v1/courses/{id}`; catalog data from `GET /api/v1/courses`; enrollment via `POST /api/v1/enrollments`

## Dependencies

- STORY-019 (base template)
- STORY-006 (course catalog API)
- STORY-009 (enrollment API)
- STORY-010 (progress data for completion %)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
