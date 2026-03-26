# Story: AI Generation Audit Log

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-016            |
| **Epic**     | EPIC-005             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3 points             |
| **Priority** | P1                   |

## User Story

**As an** Admin,
**I want** to view a list of past AI generation requests with their status, prompt, model, timestamp, and requester,
**so that** I have a complete audit trail of AI-assisted content creation for governance and troubleshooting.

## Acceptance Criteria

1. **Given** an Admin session,
   **When** `GET /api/v1/ai/requests` is called,
   **Then** a paginated list of `ContentGenerationRequest` records is returned with all audit fields.

2. **Given** a completed generation request,
   **When** its record is inspected,
   **Then** it contains: `promptText`, `modelUsed`, `requesterId`, `status`, `createdAt`, `completedAt`, `latencyMs`.

3. **Given** a Learner session,
   **When** `GET /api/v1/ai/requests` is called,
   **Then** `403 Forbidden` is returned.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                          |
|---------------|------------------------------------------------------------|
| BRD-FR-032    | COMP-003 AI Generation — generation metadata storage       |
| BRD-INT-010   | COMP-003 AI Generation — audit metadata for every call     |
| BRD-NFR-013   | COMP-003 AI Generation — AI generation calls logged        |
| BRD-NFR-014   | COMP-003 AI Generation — latency captured in structured logs |

## Tasks Breakdown

| Task ID  | Description                                                   | Estimate |
|----------|---------------------------------------------------------------|----------|
| TASK-033 | Add GET /api/v1/ai/requests list endpoint (in router.py)      | (included in TASK-033) |

## UI/UX Notes

The generation log page UI is in STORY-027 (EPIC-007).

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy, Pydantic v2
- **Key considerations:** List endpoint supports optional `status` filter and pagination (`skip`/`limit`); `promptText` should be truncated in list view for readability; `latencyMs` computed as `(completedAt - createdAt).total_seconds() * 1000`

## Dependencies

- STORY-014 (AI generation request records must be created)
- STORY-005 (RBAC — require_admin)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
