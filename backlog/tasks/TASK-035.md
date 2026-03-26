# Task: Implement Reporting Pydantic Models

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-035             |
| **Story**    | STORY-017            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement all Pydantic v2 models for the Reporting service: `QuizModuleSummary`, `CourseMetrics`, `LearnerSummary`, `DashboardResponse`, and `LearnerProgressRow` (for CSV export).

## Implementation Details

**Files to create/modify:**
- `src/reporting/__init__.py` — empty package marker
- `src/reporting/models.py` — all Pydantic models
- `src/reporting/exceptions.py` — `ReportGenerationError`

**Approach:**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class QuizModuleSummary(BaseModel):
    module_id: str
    module_title: str
    course_id: str
    total_attempts: int
    average_score: float = Field(ge=0, le=100)
    pass_count: int
    fail_count: int

class CourseMetrics(BaseModel):
    course_id: str
    course_title: str
    total_enrollments: int
    completed_count: int
    in_progress_count: int
    not_started_count: int
    completion_rate: float = Field(ge=0, le=100)
    avg_quiz_score: Optional[float] = None

class LearnerSummary(BaseModel):
    user_id: str
    user_name: str
    total_enrollments: int
    completed_count: int
    in_progress_count: int

class DashboardResponse(BaseModel):
    total_learners: int
    total_enrollments: int
    overall_completion_rate: float = Field(ge=0, le=100)
    course_metrics: list[CourseMetrics]
    quiz_summaries: list[QuizModuleSummary]
    learner_summaries: list[LearnerSummary]

class LearnerProgressRow(BaseModel):
    """Single row in CSV export."""
    user_id: str
    user_name: str
    course_id: str
    course_title: str
    enrollment_status: str
    completion_percentage: int
    last_activity: Optional[datetime] = None
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

- [ ] `CourseMetrics.completion_rate` validates 0–100 range
- [ ] `DashboardResponse` contains all five metric categories
- [ ] `LearnerProgressRow` contains all required CSV column fields
- [ ] All models importable from `src.reporting.models`

## Test Requirements

- **Unit tests:** Test `CourseMetrics` with boundary values for `completion_rate`
- **Integration tests:** N/A
- **Edge cases:** `avg_quiz_score=None` (no quiz attempts yet) is valid

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-017        |
| Epic     | EPIC-006         |
| BRD      | BRD-FR-026, BRD-FR-027, BRD-FR-028 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
