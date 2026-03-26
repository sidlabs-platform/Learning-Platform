# Story: Course Detail and Lesson Viewer Pages

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-022            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 8 points             |
| **Priority** | P0                   |

## User Story

**As a** Learner,
**I want** a course detail page showing the module and lesson structure, and a lesson viewer that displays Markdown content with a "Mark Complete" button that auto-saves my progress,
**so that** I can consume course content and track my completion without worrying about losing progress.

## Acceptance Criteria

1. **Given** a Learner visits `/courses/{id}`,
   **When** the page loads,
   **Then** the course title, description, module list, and lesson list are displayed with completion checkmarks for completed lessons.

2. **Given** a Learner opens `/courses/{id}/lessons/{lid}`,
   **When** the page loads,
   **Then** a `POST /api/v1/progress` call is automatically made with `completed=false` to record `lastViewedAt`.

3. **Given** a Learner clicks "Mark Complete",
   **When** the button is clicked,
   **Then** `POST /api/v1/progress` is called with `completed=true`, the button changes to a checkmark, and the module progress bar updates without a page reload.

4. **Given** Markdown content in a lesson,
   **When** rendered in the browser,
   **Then** `<script>` tags and `javascript:` URLs are absent from the rendered HTML (server-side sanitisation applied).

5. **Given** a Learner clicks "Next Lesson",
   **When** navigating,
   **Then** the next lesson in `sortOrder` within the same module is loaded.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                          |
|---------------|------------------------------------------------------------|
| BRD-FR-011    | COMP-002 Course Management — Markdown lesson content       |
| BRD-FR-017    | COMP-004 Progress Tracking — ProgressRecord on view        |
| BRD-FR-021    | COMP-004 Progress Tracking — progress survives page refresh|
| BRD-NFR-006   | COMP-007 Frontend — XSS-safe Markdown rendering            |
| BRD-NFR-008   | COMP-007 Frontend — ≤ 2 clicks to lesson                   |

## Tasks Breakdown

| Task ID  | Description                                                           | Estimate |
|----------|-----------------------------------------------------------------------|----------|
| TASK-043 | Create course-detail.html and lesson-viewer.html templates            | 5h       |
| TASK-048 | Implement progress.js (recordLessonView, markLessonComplete functions) | 3h      |

## UI/UX Notes

- Course detail: sidebar with module accordion showing lesson links; completed lessons show green checkmark
- Lesson viewer: readable content area with Markdown rendered to HTML; "Mark Complete" button top/bottom; prev/next lesson navigation
- Progress bar per module updates in real-time after Mark Complete

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch, CSS
- **Key considerations:** `recordLessonView()` called in `DOMContentLoaded` event; server renders pre-sanitised HTML (bleach applied at write time); `progress.js` handles button state changes and progress bar DOM updates

## Dependencies

- STORY-019 (base template)
- STORY-007 (module/lesson API)
- STORY-010 (progress recording API)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
