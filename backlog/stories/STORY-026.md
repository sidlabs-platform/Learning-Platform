# Story: Admin Reporting Dashboard UI

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-026            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** a reporting dashboard page showing enrollment metrics, completion rates, and quiz performance summaries with filter controls, plus a "Export CSV" button,
**so that** I can measure training effectiveness and share progress data with stakeholders.

## Acceptance Criteria

1. **Given** `/admin` is loaded by an Admin,
   **When** the page renders,
   **Then** summary cards are displayed: total learners, total enrollments, overall completion rate, and in-progress count.

2. **Given** the course filter dropdown is changed,
   **When** a course is selected,
   **Then** all metrics update to reflect data for that course only.

3. **Given** the quiz score summary section,
   **When** it renders,
   **Then** per-module pass rates and average scores are shown in a table.

4. **Given** the "Export CSV" button is clicked,
   **When** triggered,
   **Then** a CSV file download is initiated from `GET /api/v1/reports/export?format=csv`.

5. **Given** a Learner tries to access `/admin`,
   **When** the page router checks the role,
   **Then** they are redirected to `/dashboard`.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                       |
|---------------|---------------------------------------------------------|
| BRD-FR-026    | COMP-005 Reporting — admin dashboard metrics            |
| BRD-FR-027    | COMP-005 Reporting — filter by courseId/userId          |
| BRD-FR-028    | COMP-005 Reporting — CSV export                         |
| BRD-NFR-009   | COMP-007 Frontend — responsive layout                   |

## Tasks Breakdown

| Task ID  | Description                                                     | Estimate |
|----------|-----------------------------------------------------------------|----------|
| TASK-047 | Create admin reporting dashboard template (admin/dashboard.html) | 4h      |

## UI/UX Notes

- Summary KPI cards at top: large metric number + label (Total Learners, Enrollments, Completion Rate, In Progress)
- Per-course metrics: table with columns for course title, enrollments, completed, in-progress, completion %
- Quiz summary: collapsible section per course → per module
- Filter bar: Course dropdown + User search input + "Apply Filter" button
- "Export CSV" button: triggers file download; shows spinner while downloading

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch, CSS
- **Key considerations:** Dashboard data fetched from `GET /api/v1/reports/dashboard` on page load; filter changes trigger new fetch with query params; CSV export uses `window.location.href` assignment for file download

## Dependencies

- STORY-019 (base template)
- STORY-017 (reporting dashboard API)
- STORY-018 (CSV export API)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
