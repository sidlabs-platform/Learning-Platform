# Task: Implement Content Persistence Layer (AI Generation)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-031             |
| **Story**    | STORY-014            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5h                   |

## Description

Implement the Content Persistence Layer (`src/ai_generation/content_service.py`): validate the raw JSON response from GPT-4o against `GeneratedCourseSchema`, sanitise all Markdown content via `sanitise_markdown()`, and persist draft Course/Modules/Lessons/QuizQuestions with `isAiGenerated=True`, then insert a `ContentGenerationArtifact` record.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/content_service.py` — `persist_generated_course()`, `persist_generated_section()`

**Approach:**
```python
import json
from pydantic import ValidationError
from src.course_management.sanitiser import sanitise_markdown
from src.course_management.service import create_course, create_module, create_lesson, create_quiz_question
from .models import GeneratedCourseSchema
from .exceptions import SchemaValidationError

async def persist_generated_course(db: AsyncSession, raw_json: str, request_id: str, admin_id: str) -> str:
    """Validate JSON, sanitise Markdown, insert draft course. Returns courseId."""
    try:
        data = json.loads(raw_json)
        schema = GeneratedCourseSchema(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise SchemaValidationError(f"AI response does not match expected schema: {e}")
    
    # Create draft Course
    from src.course_management.models import CourseCreate
    course_data = CourseCreate(
        title=schema.title, description=schema.description,
        difficulty="beginner",  # Default; admin can update
        estimated_duration=sum(
            lesson.estimated_minutes
            for module in schema.modules
            for lesson in module.lessons
        ),
        target_audience=schema.target_audience,
        learning_objectives=schema.learning_objectives,
        tags=[],
        is_ai_generated=True
    )
    course = await create_course(db, course_data, admin_id)
    
    for sort_order, module_data in enumerate(schema.modules):
        # Create module
        module = await create_module(db, course.id, ModuleCreate(
            title=module_data.title, summary=module_data.summary,
            sort_order=sort_order, is_ai_generated=True
        ))
        
        # Create lessons with sanitised content
        for lesson_order, lesson_data in enumerate(module_data.lessons):
            sanitised = sanitise_markdown(lesson_data.markdown_content)
            await create_lesson(db, module.id, LessonCreate(
                title=lesson_data.title,
                markdown_content=sanitised,
                estimated_minutes=lesson_data.estimated_minutes,
                sort_order=lesson_order, is_ai_generated=True
            ))
        
        # Create quiz questions
        for quiz_data in module_data.quiz_questions:
            await create_quiz_question(db, module.id, QuizQuestionCreate(
                question=quiz_data.question, options=quiz_data.options,
                correct_answer=quiz_data.correct_answer,
                explanation=quiz_data.explanation, is_ai_generated=True
            ))
    
    # Insert ContentGenerationArtifact
    artifact = ContentGenerationArtifact(
        id=_uuid(), source_request_id=request_id,
        generated_content=raw_json, content_type="course"
    )
    db.add(artifact)
    await db.flush()
    
    return course.id
```

## API Changes

N/A — service layer.

## Data Model Changes

N/A — writes to all course-related tables and `content_generation_artifacts`.

## Dependencies

| Prerequisite Task | Reason                                          |
|-------------------|-------------------------------------------------|
| TASK-028          | Prompt service and GeneratedCourseSchema models |
| TASK-030          | AI generation Pydantic models (GeneratedCourseSchema) |
| TASK-015          | Course management service functions (create_course, etc.) |
| TASK-016          | Module and lesson service functions             |
| TASK-017          | Quiz question service functions                 |
| TASK-014          | `sanitise_markdown()` required                  |

**Wave:** 6

## Acceptance Criteria

- [ ] Valid GPT-4o JSON response creates all Course, Module, Lesson, QuizQuestion records with `isAiGenerated=True` and `status=draft`
- [ ] All Markdown in lessons is sanitised via `sanitise_markdown()` before storage
- [ ] Invalid JSON raises `SchemaValidationError`
- [ ] JSON that doesn't match `GeneratedCourseSchema` raises `SchemaValidationError`
- [ ] `ContentGenerationArtifact` is inserted with the raw JSON
- [ ] Function returns the new `courseId`

## Test Requirements

- **Unit tests:** Test with valid schema JSON; test with invalid JSON; test with schema mismatch
- **Integration tests:** Full persist flow with test DB; verify all records created correctly
- **Edge cases:** GPT-4o returns extra fields (should be ignored by Pydantic); module with no quiz questions (valid)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-014        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-030, BRD-FR-031, BRD-INT-006 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
