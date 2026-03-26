# Task: Implement Module and Lesson Service Functions

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-016             |
| **Story**    | STORY-007            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement CRUD service functions for Modules and Lessons in `src/course_management/service.py`: `create_module()`, `update_module()`, `delete_module()`, `create_lesson()`, `update_lesson()`, and `delete_lesson()`. Lessons must have `markdownContent` sanitised via `sanitise_markdown()` on every write. Manual lesson edits set `isAiGenerated=False`.

## Implementation Details

**Files to create/modify:**
- `src/course_management/service.py` — add module and lesson CRUD functions (extends TASK-015)

**Approach:**
```python
async def create_module(db: AsyncSession, course_id: str, data: ModuleCreate) -> Module:
    # Verify course exists
    await get_course_or_404(course_id, db)
    module = Module(**data.model_dump(), id=_uuid(), course_id=course_id)
    db.add(module)
    await db.flush()
    return module

async def create_lesson(db: AsyncSession, module_id: str, data: LessonCreate) -> Lesson:
    # Sanitise markdown content before storage
    sanitised_content = sanitise_markdown(data.markdown_content)
    lesson = Lesson(
        **data.model_dump(exclude={"markdown_content"}),
        markdown_content=sanitised_content,
        id=_uuid(), module_id=module_id
    )
    db.add(lesson)
    await db.flush()
    return lesson

async def update_lesson(db: AsyncSession, lesson_id: str, data: LessonUpdate) -> Lesson:
    lesson = await get_lesson_or_404(lesson_id, db)
    if data.markdown_content:
        lesson.markdown_content = sanitise_markdown(data.markdown_content)
        lesson.is_ai_generated = False  # Manual edit clears AI flag
    # Update other fields
    await db.flush()
    return lesson
```

Modules ordered by `sort_order` — ordering enforced in queries, not DB constraints (for flexibility).

## API Changes

N/A — service functions only.

## Data Model Changes

N/A — reads/writes `modules` and `lessons` tables.

## Dependencies

| Prerequisite Task | Reason                                         |
|-------------------|------------------------------------------------|
| TASK-015          | Course service (get_course_or_404) must exist  |
| TASK-014          | `sanitise_markdown()` required for lessons     |

**Wave:** 5

## Acceptance Criteria

- [ ] `create_lesson()` stores sanitised `markdownContent` (script tags stripped)
- [ ] `update_lesson()` re-sanitises content and sets `isAiGenerated=False`
- [ ] `create_module()` fails with 404 if `courseId` does not exist
- [ ] Deleting a module cascades to delete its lessons and quiz questions
- [ ] Modules are returned ordered by `sortOrder` ascending in `get_course_detail()`

## Test Requirements

- **Unit tests:** Test `sanitise_markdown` integration in `create_lesson()`; test `isAiGenerated` flag reset on update
- **Integration tests:** Create course → create module → create lesson → verify sanitisation; delete module → verify cascade
- **Edge cases:** Create lesson with empty `markdownContent`; update non-existent lesson → 404

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-007        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-011, BRD-FR-013, BRD-FR-037, BRD-FR-039 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
