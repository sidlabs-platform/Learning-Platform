# Task: Implement AI Generation Pydantic Models

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-030             |
| **Story**    | STORY-013            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement all Pydantic v2 models for the AI Generation service: `GenerationRequest`, `GenerationStatusResponse`, `GeneratedCourseSchema` (for validating GPT-4o JSON output), `GeneratedModuleSchema`, `GeneratedLessonSchema`, `GeneratedQuizQuestionSchema`, `SectionRegenerationRequest`, and `PromptTemplate`.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/models.py` — all Pydantic models for AI generation

**Approach:**
```python
class GenerationRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    target_audience: str = Field(max_length=500)
    learning_objectives: list[str] = Field(min_length=1)
    difficulty: Literal["beginner", "intermediate", "advanced"]
    desired_module_count: int = Field(ge=1, le=10, default=5)
    preferred_tone: Optional[str] = "professional"

class GenerationStatusResponse(BaseModel):
    request_id: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    course_id: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: Optional[int] = None

# Schemas for validating GPT-4o response
class GeneratedQuizQuestionSchema(BaseModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=5)
    correct_answer: str
    explanation: str

class GeneratedLessonSchema(BaseModel):
    title: str
    markdown_content: str
    estimated_minutes: int = Field(ge=1, le=120, default=10)

class GeneratedModuleSchema(BaseModel):
    title: str
    summary: str = ""
    lessons: list[GeneratedLessonSchema] = Field(min_length=1)
    quiz_questions: list[GeneratedQuizQuestionSchema] = Field(default_factory=list)

class GeneratedCourseSchema(BaseModel):
    title: str
    description: str
    target_audience: str = ""
    learning_objectives: list[str] = Field(default_factory=list)
    modules: list[GeneratedModuleSchema] = Field(min_length=1)

class SectionRegenerationRequest(BaseModel):
    section_type: Literal["lesson", "quiz", "module_summary"]
    section_id: str
    context: Optional[dict] = None
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

- [ ] `GenerationRequest` with `desired_module_count=0` raises `ValidationError`
- [ ] `GeneratedCourseSchema` with empty `modules` list raises `ValidationError`
- [ ] `GeneratedQuizQuestionSchema` with < 2 options raises `ValidationError`
- [ ] `GenerationStatusResponse` accepts all four status literals
- [ ] All models are importable from `src.ai_generation.models`

## Test Requirements

- **Unit tests:** Test `GenerationRequest` validation; test `GeneratedCourseSchema` with sample GPT-4o response JSON
- **Integration tests:** N/A
- **Edge cases:** `desired_module_count=10` (max boundary); module with zero quiz questions (valid)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-013        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-029, BRD-INT-006 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
