# Task: Implement Quiz Question Service Functions

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-017             |
| **Story**    | STORY-007            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Implement CRUD service functions for QuizQuestions: `create_quiz_question()`, `update_quiz_question()`, and `delete_quiz_question()`. QuizQuestion validation enforces 2–5 options and requires `correctAnswer` to be one of the `options` values.

## Implementation Details

**Files to create/modify:**
- `src/course_management/service.py` — add quiz question CRUD functions (extends TASK-016)

**Approach:**
```python
async def create_quiz_question(db: AsyncSession, module_id: str, data: QuizQuestionCreate) -> QuizQuestion:
    # Verify module exists
    await get_module_or_404(module_id, db)
    # Pydantic validation already enforces 2-5 options and correct_answer in options
    quiz = QuizQuestion(**data.model_dump(), id=_uuid(), module_id=module_id)
    db.add(quiz)
    await db.flush()
    return quiz

async def get_quiz_questions_for_module(db: AsyncSession, module_id: str) -> list[QuizQuestion]:
    result = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.module_id == module_id)
        .order_by(QuizQuestion.sort_order)
    )
    return result.scalars().all()

async def update_quiz_question(db: AsyncSession, question_id: str, data: QuizQuestionUpdate) -> QuizQuestion:
    question = await get_quiz_question_or_404(question_id, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    await db.flush()
    return question
```

## API Changes

N/A — service functions only.

## Data Model Changes

N/A — reads/writes `quiz_questions` table.

## Dependencies

| Prerequisite Task | Reason                                      |
|-------------------|---------------------------------------------|
| TASK-016          | Module service (get_module_or_404) must exist|

**Wave:** 5 (parallel with TASK-016)

## Acceptance Criteria

- [ ] `create_quiz_question()` with < 2 options raises `ValidationError` (Pydantic catches before service layer)
- [ ] `create_quiz_question()` with `correctAnswer` not in `options` raises `ValidationError`
- [ ] `create_quiz_question()` with valid data returns `QuizQuestion` ORM object
- [ ] `get_quiz_questions_for_module()` returns questions ordered by `sortOrder`
- [ ] `delete_quiz_question()` removes the record without affecting the module

## Test Requirements

- **Unit tests:** Test Pydantic validation for options/correctAnswer; test `get_quiz_questions_for_module()` ordering
- **Integration tests:** Create quiz question → retrieve in module detail
- **Edge cases:** `create_quiz_question()` for non-existent module → 404; 5 options (max); 2 options (min)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-007        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-012, BRD-FR-022 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
