# Task: Implement Enrollment Service

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-021             |
| **Story**    | STORY-009            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the enrollment business logic in `src/progress_tracking/service.py`: `create_enrollment()` for both admin-created and self-enrollment, `get_enrollment()`, `list_enrollments_for_user()`, and enrollment validation (duplicate detection, published course check for self-enrollment).

## Implementation Details

**Files to create/modify:**
- `src/progress_tracking/service.py` — enrollment service functions
- `src/progress_tracking/dependencies.py` — `get_enrollment_or_404()`, `assert_enrolled()` FastAPI dependencies

**Approach:**
```python
async def create_enrollment(db: AsyncSession, user_id: str, course_id: str, created_by_role: str) -> Enrollment:
    # For self-enrollment (learner), verify course is published
    if created_by_role == "learner":
        course = await db.get(Course, course_id)
        if not course or course.status != "published":
            raise CourseNotFoundError(f"Course {course_id} not found or not published")
    
    # Check for duplicate
    existing = await db.execute(
        select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
    )
    if existing.scalar_one_or_none():
        raise DuplicateEnrollmentError("Already enrolled")
    
    enrollment = Enrollment(
        id=_uuid(), user_id=user_id, course_id=course_id,
        status="not_started", enrolled_at=datetime.utcnow()
    )
    db.add(enrollment)
    await db.flush()
    return enrollment

async def get_enrollment(db: AsyncSession, enrollment_id: str) -> Enrollment:
    enrollment = await db.get(Enrollment, enrollment_id)
    if not enrollment:
        raise EnrollmentNotFoundError(f"Enrollment {enrollment_id} not found")
    return enrollment

async def list_enrollments_for_user(db: AsyncSession, user_id: str) -> list[Enrollment]:
    result = await db.execute(select(Enrollment).where(Enrollment.user_id == user_id))
    return result.scalars().all()
```

## API Changes

N/A — service layer.

## Data Model Changes

N/A — reads/writes `enrollments` table.

## Dependencies

| Prerequisite Task | Reason                                    |
|-------------------|-------------------------------------------|
| TASK-005          | Enrollment ORM model required             |
| TASK-020          | Pydantic models and exceptions required   |

**Wave:** 4

## Acceptance Criteria

- [ ] `create_enrollment()` returns `Enrollment` with `status=not_started`
- [ ] Duplicate enrollment raises `DuplicateEnrollmentError`
- [ ] Self-enrollment in unpublished course raises `CourseNotFoundError`
- [ ] `list_enrollments_for_user()` returns only that user's enrollments

## Test Requirements

- **Unit tests:** Test duplicate detection; test self-enrollment published/unpublished check
- **Integration tests:** Admin creates enrollment; learner self-enrolls; duplicate returns 409
- **Edge cases:** Enroll in non-existent course; list enrollments for user with no enrollments

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-009        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-014, BRD-FR-015, BRD-FR-016 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
