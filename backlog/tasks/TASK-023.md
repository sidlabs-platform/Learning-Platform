# Task: Implement Auto-Completion and Enrollment Status Machine

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-023             |
| **Story**    | STORY-010            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Implement `auto_complete_enrollment()` which checks if all required lessons are complete and all mandatory quizzes are passed, then transitions the enrollment to `completed`. This function is called after every `mark_lesson_complete()` and `submit_quiz()` operation.

## Implementation Details

**Files to create/modify:**
- `src/progress_tracking/service.py` — add `auto_complete_enrollment()` function (extends TASK-022)

**Approach:**
```python
async def auto_complete_enrollment(db: AsyncSession, enrollment_id: str) -> Enrollment:
    enrollment = await db.get(Enrollment, enrollment_id)
    if enrollment.status == "completed":
        return enrollment  # Already done
    
    # Check all lessons complete
    percentage = await calculate_completion_percentage(db, enrollment_id)
    if percentage < 100:
        return enrollment
    
    # Check all non-informational quizzes passed
    modules_result = await db.execute(
        select(Module).where(Module.course_id == enrollment.course_id, Module.is_quiz_informational == False)
    )
    mandatory_quiz_modules = modules_result.scalars().all()
    
    for module in mandatory_quiz_modules:
        # Check if learner has passed this module's quiz
        # Count correct attempts vs total questions; compare to quizPassingScore
        questions = await get_quiz_questions_for_module(db, module.id)
        if not questions:
            continue
        attempts = await db.execute(
            select(QuizAttempt).where(
                QuizAttempt.user_id == enrollment.user_id,
                QuizAttempt.quiz_question_id.in_([q.id for q in questions])
            ).order_by(QuizAttempt.attempted_at.desc())
        )
        latest_attempts = attempts.scalars().all()
        # Check if latest attempt score meets passing threshold
        passing = _check_quiz_passed(questions, latest_attempts, module.quiz_passing_score)
        if not passing:
            return enrollment  # Quiz not yet passed; don't complete
    
    # All conditions met — complete the enrollment
    enrollment.status = "completed"
    enrollment.completed_at = datetime.utcnow()
    await db.flush()
    return enrollment
```

## API Changes

N/A — service function.

## Data Model Changes

N/A — writes to `enrollments` table.

## Dependencies

| Prerequisite Task | Reason                                         |
|-------------------|------------------------------------------------|
| TASK-022          | Progress recording service (calculate_completion_percentage) |
| TASK-017          | Quiz question service (get_quiz_questions_for_module) |

**Wave:** 6

## Acceptance Criteria

- [ ] Enrollment transitions to `completed` when all lessons are marked complete AND all mandatory quizzes are passed
- [ ] Enrollment stays `in_progress` if any mandatory quiz is not yet passed
- [ ] Informational quizzes (`isQuizInformational=True`) do not block completion
- [ ] `completedAt` is set when status transitions to `completed`
- [ ] Already-completed enrollment is returned unchanged (no re-completion)

## Test Requirements

- **Unit tests:** Test completion logic with various lesson/quiz completion states
- **Integration tests:** Full course completion flow: enroll → complete all lessons → submit quiz → verify enrollment completed
- **Edge cases:** Course with no quiz questions; course where all modules are informational; course with mix of informational and mandatory quizzes

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-010        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-020, BRD-FR-025 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
