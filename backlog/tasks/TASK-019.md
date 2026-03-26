# Task: Write Course Management Tests

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-019             |
| **Story**    | STORY-006            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Write comprehensive pytest integration tests for the course management service and router, covering the full CRUD lifecycle, publish/unpublish workflow, catalog filtering, Markdown sanitisation, and seed data validation.

## Implementation Details

**Files to create/modify:**
- `tests/test_course_management.py` — course management integration tests
- `tests/test_sanitiser.py` — unit tests for `sanitise_markdown()`

**Approach:**
```python
# test_course_management.py
class TestCourseCatalog:
    async def test_catalog_returns_only_published(admin_client, learner_client): ...
    async def test_catalog_filter_by_difficulty(learner_client): ...
    async def test_catalog_filter_by_tag(learner_client): ...

class TestCourseCreate:
    async def test_create_course_as_admin(admin_client): ...
    async def test_create_course_as_learner_returns_403(learner_client): ...
    async def test_create_course_missing_title_returns_422(admin_client): ...

class TestPublishUnpublish:
    async def test_publish_course(admin_client): ...
    async def test_unpublish_course(admin_client): ...
    async def test_learner_cannot_publish(learner_client): ...
    async def test_publish_already_published_returns_409(admin_client): ...

class TestSeedData:
    async def test_three_starter_courses_exist(async_client): ...
    async def test_github_foundations_has_5_modules(async_client): ...
```

## API Changes

N/A — test file only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                      |
|-------------------|---------------------------------------------|
| TASK-018          | Course management router must be implemented|
| TASK-007          | Seed data must be available for seed tests  |

**Wave:** 7

## Acceptance Criteria

- [ ] All tests in `test_course_management.py` pass with `pytest -v`
- [ ] `test_sanitiser.py` covers `<script>`, `javascript:`, `onerror=`, and safe content
- [ ] Seed data validation tests confirm 3 courses with 5 modules each
- [ ] Test coverage for course management module ≥ 80%

## Test Requirements

- **Unit tests:** `sanitise_markdown()` with various XSS vectors
- **Integration tests:** Full CRUD + publish/unpublish cycle; catalog filtering
- **Edge cases:** Empty catalog; duplicate course title; cascading delete

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-006        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-005, BRD-FR-006, BRD-FR-007, BRD-FR-008, BRD-FR-037, BRD-FR-041–044 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
