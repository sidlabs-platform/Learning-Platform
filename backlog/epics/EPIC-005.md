# Epic: AI-Assisted Course Generation

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-005             |
| **Status**  | Ready                |
| **Owner**   | 4-develop-agent      |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 3             |

## Goal / Objective

Implement the four-layer AI generation service (Prompt Orchestration → Model Invocation → Content Persistence → Review Workflow) that integrates with the GitHub Models API (GPT-4o) to generate structured course drafts, supporting async dispatch, exponential backoff retry, full audit logging, and section-level regeneration — all with a mandatory admin review gate before any content reaches learners.

## Business Value

AI-assisted generation is the core innovation that reduces content authoring effort (BO-3) and validates the platform's premise (BO-4). By generating draft course outlines, lesson content, quiz questions, and key takeaways from a simple prompt, it eliminates hours of manual authoring. The mandatory draft-review-publish workflow protects content quality.

## BRD Requirements Mapped

| BRD ID        | Description                                                                              |
|---------------|------------------------------------------------------------------------------------------|
| BRD-FR-029    | Generation request with: topic, audience, objectives, difficulty, moduleCount, tone      |
| BRD-FR-030    | GPT-4o generates: title, description, module outline, lesson drafts, quiz, key takeaways |
| BRD-FR-031    | AI content saved as `draft`; never auto-published                                        |
| BRD-FR-032    | Generation metadata stored: promptText, modelUsed, requesterId, status, timestamps      |
| BRD-FR-033    | Admin UI labels AI-generated content as "AI-generated draft"                            |
| BRD-FR-034    | Section-level regeneration without regenerating whole course                             |
| BRD-FR-035    | AI failures return clear retryable error; published courses unaffected                   |
| BRD-FR-036    | Five reusable prompt templates (PT-001 through PT-005)                                  |
| BRD-INT-001   | GitHub Models API auth via `GITHUB_MODELS_API_KEY` environment variable                 |
| BRD-INT-002   | GitHub Models endpoint via `GITHUB_MODELS_ENDPOINT`; GPT-4o model                      |
| BRD-INT-003   | HTTP 429 handled with exponential backoff (max 3 retries)                               |
| BRD-INT-004   | All GitHub Models errors wrapped; raw details not exposed to non-admins                 |
| BRD-INT-005   | 60-second timeout on all GitHub Models calls                                             |
| BRD-INT-006   | Generated JSON validated against defined content schema                                  |
| BRD-INT-007   | Five prompt templates stored as application-level configuration                          |
| BRD-INT-008   | Four-layer modular design for MCP readiness                                              |
| BRD-INT-010   | Audit metadata for every API call: prompt, model, requester, status, latency, errors    |
| BRD-NFR-002   | Generation status endpoint responds < 500 ms; full generation < 60 s                    |
| BRD-NFR-005   | API key never logged or returned                                                          |
| BRD-NFR-011   | AI failures do not affect published course access                                        |
| BRD-NFR-012   | Failed generation shows clear error and retry option                                     |
| BRD-NFR-013   | AI generation calls logged                                                                |
| BRD-NFR-014   | AI generation latency captured in structured log entries                                 |

## Features

| Feature ID | Name                                      | Priority (P0/P1/P2) | Status  |
|------------|-------------------------------------------|----------------------|---------|
| FEAT-025   | Five prompt templates (PT-001 to PT-005)  | P0                   | Planned |
| FEAT-026   | Prompt orchestration service              | P0                   | Planned |
| FEAT-027   | GitHub Models API client with retry/backoff | P0                 | Planned |
| FEAT-028   | Async generation dispatch (BackgroundTasks) | P0                 | Planned |
| FEAT-029   | Content persistence layer (validate + sanitise + insert draft) | P0 | Planned |
| FEAT-030   | Generation status polling endpoint        | P0                   | Planned |
| FEAT-031   | Section regeneration endpoint             | P1                   | Planned |
| FEAT-032   | Generation audit log endpoint             | P1                   | Planned |

## Acceptance Criteria

1. `POST /api/v1/ai/generate-course` returns `202 Accepted` with a `generationRequestId` immediately.
2. Background task calls GitHub Models API, validates JSON response, sanitises Markdown, and inserts draft Course/Modules/Lessons/QuizQuestions.
3. `GET /api/v1/ai/requests/{id}` returns the current generation status within 500 ms.
4. On HTTP 429, the client retries up to 3 times with exponential backoff before setting status to `failed`.
5. On timeout (> 60 s) or 5xx, status is set to `failed` with a descriptive error message; admin UI shows retry button.
6. `GITHUB_MODELS_API_KEY` never appears in logs or API responses.
7. All generated course records have `status=draft` and `isAiGenerated=true`.
8. Section regeneration (`POST /api/v1/ai/regenerate-section`) updates only the targeted section.

## Dependencies & Risks

**Dependencies:**
- EPIC-001 (ORM models, `content_generation_requests`, `content_generation_artifacts` tables)
- EPIC-002 (RBAC — require_admin dependency)
- EPIC-003 (Course Management service functions to persist draft content)
- GitHub Models API access (`GITHUB_MODELS_API_KEY`, `GITHUB_MODELS_ENDPOINT`)

**Risks:**
- GitHub Models API unavailability during development — mitigate with `respx` mock in tests
- GPT-4o JSON output not conforming to schema — mitigate with strict Pydantic validation + error handling
- Long generation times exceeding test patience — mitigate with mocked model client in integration tests

## Out of Scope

- Full MCP server implementation (architecture must be MCP-ready; MCP server is a future release)
- Non-GPT-4o model providers
- Auto-publishing of AI-generated content (always manual)

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
