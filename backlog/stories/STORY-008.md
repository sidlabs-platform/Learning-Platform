# Story: Course Publish, Unpublish, and Governance Workflow

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-008            |
| **Epic**     | EPIC-003             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** to publish or unpublish a course to control its visibility in the learner catalog,
**so that** I can review content before releasing it and remove courses that are no longer appropriate.

## Acceptance Criteria

1. **Given** a course with `status=draft`,
   **When** `PATCH /api/v1/courses/{id}/publish` is called by an Admin,
   **Then** the course `status` becomes `published`, `publishedAt` is set, and the course appears in the learner catalog.

2. **Given** a course with `status=published`,
   **When** `PATCH /api/v1/courses/{id}/unpublish` is called by an Admin,
   **Then** the course `status` becomes `draft` and it no longer appears in the learner catalog; existing progress records are preserved.

3. **Given** a Learner session,
   **When** `PATCH /api/v1/courses/{id}/publish` is called,
   **Then** the response is `403 Forbidden`.

4. **Given** a publish or unpublish action,
   **When** application logs are inspected,
   **Then** a log entry records the event with `courseId` and `adminId`.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                     |
|---------------|-------------------------------------------------------|
| BRD-FR-007    | COMP-002 Course Management — publish endpoint         |
| BRD-FR-008    | COMP-002 Course Management — unpublish endpoint       |
| BRD-FR-038    | COMP-002 Course Management — draft/published governance |
| BRD-NFR-013   | COMP-002 Course Management — publish/unpublish logging |

## Tasks Breakdown

| Task ID  | Description                                                    | Estimate |
|----------|----------------------------------------------------------------|----------|
| TASK-015 | Implement publish_course() and unpublish_course() in service.py | (included in TASK-015) |
| TASK-018 | Implement publish/unpublish route handlers                     | (included in TASK-018) |

## UI/UX Notes

Admin course list with publish/unpublish buttons is in STORY-022. This story is API-only.

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy
- **Key considerations:** `InvalidStatusTransitionError` raised if attempting to publish an already-published course; `unpublish` preserves all related `ProgressRecord` and `Enrollment` rows — no cascade to these tables on status change

## Dependencies

- STORY-006 (course service and router must exist)
- STORY-005 (RBAC dependencies)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
