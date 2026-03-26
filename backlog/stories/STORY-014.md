# Story: AI Course Generation Request and Background Task

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-014            |
| **Epic**     | EPIC-005             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 8 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** to submit a course generation request and immediately receive a request ID, then poll for completion,
**so that** I can trigger AI-assisted draft creation without waiting for the full generation cycle in the browser.

## Acceptance Criteria

1. **Given** an Admin session,
   **When** `POST /api/v1/ai/generate-course` is called with all required fields,
   **Then** `202 Accepted` is returned within 500 ms with a `generationRequestId`.

2. **Given** a generation request is submitted,
   **When** the background task completes successfully,
   **Then** `GET /api/v1/ai/requests/{id}` returns `status=completed` with a `courseId` pointing to the new draft course.

3. **Given** a generation request,
   **When** the background task calls the GitHub Models API and receives a valid JSON response,
   **Then** all generated content (Course, Modules, Lessons, QuizQuestions) is persisted with `status=draft` and `isAiGenerated=true`.

4. **Given** a generation request,
   **When** a `ContentGenerationRequest` record is created,
   **Then** it includes `promptText`, `modelUsed`, `requesterId`, `status=pending`, and `createdAt`.

5. **Given** a missing required field in the generation request body,
   **When** `POST /api/v1/ai/generate-course` is called,
   **Then** `422 Unprocessable Entity` is returned.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                              |
|---------------|----------------------------------------------------------------|
| BRD-FR-029    | COMP-003 AI Generation — generation request schema             |
| BRD-FR-030    | COMP-003 AI Generation — GPT-4o generates all content types    |
| BRD-FR-031    | COMP-003 AI Generation — all AI content saved as draft         |
| BRD-FR-032    | COMP-003 AI Generation — generation metadata storage           |
| BRD-INT-010   | COMP-003 AI Generation — audit metadata for every call         |
| BRD-NFR-002   | COMP-003 AI Generation — 202 within 500ms; full gen < 60s     |

## Tasks Breakdown

| Task ID  | Description                                                         | Estimate |
|----------|---------------------------------------------------------------------|----------|
| TASK-032 | Implement content persistence layer (validate JSON, sanitise, insert draft) | 5h |
| TASK-033 | Implement AI generation router (trigger + status poll endpoints)    | 4h       |

## UI/UX Notes

AI generation form UI is covered in STORY-026 (EPIC-007). The admin polls `GET /api/v1/ai/requests/{id}` via Vanilla JS.

## Technical Notes

- **Stack:** FastAPI BackgroundTasks, httpx, SQLAlchemy async, Pydantic v2
- **Key considerations:** `_run_generation_task()` orchestrates prompt → model call → persist → status update inside BackgroundTask; `ContentGenerationArtifact` inserted after successful persist; always update `ContentGenerationRequest.status` to `completed` or `failed` — never leave in `in_progress` on error

## Dependencies

- STORY-012 (prompt templates and orchestration layer)
- STORY-013 (GitHub Models client)
- STORY-007 (course management service functions to persist draft content)
- STORY-005 (RBAC — require_admin)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
