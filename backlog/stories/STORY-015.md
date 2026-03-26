# Story: AI Generation Failure Handling and Section Regeneration

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-015            |
| **Epic**     | EPIC-005             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P1                   |

## User Story

**As an** Admin,
**I want** to see a clear error message with a retry option when AI generation fails, and to be able to regenerate a single module or lesson without regenerating the whole course,
**so that** I can efficiently fix incomplete or poor-quality generated sections.

## Acceptance Criteria

1. **Given** the GitHub Models API returns a 5xx error or times out,
   **When** all retries are exhausted,
   **Then** `ContentGenerationRequest.status=failed` with a descriptive `errorMessage`, and published courses remain accessible.

2. **Given** a failed generation request,
   **When** `GET /api/v1/ai/requests/{id}` is polled,
   **Then** the response includes `status=failed` and an `errorMessage`.

3. **Given** an Admin targeting a specific lesson,
   **When** `POST /api/v1/ai/regenerate-section` is called with `{ sectionType: "lesson", sectionId: "..." }`,
   **Then** only the targeted lesson is updated; all other lessons and modules are unchanged.

4. **Given** a section regeneration request,
   **When** it completes,
   **Then** a new `ContentGenerationRequest` record is created scoped to that section.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                             |
|---------------|---------------------------------------------------------------|
| BRD-FR-034    | COMP-003 AI Generation — section-level regeneration           |
| BRD-FR-035    | COMP-003 AI Generation — clear retryable error for admin      |
| BRD-INT-003   | COMP-003 AI Generation — exponential backoff                  |
| BRD-NFR-011   | COMP-003 AI Generation — AI failures don't affect courses     |
| BRD-NFR-012   | COMP-003 AI Generation — clear error + retry option           |

## Tasks Breakdown

| Task ID  | Description                                                          | Estimate |
|----------|----------------------------------------------------------------------|----------|
| TASK-034 | Implement section regeneration router (review_router.py)             | 4h       |

## UI/UX Notes

The admin UI showing error + retry button is in STORY-026 (EPIC-007).

## Technical Notes

- **Stack:** FastAPI BackgroundTasks, httpx, SQLAlchemy
- **Key considerations:** `trigger_section_regeneration()` creates a new `ContentGenerationRequest` with `section_type` and `section_id`; uses appropriate prompt template (PT-002 for lesson, PT-003 for quiz); on success, only the targeted section record is updated

## Dependencies

- STORY-014 (generation router and content persistence layer must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
