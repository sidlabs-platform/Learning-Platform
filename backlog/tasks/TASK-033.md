# Task: Implement Section Regeneration Router

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-033             |
| **Story**    | STORY-015            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the Review Workflow Layer (`src/ai_generation/review_router.py`) with the `POST /api/v1/ai/regenerate-section` endpoint that triggers a scoped regeneration for a single module, lesson, or quiz section without regenerating the whole course.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/review_router.py` — `trigger_section_regeneration()` endpoint and `_run_section_regeneration_task()` background function
- `src/ai_generation/content_service.py` — add `persist_generated_section()` function

**Approach:**
```python
# review_router.py
review_router = APIRouter(prefix="/api/v1/ai", tags=["ai-generation"])

@review_router.post("/regenerate-section", response_model=GenerationStatusResponse, status_code=202)
async def regenerate_section(
    request: SectionRegenerationRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    admin=Depends(require_admin)
):
    gen_request = ContentGenerationRequest(
        id=_uuid(), model_used="gpt-4o",
        requester_id=admin.sub, status="pending",
        created_at=datetime.utcnow()
    )
    db.add(gen_request)
    await db.commit()
    background_tasks.add_task(_run_section_regeneration_task, gen_request.id, request, admin.sub)
    return GenerationStatusResponse(request_id=gen_request.id, status="pending")

async def _run_section_regeneration_task(request_id, regen_request, admin_id):
    async with AsyncSessionLocal() as db:
        try:
            req = await db.get(ContentGenerationRequest, request_id)
            req.status = "in_progress"
            await db.commit()
            
            start_time = datetime.utcnow()
            context = regen_request.context or {}
            prompt, template_id = render_section_regeneration_prompt(regen_request.section_type, context)
            req.prompt_text = prompt
            
            client = GitHubModelsClient()
            raw_json = await client.generate(prompt)
            
            await persist_generated_section(db, raw_json, regen_request.section_type, regen_request.section_id, request_id)
            
            req.status = "completed"
            req.completed_at = datetime.utcnow()
            req.latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            await db.commit()
        
        except Exception as e:
            req.status = "failed"
            req.error_message = str(e)
            req.completed_at = datetime.utcnow()
            await db.commit()
```

## API Changes

| Endpoint                           | Method | Auth  | Description                                        |
|------------------------------------|--------|-------|----------------------------------------------------|
| `/api/v1/ai/regenerate-section`    | POST   | Admin | Trigger scoped regeneration for one section (202)  |

**Request body:**
```json
{
  "section_type": "lesson",
  "section_id": "uuid-of-lesson",
  "context": {"course_title": "...", "module_title": "...", "lesson_title": "..."}
}
```

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                              |
|-------------------|-----------------------------------------------------|
| TASK-032          | AI generation router pattern and background task approach |
| TASK-028          | `render_section_regeneration_prompt()` required     |
| TASK-031          | `persist_generated_section()` required              |

**Wave:** 8

## Acceptance Criteria

- [ ] `POST /api/v1/ai/regenerate-section` returns 202 immediately
- [ ] Only the targeted section (lesson/quiz/module) is updated; other content unchanged
- [ ] A new `ContentGenerationRequest` is created for the section regeneration
- [ ] On failure, `ContentGenerationRequest.status=failed` with error message
- [ ] Learner session returns 403

## Test Requirements

- **Unit tests:** Test background task dispatches correctly; test section type → template mapping
- **Integration tests:** Mock GitHub Models client; regenerate a lesson; verify only that lesson updated
- **Edge cases:** Invalid `sectionId` → handled gracefully in background task (marked as failed)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-015        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-034, BRD-INT-008 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
