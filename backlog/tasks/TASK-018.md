# Task: Implement Course Management Router

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-018             |
| **Story**    | STORY-006            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the FastAPI router for all course management endpoints: course CRUD, catalog listing with filters, course detail, publish/unpublish, and module/lesson/quiz CRUD endpoints. Wire up RBAC dependencies so admin-only endpoints are gated correctly.

## Implementation Details

**Files to create/modify:**
- `src/course_management/router.py` — FastAPI `APIRouter` with all course management endpoints
- `src/main.py` — register `course_management.router`

**Approach:**
```python
router = APIRouter(prefix="/api/v1/courses", tags=["courses"])

@router.get("", response_model=list[CourseOut])
async def list_courses(
    difficulty: str | None = None, tag: str | None = None,
    db=Depends(get_db), current_user=Depends(require_authenticated_user)
):
    include_drafts = current_user.role == "admin"
    return await get_course_catalog(db, difficulty, tag, include_drafts)

@router.post("", response_model=CourseOut, status_code=201)
async def create_course_endpoint(data: CourseCreate, db=Depends(get_db), admin=Depends(require_admin)):
    return await create_course(db, data, admin.sub)

@router.patch("/{course_id}/publish", response_model=CourseOut)
async def publish(course_id: str, db=Depends(get_db), admin=Depends(require_admin)):
    return await publish_course(db, course_id, admin.sub)

@router.patch("/{course_id}/unpublish", response_model=CourseOut)
async def unpublish(course_id: str, db=Depends(get_db), admin=Depends(require_admin)):
    return await unpublish_course(db, course_id, admin.sub)

# Module endpoints: POST /courses/{id}/modules, PATCH /courses/{id}/modules/{mid}, DELETE ...
# Lesson endpoints: POST /courses/{id}/modules/{mid}/lessons, PATCH /lessons/{lid}, DELETE ...
# Quiz endpoints: POST /courses/{id}/modules/{mid}/quiz-questions, PATCH /quiz-questions/{qid}
```

Map exceptions to HTTP status codes in exception handlers: `CourseNotFoundError` → 404, `InvalidStatusTransitionError` → 409.

## API Changes

| Endpoint                                    | Method | Auth    | Description                       |
|---------------------------------------------|--------|---------|-----------------------------------|
| `/api/v1/courses`                           | GET    | Any     | List courses (published for learners, all for admins) |
| `/api/v1/courses`                           | POST   | Admin   | Create new course                 |
| `/api/v1/courses/{id}`                      | GET    | Any     | Get course detail with nested structure |
| `/api/v1/courses/{id}`                      | PATCH  | Admin   | Update course metadata            |
| `/api/v1/courses/{id}`                      | DELETE | Admin   | Delete course                     |
| `/api/v1/courses/{id}/publish`              | PATCH  | Admin   | Publish course                    |
| `/api/v1/courses/{id}/unpublish`            | PATCH  | Admin   | Unpublish course                  |
| `/api/v1/courses/{id}/modules`              | POST   | Admin   | Create module                     |
| `/api/v1/courses/{id}/modules/{mid}`        | PATCH  | Admin   | Update module                     |
| `/api/v1/courses/{id}/modules/{mid}/lessons`| POST   | Admin   | Create lesson                     |
| `/api/v1/lessons/{lid}`                     | PATCH  | Admin   | Update lesson content             |
| `/api/v1/courses/{id}/modules/{mid}/quiz-questions` | POST | Admin | Create quiz question        |

## Data Model Changes

N/A — service layer implemented in prior tasks.

## Dependencies

| Prerequisite Task | Reason                                           |
|-------------------|--------------------------------------------------|
| TASK-015          | Course service functions required                |
| TASK-016          | Module and lesson service functions required     |
| TASK-017          | Quiz question service functions required         |
| TASK-010          | RBAC dependencies (require_admin) required       |
| TASK-011          | Auth router must be registered (for consistency) |

**Wave:** 6

## Acceptance Criteria

- [ ] `GET /api/v1/courses` returns only published courses for Learner sessions
- [ ] `POST /api/v1/courses` with Learner token returns 403
- [ ] `PATCH /api/v1/courses/{id}/publish` with Admin token changes status to published
- [ ] Missing required fields on `POST /api/v1/courses` return 422 with field-level errors
- [ ] `GET /api/v1/courses/{id}` returns full nested course structure

## Test Requirements

- **Unit tests:** Test router error mapping (CourseNotFoundError → 404)
- **Integration tests:** Full CRUD flow: create course → add module → add lesson → publish → get catalog
- **Edge cases:** Publish already-published course → 409; get non-existent course → 404; filter with no matches → empty list

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-006        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-005, BRD-FR-006, BRD-FR-007, BRD-FR-008, BRD-FR-009 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
