# Task: Implement Reporting Service (Dashboard + CSV Export)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-036             |
| **Story**    | STORY-017            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5h                   |

## Description

Implement the reporting business logic in `src/reporting/service.py`: `get_dashboard_metrics()` (aggregated enrollment counts, completion rates, quiz score summaries), `get_per_course_metrics()`, `get_quiz_score_summary()`, and `generate_csv_export()` using Python's `csv.writer` with `StreamingResponse`.

## Implementation Details

**Files to create/modify:**
- `src/reporting/service.py` — all reporting service functions

**Approach:**
```python
from sqlalchemy import func, select
from fastapi.responses import StreamingResponse
import csv
import io

async def get_dashboard_metrics(db: AsyncSession, course_id=None, user_id=None) -> DashboardResponse:
    # Total learners
    learner_count = await db.scalar(
        select(func.count(User.id)).where(User.role == "learner")
    )
    
    # Total enrollments (with optional filters)
    enroll_stmt = select(func.count(Enrollment.id))
    if course_id:
        enroll_stmt = enroll_stmt.where(Enrollment.course_id == course_id)
    if user_id:
        enroll_stmt = enroll_stmt.where(Enrollment.user_id == user_id)
    total_enrollments = await db.scalar(enroll_stmt)
    
    # Completion rate
    completed = await db.scalar(
        enroll_stmt.where(Enrollment.status == "completed")
    )
    completion_rate = (completed / total_enrollments * 100) if total_enrollments > 0 else 0
    
    course_metrics = await get_per_course_metrics(db, course_id)
    quiz_summaries = await get_quiz_score_summary(db, course_id)
    
    return DashboardResponse(
        total_learners=learner_count or 0,
        total_enrollments=total_enrollments or 0,
        overall_completion_rate=round(completion_rate, 1),
        course_metrics=course_metrics,
        quiz_summaries=quiz_summaries,
        learner_summaries=[]
    )

async def generate_csv_export(db, course_id=None, user_id=None, status_filter=None):
    """Returns FastAPI StreamingResponse with CSV data."""
    async def csv_generator():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["userId", "userName", "courseId", "courseTitle",
                        "enrollmentStatus", "completionPercentage", "lastActivity"])
        yield output.getvalue()
        output.truncate(0)
        output.seek(0)
        
        # Query enrollments with joined user and course data
        stmt = (
            select(Enrollment, User, Course)
            .join(User, Enrollment.user_id == User.id)
            .join(Course, Enrollment.course_id == Course.id)
        )
        if course_id:
            stmt = stmt.where(Enrollment.course_id == course_id)
        if user_id:
            stmt = stmt.where(Enrollment.user_id == user_id)
        
        result = await db.execute(stmt)
        for enrollment, user, course in result:
            # Calculate completion percentage
            writer.writerow([
                user.id, user.name, course.id, course.title,
                enrollment.status, 0, enrollment.enrolled_at.isoformat()
            ])
            yield output.getvalue()
            output.truncate(0)
            output.seek(0)
    
    return StreamingResponse(
        csv_generator(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=progress_export.csv"}
    )
```

## API Changes

N/A — service layer.

## Data Model Changes

N/A — read-only queries across multiple tables.

## Dependencies

| Prerequisite Task | Reason                                   |
|-------------------|------------------------------------------|
| TASK-005          | ORM models (Enrollment, User, Course, etc.) |
| TASK-035          | Reporting Pydantic models required       |

**Wave:** 5

## Acceptance Criteria

- [ ] `get_dashboard_metrics()` returns correct `total_learners` count
- [ ] `get_dashboard_metrics(course_id=X)` scopes all metrics to course X
- [ ] `generate_csv_export()` returns `StreamingResponse` with `text/csv` media type
- [ ] CSV headers match spec: userId, userName, courseId, courseTitle, enrollmentStatus, completionPercentage, lastActivity
- [ ] Empty dataset returns headers-only CSV (valid format, no error)

## Test Requirements

- **Unit tests:** Test `get_dashboard_metrics()` with known seeded data; verify all aggregation values
- **Integration tests:** CSV export returns valid CSV; filter by courseId narrows rows
- **Edge cases:** Zero enrollments; all-completed enrollments; course with no quiz questions

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
