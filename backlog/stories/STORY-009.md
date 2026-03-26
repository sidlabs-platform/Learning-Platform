# Story: Enrollment Management

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-009            |
| **Epic**     | EPIC-004             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** to enroll one or more Learners in a course and have Learners be able to self-enroll in published courses,
**so that** Learners can access course content and their progress can be tracked from the moment they start.

## Acceptance Criteria

1. **Given** an Admin session,
   **When** `POST /api/v1/enrollments` is called with a valid `userId` and `courseId`,
   **Then** an `Enrollment` record is created with `status=not_started` and returned with `201 Created`.

2. **Given** a duplicate enrollment (same `userId` + `courseId`),
   **When** `POST /api/v1/enrollments` is called again,
   **Then** the response is `409 Conflict`.

3. **Given** a Learner session,
   **When** `POST /api/v1/enrollments` is called with their own `userId` and a published `courseId`,
   **Then** an `Enrollment` is created successfully.

4. **Given** a Learner trying to self-enroll in an unpublished course,
   **When** `POST /api/v1/enrollments` is called,
   **Then** the response is `404 Not Found`.

5. **Given** an authenticated Learner,
   **When** `GET /api/v1/enrollments?userId={own_id}` is called,
   **Then** only that Learner's enrollments are returned.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                       |
|---------------|---------------------------------------------------------|
| BRD-FR-014    | COMP-004 Progress Tracking — admin enrollment           |
| BRD-FR-015    | COMP-004 Progress Tracking — self-enrollment            |
| BRD-FR-016    | COMP-004 Progress Tracking — enrollment status states   |
| BRD-FR-004    | COMP-001 Auth Service — own data isolation              |

## Tasks Breakdown

| Task ID  | Description                                              | Estimate |
|----------|----------------------------------------------------------|----------|
| TASK-021 | Implement progress tracking Pydantic models              | 2h       |
| TASK-022 | Implement enrollment service (create, get, list)         | 4h       |
| TASK-026 | Implement progress tracking router (enrollment endpoints)| 2h       |

## UI/UX Notes

N/A — API only. Admin enrollment management UI is in STORY-022.

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy 2.x async, Pydantic v2
- **Key considerations:** `UNIQUE(user_id, course_id)` constraint in DB; `DuplicateEnrollmentError` → 409; for self-enrollment, verify course `status=published` before creating; `require_own_data()` applied on learner enrollment list

## Dependencies

- STORY-002 (ORM models — enrollments table)
- STORY-005 (RBAC dependencies)
- STORY-006 (Course data must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
