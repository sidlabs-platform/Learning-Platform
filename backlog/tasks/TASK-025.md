# Task: Implement Progress Tracking Router

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-025             |
| **Story**    | STORY-009            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the FastAPI router for all progress tracking endpoints: enrollment CRUD, progress recording, resume-lesson, quiz submission, and quiz score retrieval. Apply RBAC and own-data isolation as appropriate.

## Implementation Details

**Files to create/modify:**
- `src/progress_tracking/router.py` — FastAPI `APIRouter` for enrollment, progress, and quiz endpoints
- `src/main.py` — register `progress_tracking.router`

**Approach:**
```python
router = APIRouter(tags=["progress"])

# Enrollments
@router.post("/api/v1/enrollments", response_model=EnrollmentOut, status_code=201)
async def enroll(data: EnrollmentCreate, db=Depends(get_db), current_user=Depends(require_authenticated_user)):
    # Admin can enroll any user; Learner can only self-enroll
    if current_user.role == "learner" and data.user_id != current_user.sub:
        raise HTTPException(403)
    return await create_enrollment(db, data.user_id, data.course_id, current_user.role)

@router.get("/api/v1/enrollments/{enrollment_id}", response_model=EnrollmentOut)
async def get_enrollment_endpoint(enrollment_id: str, db=Depends(get_db), current_user=Depends(require_authenticated_user)):
    enrollment = await get_enrollment(db, enrollment_id)
    # Own data check
    if current_user.role == "learner" and enrollment.user_id != current_user.sub:
        raise HTTPException(403)
    percentage = await calculate_completion_percentage(db, enrollment_id)
    out = EnrollmentOut.model_validate(enrollment)
    out.completion_percentage = percentage
    return out

@router.get("/api/v1/enrollments/{enrollment_id}/resume")
async def resume(enrollment_id: str, db=Depends(get_db), current_user=Depends(require_authenticated_user)):
    lesson_id = await get_resume_lesson(db, enrollment_id)
    return {"lesson_id": lesson_id}

# Progress recording
@router.post("/api/v1/progress", response_model=EnrollmentOut)
async def record_progress(data: ProgressRecordCreate, db=Depends(get_db), current_user=Depends(require_authenticated_user)):
    if data.completed:
        return await mark_lesson_complete(db, current_user.sub, data.lesson_id, data.enrollment_id)
    else:
        await record_lesson_view(db, current_user.sub, data.lesson_id, data.enrollment_id)

# Quiz submission
@router.post("/api/v1/enrollments/{enrollment_id}/quiz-submit", response_model=QuizScoreResponse)
async def quiz_submit(enrollment_id: str, submission: QuizSubmission, db=Depends(get_db), current_user=Depends(require_authenticated_user)):
    return await submit_quiz(db, current_user.sub, enrollment_id, submission.module_id, submission.answers)
```

## API Changes

| Endpoint                                         | Method | Auth       | Description                                |
|--------------------------------------------------|--------|------------|--------------------------------------------|
| `/api/v1/enrollments`                            | POST   | Any (auth) | Create enrollment                          |
| `/api/v1/enrollments/{id}`                       | GET    | Any (auth) | Get enrollment with completionPercentage   |
| `/api/v1/enrollments`                            | GET    | Any (auth) | List enrollments (own for learners, all for admins) |
| `/api/v1/enrollments/{id}/resume`                | GET    | Any (auth) | Get last-accessed lesson ID                |
| `/api/v1/progress`                               | POST   | Any (auth) | Record lesson view or completion           |
| `/api/v1/enrollments/{id}/quiz-submit`           | POST   | Any (auth) | Submit quiz answers and get score          |

## Data Model Changes

N/A — service layer implemented in prior tasks.

## Dependencies

| Prerequisite Task | Reason                                         |
|-------------------|------------------------------------------------|
| TASK-021          | Enrollment service required                    |
| TASK-022          | Progress recording service required            |
| TASK-023          | Auto-complete service required                 |
| TASK-024          | Quiz submission service required               |
| TASK-010          | RBAC dependencies required                     |

**Wave:** 7

## Acceptance Criteria

- [ ] `POST /api/v1/enrollments` (Learner) with another user's ID returns 403
- [ ] `POST /api/v1/enrollments` duplicate returns 409
- [ ] `GET /api/v1/enrollments/{id}` includes `completionPercentage`
- [ ] `GET /api/v1/enrollments/{id}/resume` returns `{"lesson_id": "..."}`
- [ ] `POST /api/v1/progress` with `completed=true` triggers auto-completion check
- [ ] `POST /api/v1/enrollments/{id}/quiz-submit` returns `{ correct, total, percentage, passed }`

## Test Requirements

- **Unit tests:** Test router RBAC enforcement
- **Integration tests:** Full enrollment → view lesson → mark complete → resume flow; quiz submit and score
- **Edge cases:** Resume with no lessons viewed returns `{"lesson_id": null}`

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-009        |
| Epic     | EPIC-004         |
| BRD      | BRD-FR-014–025   |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
