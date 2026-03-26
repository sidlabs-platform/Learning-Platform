# Story: Course CRUD and Catalog API

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-006            |
| **Epic**     | EPIC-003             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 8 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** to create, read, update, and delete courses via the API,
**so that** I can build and manage the course catalog that Learners will browse and enroll in.

## Acceptance Criteria

1. **Given** an Admin session,
   **When** `POST /api/v1/courses` is called with all required fields,
   **Then** a course is created with `status=draft` and returned with `201 Created`.

2. **Given** a missing required field (e.g., no `title`),
   **When** `POST /api/v1/courses` is called,
   **Then** the response is `422 Unprocessable Entity` with field-level error details.

3. **Given** a Learner session,
   **When** `GET /api/v1/courses` is called,
   **Then** only `published` courses are returned.

4. **Given** query parameters `?difficulty=beginner&tag=git`,
   **When** `GET /api/v1/courses` is called,
   **Then** only courses matching both filters are returned.

5. **Given** an Admin session,
   **When** `GET /api/v1/courses` is called (without `status` restriction),
   **Then** both draft and published courses are returned.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                    |
|---------------|------------------------------------------------------|
| BRD-FR-005    | COMP-002 Course Management — catalog endpoint        |
| BRD-FR-006    | COMP-002 Course Management — catalog filtering       |
| BRD-FR-009    | COMP-002 Course Management — course hierarchy        |
| BRD-FR-010    | COMP-002 Course Management — course entity fields    |
| BRD-NFR-001   | COMP-002 Course Management — < 2s response time      |

## Tasks Breakdown

| Task ID  | Description                                                         | Estimate |
|----------|---------------------------------------------------------------------|----------|
| TASK-013 | Implement course management Pydantic models                         | 3h       |
| TASK-014 | Implement Markdown sanitiser (bleach wrapper)                       | 2h       |
| TASK-015 | Implement course management service (course CRUD + catalog)         | 5h       |
| TASK-018 | Implement course management router (course endpoints)               | 3h       |

## UI/UX Notes

Frontend catalog page is covered in STORY-015 (EPIC-007). This story is API-only.

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy 2.x async, Pydantic v2, bleach
- **Key considerations:** `get_course_catalog()` filters by `status=published` for Learner; `difficulty` and `tag` are optional query params; course `learning_objectives` and `tags` stored as JSON via `JSONList` TypeDecorator

## Dependencies

- STORY-002 (ORM models)
- STORY-005 (RBAC dependencies)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
