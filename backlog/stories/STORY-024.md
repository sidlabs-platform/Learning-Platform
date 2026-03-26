# Story: Admin Course Management UI

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-024            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 8 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** a course management UI where I can view all courses, create new ones, edit existing content, manage modules and lessons, and publish or unpublish courses,
**so that** I can maintain the course catalog without using raw API calls.

## Acceptance Criteria

1. **Given** `/admin/courses` is loaded,
   **When** the page renders,
   **Then** all courses (draft and published) are listed with status badges and action buttons (Edit, Publish/Unpublish).

2. **Given** the "Publish" button is clicked for a draft course,
   **When** the action completes,
   **Then** the status badge updates to "Published" without a full page reload.

3. **Given** `/admin/courses/new` is loaded,
   **When** the form is submitted with all required fields,
   **Then** a new draft course is created and the admin is redirected to the course editor.

4. **Given** `/admin/courses/{id}/edit` is loaded,
   **When** a module or lesson is edited and saved,
   **Then** the changes are persisted via the API and confirmed in the UI.

5. **Given** a lesson that is `isAiGenerated=true`,
   **When** displayed in the lesson editor,
   **Then** an "AI-generated draft" badge is shown next to the lesson title.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                        |
|---------------|----------------------------------------------------------|
| BRD-FR-007    | COMP-002 Course Management — publish endpoint            |
| BRD-FR-008    | COMP-002 Course Management — unpublish endpoint          |
| BRD-FR-033    | COMP-007 Frontend — AI-generated draft label             |
| BRD-FR-039    | COMP-002 Course Management — isAiGenerated flag          |

## Tasks Breakdown

| Task ID  | Description                                                            | Estimate |
|----------|------------------------------------------------------------------------|----------|
| TASK-045 | Create admin course management templates (course-list.html, course-editor.html, lesson-editor.html) | 6h |
| TASK-051 | Implement course-editor.js and utils.js                                | 4h       |

## UI/UX Notes

- Course list: table with columns for title, status badge (green=published, gray=draft), difficulty, created date, and action buttons
- Course editor: form fields for course metadata + accordion for modules/lessons; inline add/edit/delete for modules and lessons
- Lesson editor: full-width textarea for Markdown with live preview pane (rendered via server or simple JS)
- AI-generated badge: yellow pill label "AI Draft" shown next to AI-generated sections

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch, CSS
- **Key considerations:** `course-editor.js` handles inline add/edit of modules and lessons via fetch calls; `utils.js` provides shared `apiFetch(url, options)` wrapper with auth cookie and error handling

## Dependencies

- STORY-019 (base template)
- STORY-006 (course CRUD API)
- STORY-007 (module/lesson/quiz API)
- STORY-008 (publish/unpublish API)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
