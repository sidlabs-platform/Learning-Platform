# Task: Implement Progress Recording Service

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-022             |
| **Story**    | STORY-010            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement `record_lesson_view()`, `mark_lesson_complete()`, `calculate_completion_percentage()`, and `get_resume_lesson()` in the progress tracking service. These functions handle the core lesson progress lifecycle with idempotent upserts to ensure progress survives page refreshes.

## Implementation Details

**Files to create/modify:**
- `src/progress_tracking/service.py` — add progress recording functions (extends TASK-021)

**Approach:**
```python
async def record_lesson_view(db: AsyncSession, user_id: str, lesson_id: str, enrollment_id: str) -> ProgressRecord:
    """Upsert ProgressRecord.lastViewedAt; transition enrollment to in_progress if first lesson."""
    now = datetime.utcnow()
    
    # SQLite upsert (INSERT OR REPLACE equivalent via on_conflict_do_update)
    stmt = insert(ProgressRecord).values(
        id=_uuid(), user_id=user_id, lesson_id=lesson_id,
        last_viewed_at=now, completed=False
    ).on_conflict_do_update(
        index_elements=["user_id", "lesson_id"],
        set_={"last_viewed_at": now}
    )
    await db.execute(stmt)
    
    # Transition enrollment to in_progress if currently not_started
    enrollment = await db.get(Enrollment, enrollment_id)
    if enrollment and enrollment.status == "not_started":
        enrollment.status = "in_progress"
        enrollment.last_lesson_id = lesson_id
    elif enrollment:
        enrollment.last_lesson_id = lesson_id
    
    await db.flush()

async def mark_lesson_complete(db: AsyncSession, user_id: str, lesson_id: str, enrollment_id: str) -> EnrollmentOut:
    now = datetime.utcnow()
    # Update ProgressRecord to completed
    stmt = update(ProgressRecord).where(
        ProgressRecord.user_id == user_id,
        ProgressRecord.lesson_id == lesson_id
    ).values(completed=True, completed_at=now)
    await db.execute(stmt)
    
    # Recalculate and potentially auto-complete
    percentage = await calculate_completion_percentage(db, enrollment_id)
    enrollment = await auto_complete_enrollment(db, enrollment_id)
    return EnrollmentOut.model_validate(enrollment)

async def calculate_completion_percentage(db: AsyncSession, enrollment_id: str) -> int:
    enrollment = await db.get(Enrollment, enrollment_id)
    # Count total lessons in course vs completed ProgressRecords
    total_result = await db.execute(
        select(func.count()).select_from(Lesson).join(Module).where(Module.course_id == enrollment.course_id)
    )
    total = total_result.scalar() or 0
    if total == 0:
        return 0
    completed_result = await db.execute(
        select(func.count()).select_from(ProgressRecord).where(
            ProgressRecord.user_id == enrollment.user_id,
            ProgressRecord.completed == True
        ).join(Lesson).join(Module).where(Module.course_id == enrollment.course_id)
    )
    completed = completed_result.scalar() or 0
    return min(100, int((completed / total) * 100))

async def get_resume_lesson(db: AsyncSession, enrollment_id: str) -> str | None:
    enrollment = await db.get(Enrollment, enrollment_id)
    return enrollment.last_lesson_id if enrollment else None
```

## API Changes

N/A — service layer.

## Data Model Changes

N/A — reads/writes `progress_records`, `enrollments`.

## Dependencies

| Prerequisite Task | Reason                                     |
|-------------------|--------------------------------------------|
| TASK-021          | Enrollment service (get_enrollment) exists |
| TASK-005          | ORM models (ProgressRecord, Lesson, Module)|

**Wave:** 5

## Acceptance Criteria

- [ ] `record_lesson_view()` creates `ProgressRecord` with `lastViewedAt` on first call
- [ ] `record_lesson_view()` updates `lastViewedAt` on subsequent calls (upsert, not duplicate)
- [ ] `record_lesson_view()` transitions enrollment from `not_started` to `in_progress`
- [ ] `mark_lesson_complete()` sets `completed=True` and `completedAt`
- [ ] `calculate_completion_percentage()` returns correct integer 0–100
- [ ] `get_resume_lesson()` returns the last viewed lesson ID

## Test Requirements

- **Unit tests:** Test percentage calculation with known complete/total counts
- **Integration tests:** Open lesson (record view) → mark complete → verify percentage; refresh test
- **Edge cases:** Complete all lessons in a course; zero lessons in course; record_lesson_view called twice (idempotent)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-010        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-017, BRD-FR-018, BRD-FR-019, BRD-FR-021, BRD-NFR-010 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
