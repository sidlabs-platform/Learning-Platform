# Task: Implement Quiz Submission Service

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-024             |
| **Story**    | STORY-011            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement `submit_quiz()` and `evaluate_quiz_score()` in the progress tracking service. These functions record individual `QuizAttempt` records, evaluate correctness server-side by comparing against `correctAnswer` from the DB, compute the score summary, and apply the module's passing threshold.

## Implementation Details

**Files to create/modify:**
- `src/progress_tracking/service.py` — add `submit_quiz()` and `evaluate_quiz_score()` (extends TASK-023)

**Approach:**
```python
async def submit_quiz(db: AsyncSession, user_id: str, enrollment_id: str, moduleId: str, answers: list[QuizAnswer]) -> QuizScoreResponse:
    # Load all quiz questions for the module
    questions = await get_quiz_questions_for_module(db, moduleId)
    if not questions:
        raise QuizAttemptError("No quiz questions found for this module")
    
    question_map = {q.id: q for q in questions}
    correct_count = 0
    
    # Record QuizAttempt for each answer; evaluate server-side
    for answer in answers:
        question = question_map.get(answer.question_id)
        if not question:
            continue
        is_correct = answer.selected_answer == question.correct_answer
        if is_correct:
            correct_count += 1
        attempt = QuizAttempt(
            id=_uuid(), user_id=user_id,
            quiz_question_id=answer.question_id,
            selected_answer=answer.selected_answer,
            is_correct=is_correct,
            attempted_at=datetime.utcnow()
        )
        db.add(attempt)
    
    await db.flush()
    return await evaluate_quiz_score(db, moduleId, correct_count, len(questions))

async def evaluate_quiz_score(db, module_id, correct, total) -> QuizScoreResponse:
    module = await db.get(Module, module_id)
    percentage = (correct / total * 100) if total > 0 else 0
    
    if module.is_quiz_informational:
        passed = True  # Informational: always passes
    else:
        passed = percentage >= (module.quiz_passing_score or 100)
    
    return QuizScoreResponse(
        correct=correct, total=total,
        percentage=round(percentage, 1), passed=passed
    )
```

## API Changes

N/A — service layer.

## Data Model Changes

N/A — writes to `quiz_attempts` table.

## Dependencies

| Prerequisite Task | Reason                                       |
|-------------------|----------------------------------------------|
| TASK-021          | Enrollment service required                  |
| TASK-017          | Quiz question service required               |
| TASK-023          | Auto-complete called after quiz submit        |

**Wave:** 6

## Acceptance Criteria

- [ ] `submit_quiz()` creates one `QuizAttempt` record per submitted answer
- [ ] `isCorrect` is computed server-side (not from client input)
- [ ] Informational quizzes always return `passed=True`
- [ ] Module with `quizPassingScore=80` and 75% score returns `passed=False`
- [ ] Module with `quizPassingScore=80` and 80% score returns `passed=True` (boundary)
- [ ] `auto_complete_enrollment()` is called after `submit_quiz()` completes

## Test Requirements

- **Unit tests:** Test `evaluate_quiz_score()` with various correct/total/threshold combinations; test `is_quiz_informational=True`
- **Integration tests:** Submit quiz → verify QuizAttempt records; verify score response; verify enrollment completion triggered
- **Edge cases:** Submit quiz with unknown question IDs (skip gracefully); module with `quizPassingScore=0` (always passes); all wrong answers

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-011        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-022, BRD-FR-023, BRD-FR-024, BRD-FR-025 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
