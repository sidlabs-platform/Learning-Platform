# Task: Write Progress Tracking Tests

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-026             |
| **Story**    | STORY-010            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Write comprehensive pytest tests for the progress tracking service and router, covering enrollment, progress recording, resume-lesson, quiz submission, and enrollment auto-completion.

## Implementation Details

**Files to create/modify:**
- `tests/test_progress_tracking.py` — progress tracking integration tests

**Approach:**
```python
class TestEnrollment:
    async def test_admin_can_enroll_user(admin_client, seeded_course): ...
    async def test_learner_self_enrollment_published_course(learner_client, published_course): ...
    async def test_self_enrollment_unpublished_returns_404(learner_client, draft_course): ...
    async def test_duplicate_enrollment_returns_409(admin_client): ...
    async def test_learner_cannot_enroll_another_user(learner_client): ...

class TestProgressRecording:
    async def test_record_lesson_view_creates_progress_record(learner_client): ...
    async def test_record_lesson_view_updates_last_viewed_at_on_repeat(learner_client): ...
    async def test_mark_lesson_complete_sets_completed_flag(learner_client): ...
    async def test_completion_percentage_increases_after_lesson_complete(learner_client): ...
    async def test_progress_survives_repeat_view(learner_client): ...
    async def test_resume_lesson_returns_last_accessed(learner_client): ...

class TestQuizSubmission:
    async def test_submit_quiz_records_attempts(learner_client): ...
    async def test_quiz_score_computed_server_side(learner_client): ...
    async def test_informational_quiz_always_passes(learner_client): ...
    async def test_quiz_pass_threshold_enforced(learner_client): ...

class TestAutoCompletion:
    async def test_enrollment_completes_when_all_done(learner_client): ...
    async def test_enrollment_stays_in_progress_if_quiz_not_passed(learner_client): ...
```

## API Changes

N/A — test file only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                       |
|-------------------|----------------------------------------------|
| TASK-025          | Progress tracking router must be implemented |

**Wave:** 8

## Acceptance Criteria

- [ ] All tests pass with `pytest -v`
- [ ] Test for progress-survives-refresh explicitly verifies `lastViewedAt` is unchanged after second view call
- [ ] Test coverage for progress tracking module ≥ 80%
- [ ] Server-side quiz evaluation test verifies client cannot fake `isCorrect`

## Test Requirements

- **Unit tests:** `calculate_completion_percentage()` with known data; `evaluate_quiz_score()` boundary values
- **Integration tests:** Full enrollment lifecycle; progress recording; quiz submit
- **Edge cases:** Empty lesson course; informational quiz; already-completed enrollment

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-010        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-014–025, BRD-NFR-010 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
