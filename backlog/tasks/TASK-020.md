# Task: Implement Progress Tracking Pydantic Models

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-020             |
| **Story**    | STORY-009            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement all Pydantic v2 request/response models for the Progress Tracking service: `EnrollmentCreate`, `EnrollmentOut`, `ProgressRecordCreate`, `ProgressRecordOut`, `QuizAnswer`, `QuizSubmission`, and `QuizScoreResponse`.

## Implementation Details

**Files to create/modify:**
- `src/progress_tracking/__init__.py` — empty package marker
- `src/progress_tracking/models.py` — all Pydantic models
- `src/progress_tracking/exceptions.py` — `EnrollmentNotFoundError`, `DuplicateEnrollmentError`, `QuizAttemptError`

**Approach:**
```python
class EnrollmentCreate(BaseModel):
    user_id: str
    course_id: str

class EnrollmentOut(BaseModel):
    id: str
    user_id: str
    course_id: str
    enrolled_at: datetime
    status: Literal["not_started", "in_progress", "completed"]
    completed_at: Optional[datetime] = None
    last_lesson_id: Optional[str] = None
    completion_percentage: int = Field(ge=0, le=100, default=0)
    model_config = {"from_attributes": True}

class ProgressRecordCreate(BaseModel):
    lesson_id: str
    enrollment_id: str
    completed: bool = False

class QuizAnswer(BaseModel):
    question_id: str
    selected_answer: str

class QuizSubmission(BaseModel):
    module_id: str
    answers: list[QuizAnswer] = Field(min_length=1)

class QuizScoreResponse(BaseModel):
    correct: int
    total: int
    percentage: float = Field(ge=0, le=100)
    passed: bool
```

## API Changes

N/A — models only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                              |
|-------------------|-------------------------------------|
| TASK-003          | FastAPI app (for imports)           |

**Wave:** 2

## Acceptance Criteria

- [ ] `EnrollmentOut.completion_percentage` validates 0–100 range
- [ ] `EnrollmentOut.status` only accepts valid literal values
- [ ] `QuizSubmission.answers` rejects empty list
- [ ] All `*Out` models support `from_attributes=True` for ORM compatibility

## Test Requirements

- **Unit tests:** Test model validation boundaries
- **Integration tests:** N/A
- **Edge cases:** `completion_percentage=101` raises ValidationError; empty `answers` list raises ValidationError

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-009        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-014, BRD-FR-019, BRD-FR-024 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
