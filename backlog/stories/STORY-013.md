# Story: GitHub Models API Client with Retry and Backoff

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-013            |
| **Epic**     | EPIC-005             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** backend developer,
**I want** a robust async HTTP client wrapper for the GitHub Models API that handles retries, timeouts, and error mapping without leaking credentials or raw error details,
**so that** the AI generation service can call GPT-4o reliably and surface clean error states to admins.

## Acceptance Criteria

1. **Given** a successful GitHub Models API call,
   **When** `GitHubModelsClient.generate(prompt)` is called,
   **Then** the raw JSON string from the model's response content is returned.

2. **Given** the API returns HTTP 429,
   **When** the client retries with exponential backoff (1s, 2s, 4s),
   **Then** after 3 failed retries, `GenerationFailedError` is raised with a clear message.

3. **Given** the request exceeds 60 seconds,
   **When** `httpx.TimeoutException` is raised,
   **Then** `GenerationFailedError` is raised (no retry on pure timeout).

4. **Given** a 5xx error from the API,
   **When** retries are exhausted,
   **Then** `GenerationFailedError` is raised; the raw error body is logged internally but NOT returned to callers.

5. **Given** `GITHUB_MODELS_API_KEY` is missing from environment,
   **When** the application starts,
   **Then** `pydantic-settings` raises `ValidationError` at startup — before any request is served.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                            |
|---------------|--------------------------------------------------------------|
| BRD-INT-001   | COMP-003 AI Generation — API key via env var                 |
| BRD-INT-002   | COMP-003 AI Generation — GPT-4o endpoint configuration       |
| BRD-INT-003   | COMP-003 AI Generation — exponential backoff on 429          |
| BRD-INT-004   | COMP-003 AI Generation — error wrapping, no raw leak         |
| BRD-INT-005   | COMP-003 AI Generation — 60-second timeout                   |
| BRD-NFR-005   | COMP-001 Auth Service — API key never in logs                |
| BRD-NFR-011   | COMP-003 AI Generation — AI failure does not affect courses  |

## Tasks Breakdown

| Task ID  | Description                                                          | Estimate |
|----------|----------------------------------------------------------------------|----------|
| TASK-031 | Implement AI generation Pydantic models                              | 2h       |
| TASK-030 | Implement GitHubModelsClient (httpx, retry, timeout, error mapping)  | 5h       |

## UI/UX Notes

N/A — backend model invocation layer only.

## Technical Notes

- **Stack:** httpx AsyncClient, asyncio.sleep(), pydantic-settings
- **Key considerations:** `Authorization: Bearer {GITHUB_MODELS_API_KEY}` header; `timeout=httpx.Timeout(60.0)`; exponential backoff: `asyncio.sleep(2**attempt)` for attempts 0–2; `AI_MAX_RETRIES` and `AI_REQUEST_TIMEOUT_SECONDS` from settings; never log the API key value

## Dependencies

- STORY-001 (settings module with API key configuration)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
