# Task: Implement Course Management Service (Course CRUD + Catalog)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-015             |
| **Story**    | STORY-006            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5h                   |

## Description

Implement the core course business logic in `src/course_management/service.py`: creating and updating courses, retrieving the published catalog with filters, getting full course detail with nested structure, and the publish/unpublish workflow with logging.

## Implementation Details

**Files to create/modify:**
- `src/course_management/service.py` — all course-level service functions
- `src/course_management/dependencies.py` — `get_course_or_404()` FastAPI dependency

**Approach:**
Key functions to implement:
```python
async def create_course(db: AsyncSession, data: CourseCreate, requester_id: str) -> Course:
    course = Course(**data.model_dump(), id=_uuid(), created_at=utcnow())
    db.add(course)
    await db.flush()
    return course

async def get_course_catalog(db, difficulty=None, tag=None, include_drafts=False) -> list[CourseOut]:
    stmt = select(Course)
    if not include_drafts:
        stmt = stmt.where(Course.status == "published")
    if difficulty:
        stmt = stmt.where(Course.difficulty == difficulty)
    # tag filter: load all published courses, filter in Python (SQLite JSON)
    result = await db.execute(stmt)
    courses = result.scalars().all()
    if tag:
        courses = [c for c in courses if tag in (c.tags or [])]
    return courses

async def get_course_detail(db, course_id, include_drafts=False) -> Course:
    # Eager load modules -> lessons, quiz_questions ordered by sort_order

async def publish_course(db, course_id, admin_id) -> Course:
    course = await get_course_or_404(course_id, db)
    if course.status == "published":
        raise InvalidStatusTransitionError("Already published")
    course.status = "published"
    course.published_at = datetime.utcnow()
    logger.info(f"Course published: course_id={course_id} admin_id={admin_id}")
    await db.flush()
    return course

async def unpublish_course(db, course_id, admin_id) -> Course:
    # Similar to publish but transitions to "draft"
```

## API Changes

N/A — service layer.

## Data Model Changes

N/A — reads/writes `courses` table.

## Dependencies

| Prerequisite Task | Reason                                      |
|-------------------|---------------------------------------------|
| TASK-005          | Course ORM model required                   |
| TASK-013          | Course Pydantic models required             |
| TASK-014          | sanitise_markdown used in lesson creation   |

**Wave:** 4

## Acceptance Criteria

- [ ] `create_course()` returns a `Course` ORM object with `status=draft`
- [ ] `get_course_catalog(include_drafts=False)` returns only `status=published` courses
- [ ] `get_course_catalog(difficulty="beginner")` filters correctly
- [ ] `get_course_catalog(tag="github-actions")` filters by tag
- [ ] `publish_course()` sets `status=published` and `published_at`
- [ ] `publish_course()` on already-published course raises `InvalidStatusTransitionError`
- [ ] `unpublish_course()` sets `status=draft`

## Test Requirements

- **Unit tests:** Test each function with mocked `AsyncSession`
- **Integration tests:** Test catalog filtering with seeded data; test publish/unpublish transitions
- **Edge cases:** Catalog with no published courses returns empty list; filter with no matches

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-006        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-005, BRD-FR-006, BRD-FR-007, BRD-FR-008, BRD-FR-038 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
