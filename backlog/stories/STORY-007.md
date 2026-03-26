# Story: Module, Lesson, and Quiz Question CRUD

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-007            |
| **Epic**     | EPIC-003             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 8 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** to create, read, update, and delete modules, lessons, and quiz questions within a course,
**so that** I can build the full Course → Module → Lesson → QuizQuestion content hierarchy.

## Acceptance Criteria

1. **Given** an Admin and an existing course,
   **When** `POST /api/v1/courses/{id}/modules` is called with valid data,
   **Then** a module is created with the correct `courseId` and `sortOrder`.

2. **Given** a module,
   **When** `POST /api/v1/courses/{id}/modules/{mid}/lessons` is called with `markdownContent` containing a `<script>` tag,
   **Then** the script tag is stripped from `markdownContent` before storage.

3. **Given** a QuizQuestion creation request with fewer than 2 options,
   **When** `POST /api/v1/courses/{id}/modules/{mid}/quiz-questions` is called,
   **Then** the response is `422 Unprocessable Entity`.

4. **Given** a course with multiple modules,
   **When** `GET /api/v1/courses/{id}` is called,
   **Then** modules are returned ordered by `sortOrder` ascending, and each module contains its `lessons` and `quizQuestions` arrays.

5. **Given** a lesson with `isAiGenerated=true` is manually edited,
   **When** the lesson is updated via `PATCH /api/v1/lessons/{id}`,
   **Then** `isAiGenerated` is set to `false`.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                       |
|---------------|---------------------------------------------------------|
| BRD-FR-009    | COMP-002 Course Management — four-level hierarchy       |
| BRD-FR-011    | COMP-002 Course Management — Markdown lesson content    |
| BRD-FR-012    | COMP-002 Course Management — quiz question schema       |
| BRD-FR-013    | COMP-002 Course Management — sortOrder for modules/lessons |
| BRD-FR-037    | COMP-002 Course Management — XSS sanitisation          |
| BRD-FR-039    | COMP-002 Course Management — isAiGenerated flag        |

## Tasks Breakdown

| Task ID  | Description                                             | Estimate |
|----------|---------------------------------------------------------|----------|
| TASK-016 | Implement module and lesson service functions           | 4h       |
| TASK-017 | Implement quiz question service functions               | 3h       |
| TASK-018 | Implement course management router (module/lesson/quiz endpoints) | 3h |

## UI/UX Notes

Admin course editor UI is covered in STORY-022 (EPIC-007). This story is API-only.

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy 2.x async, Pydantic v2, bleach
- **Key considerations:** `sanitise_markdown()` must be called on every lesson create/update; `options` field on QuizQuestion validated `min_items=2, max_items=5`; `correctAnswer` must be one of the `options` values; `isAiGenerated` set to `false` on any manual admin edit

## Dependencies

- STORY-006 (course service and models must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
