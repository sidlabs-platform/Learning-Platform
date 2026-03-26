# Task: Write AI Generation Tests with Mocks

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-034             |
| **Story**    | STORY-014            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5h                   |

## Description

Write comprehensive pytest tests for the AI generation service using `respx` to mock the GitHub Models API. Tests must cover the full happy path, error scenarios (429, 5xx, timeout), schema validation failures, and key security requirements (API key not in logs).

## Implementation Details

**Files to create/modify:**
- `tests/test_ai_generation.py` — AI generation integration tests with mocked GitHub Models API

**Approach:**
```python
import respx
import httpx

MOCK_GPT_RESPONSE = {
    "choices": [{"message": {"content": json.dumps({
        "title": "Test Course", "description": "Test desc",
        "target_audience": "developers", "learning_objectives": ["Learn testing"],
        "modules": [{
            "title": "Module 1", "summary": "Summary",
            "lessons": [{"title": "Lesson 1", "markdown_content": "# Content", "estimated_minutes": 10}],
            "quiz_questions": [{"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "Because A"}]
        }]
    })}}]
}

class TestGenerateCourse:
    @respx.mock
    async def test_generate_course_returns_202(admin_client): ...
    
    @respx.mock
    async def test_generation_completes_and_creates_draft_course(admin_client): ...
    
    @respx.mock  
    async def test_generation_with_429_retries_and_eventually_fails(admin_client): ...
    
    @respx.mock
    async def test_generation_timeout_marks_failed(admin_client): ...
    
    async def test_generation_by_learner_returns_403(learner_client): ...

class TestApiKeyNotLeaked:
    async def test_api_key_not_in_log_output(caplog, admin_client): ...
    async def test_api_key_not_in_error_response(admin_client): ...

class TestSectionRegeneration:
    @respx.mock
    async def test_regenerate_section_returns_202(admin_client): ...
    
    @respx.mock
    async def test_regenerate_only_updates_target_section(admin_client): ...

class TestAuditLog:
    async def test_generation_request_list_admin_only(admin_client, learner_client): ...
    async def test_completed_request_has_latency_ms(admin_client): ...
```

## API Changes

N/A — test file only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                        |
|-------------------|-----------------------------------------------|
| TASK-032          | AI generation router must be implemented      |
| TASK-033          | Section regeneration router must be implemented|

**Wave:** 8

## Acceptance Criteria

- [ ] All tests pass with `pytest -v`
- [ ] `respx` is used to mock all GitHub Models API calls (no real API calls in tests)
- [ ] Test coverage for AI generation module ≥ 80%
- [ ] API key non-leakage test verifies key does not appear in logs or response bodies
- [ ] 429 retry test confirms exactly 3 retry attempts before failure

## Test Requirements

- **Unit tests:** `GitHubModelsClient.generate()` with all error types; `persist_generated_course()` with valid/invalid JSON; prompt rendering
- **Integration tests:** Full 202 → background task → status poll cycle (mocked); failure cycle
- **Edge cases:** GPT-4o returns malformed JSON; GPT-4o returns valid JSON but wrong schema; generation request with missing optional fields

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-014        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-029–037, BRD-INT-001–010, BRD-NFR-005, BRD-NFR-011, BRD-NFR-012, BRD-NFR-014 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
