# Story: Admin Reporting Dashboard API

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-017            |
| **Epic**     | EPIC-006             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** a single dashboard API endpoint that returns all key training metrics — total learners, enrollments per course, completion rates, in-progress counts, and quiz score summaries — with optional course and learner filters,
**so that** I can monitor training effectiveness and identify learners who need follow-up.

## Acceptance Criteria

1. **Given** an Admin session,
   **When** `GET /api/v1/reports/dashboard` is called,
   **Then** a `200 OK` response is returned within 2 seconds with all five metric categories.

2. **Given** a Learner session,
   **When** `GET /api/v1/reports/dashboard` is called,
   **Then** `403 Forbidden` is returned.

3. **Given** `?courseId=X` query parameter,
   **When** `GET /api/v1/reports/dashboard` is called,
   **Then** all metrics are scoped to course X only.

4. **Given** `?userId=Y` query parameter,
   **When** `GET /api/v1/reports/dashboard` is called,
   **Then** all metrics are scoped to learner Y only.

5. **Given** any reporting request,
   **When** logs are inspected,
   **Then** a structured log entry records the admin's `userId`, the endpoint called, and the filter parameters.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                        |
|---------------|----------------------------------------------------------|
| BRD-FR-026    | COMP-005 Reporting — dashboard metrics                   |
| BRD-FR-027    | COMP-005 Reporting — filter by courseId/userId           |
| BRD-NFR-001   | COMP-005 Reporting — < 2s response time                  |
| BRD-NFR-013   | COMP-005 Reporting — reporting action logging            |
| BRD-NFR-015   | COMP-005 Reporting — traceable to requesting admin       |

## Tasks Breakdown

| Task ID  | Description                                               | Estimate |
|----------|-----------------------------------------------------------|----------|
| TASK-036 | Implement reporting Pydantic models                       | 2h       |
| TASK-037 | Implement reporting service (dashboard metrics, per-course, quiz summary) | 5h |
| TASK-038 | Implement reporting router (dashboard endpoint)           | 2h       |

## UI/UX Notes

Admin reporting dashboard UI is in STORY-029 (EPIC-007).

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy 2.x async aggregate queries, Pydantic v2
- **Key considerations:** Use SQLAlchemy `func.count()`, `func.avg()` for aggregations; apply optional `course_id` / `user_id` WHERE filters; reporting service is read-only (no writes); log reporting actions with `logger.info()` including admin userId

## Dependencies

- STORY-002 (ORM models)
- STORY-005 (RBAC — require_admin)
- STORY-009 (enrollment data)
- STORY-010 (progress data)
- STORY-011 (quiz attempt data)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
