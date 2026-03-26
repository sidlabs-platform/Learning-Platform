# Story: CSV Export of Learner Progress Data

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-018            |
| **Epic**     | EPIC-006             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3 points             |
| **Priority** | P1                   |

## User Story

**As an** Admin,
**I want** to export learner progress data as a CSV file with optional filters,
**so that** I can share training completion reports with stakeholders or import the data into other tools.

## Acceptance Criteria

1. **Given** an Admin session,
   **When** `GET /api/v1/reports/export?format=csv` is called,
   **Then** a `200 OK` response is returned with `Content-Type: text/csv` and a downloadable file containing all learner progress rows.

2. **Given** an optional `?courseId=X` filter,
   **When** the export endpoint is called,
   **Then** only rows for course X are included.

3. **Given** the CSV response,
   **When** it is parsed,
   **Then** it contains the headers: `userId`, `userName`, `courseId`, `courseTitle`, `enrollmentStatus`, `completionPercentage`, `lastActivity`.

4. **Given** no enrollments exist,
   **When** the export is requested,
   **Then** a valid CSV with headers only (no data rows) is returned — not an error.

5. **Given** a Learner session,
   **When** `GET /api/v1/reports/export` is called,
   **Then** `403 Forbidden` is returned.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                    |
|---------------|------------------------------------------------------|
| BRD-FR-028    | COMP-005 Reporting — CSV export                      |
| BRD-NFR-001   | COMP-005 Reporting — < 2s response time              |

## Tasks Breakdown

| Task ID  | Description                                                   | Estimate |
|----------|---------------------------------------------------------------|----------|
| TASK-037 | Implement generate_csv_export() in reporting service          | (included in TASK-037) |
| TASK-038 | Implement CSV export route handler (StreamingResponse)        | (included in TASK-038) |

## UI/UX Notes

The "Export CSV" button on the admin reporting dashboard is in STORY-029 (EPIC-007).

## Technical Notes

- **Stack:** FastAPI `StreamingResponse`, Python `csv.writer`, generator pattern
- **Key considerations:** Use `StreamingResponse` with an async generator to avoid buffering entire dataset in memory; `Content-Disposition: attachment; filename="progress_export.csv"` header; use Python's `csv.writer` not string concatenation

## Dependencies

- STORY-017 (reporting service must be partially implemented)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
