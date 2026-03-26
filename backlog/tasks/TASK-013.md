# Task: Implement Course Management Pydantic Models

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-013             |
| **Story**    | STORY-006            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Implement all Pydantic v2 request/response models for the Course Management service: `CourseCreate`, `CourseUpdate`, `CourseOut`, `ModuleCreate`, `ModuleUpdate`, `ModuleOut`, `LessonCreate`, `LessonUpdate`, `LessonOut`, `QuizQuestionCreate`, `QuizQuestionUpdate`, and `QuizQuestionOut`.

## Implementation Details

**Files to create/modify:**
- `src/course_management/__init__.py` — empty package marker
- `src/course_management/models.py` — all Pydantic models
- `src/course_management/exceptions.py` — `CourseNotFoundError`, `ModuleNotFoundError`, `LessonNotFoundError`, `DuplicateCourseError`, `InvalidStatusTransitionError`

**Approach:**
Key models (based on course-management-service LLD):
```python
class CourseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    difficulty: Literal["beginner", "intermediate", "advanced"]
    estimated_duration: int = Field(gt=0)
    target_audience: str = Field(max_length=500)
    learning_objectives: list[str] = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    is_ai_generated: bool = False

class QuizQuestionCreate(BaseModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=5)  # 2-5 options
    correct_answer: str
    explanation: str
    sort_order: int = 0
    
    @field_validator("correct_answer")
    def correct_answer_must_be_in_options(cls, v, values):
        if "options" in values.data and v not in values.data["options"]:
            raise ValueError("correctAnswer must be one of the options")
        return v
```

All `*Out` models include `model_config = {"from_attributes": True}` for ORM compatibility.

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

- [ ] `QuizQuestionCreate` with < 2 options raises `ValidationError`
- [ ] `QuizQuestionCreate` with `correctAnswer` not in `options` raises `ValidationError`
- [ ] `CourseCreate` with `title` < 3 chars raises `ValidationError`
- [ ] All `*Out` models can be constructed from SQLAlchemy ORM objects (`from_attributes=True`)
- [ ] `CourseOut` supports optional nested `modules` list

## Test Requirements

- **Unit tests:** Test validation rules for each model (boundary values, invalid literals)
- **Integration tests:** N/A
- **Edge cases:** `QuizQuestionCreate` with exactly 2 options and 5 options; `CourseCreate` with empty `tags`

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-006        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-010, BRD-FR-012 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
