# Task: Implement AI Generation Router (Trigger + Status Poll)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-032             |
| **Story**    | STORY-014            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the AI generation API router (`src/ai_generation/router.py`) with: `POST /api/v1/ai/generate-course` (returns 202 immediately, dispatches BackgroundTask), `GET /api/v1/ai/requests/{id}` (status poll), and `GET /api/v1/ai/requests` (audit log list). Wire `_run_generation_task()` background function.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/router.py` — FastAPI APIRouter for generation endpoints
- `src/main.py` — register `ai_generation.router`

**Approach:**
```python
router = APIRouter(prefix="/api/v1/ai", tags=["ai-generation"])

@router.post("/generate-course", response_model=GenerationStatusResponse, status_code=202)
async def trigger_course_generation(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin)
):
    # Create ContentGenerationRequest record (status=pending)
    gen_request = ContentGenerationRequest(
        id=_uuid(), prompt_text=str(request.model_dump()),
        model_used="gpt-4o", requester_id=admin.sub,
        status="pending", created_at=datetime.utcnow()
    )
    db.add(gen_request)
    await db.commit()
    
    # Dispatch background task
    background_tasks.add_task(_run_generation_task, gen_request.id, request, admin.sub)
    
    logger.info(f"AI generation triggered: request_id={gen_request.id} admin_id={admin.sub}")
    return GenerationStatusResponse(request_id=gen_request.id, status="pending")

async def _run_generation_task(request_id: str, gen_request: GenerationRequest, admin_id: str):
    """BackgroundTask: prompt → model call → persist → update status."""
    # Get fresh DB session (BackgroundTask needs its own session)
    async with AsyncSessionLocal() as db:
        try:
            # Update status to in_progress
            req = await db.get(ContentGenerationRequest, request_id)
            req.status = "in_progress"
            await db.commit()
            
            start_time = datetime.utcnow()
            # Build prompt
            prompt, template_id = render_course_generation_prompt(gen_request)
            req.prompt_text = prompt  # Store rendered prompt for audit
            
            # Call GitHub Models
            client = GitHubModelsClient()
            raw_json = await client.generate(prompt)
            
            # Persist draft course
            course_id = await persist_generated_course(db, raw_json, request_id, admin_id)
            
            # Mark completed
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            req.status = "completed"
            req.course_id = course_id  # Store for status poll
            req.completed_at = datetime.utcnow()
            req.latency_ms = latency_ms
            await db.commit()
            logger.info(f"AI generation completed: request_id={request_id} latency_ms={latency_ms}")
        
        except (GenerationFailedError, SchemaValidationError) as e:
            req.status = "failed"
            req.error_message = str(e)
            req.completed_at = datetime.utcnow()
            await db.commit()
            logger.error(f"AI generation failed: request_id={request_id} error={e}")

@router.get("/requests/{request_id}", response_model=GenerationStatusResponse)
async def get_generation_status(request_id: str, db=Depends(get_db), admin=Depends(require_admin)):
    req = await db.get(ContentGenerationRequest, request_id)
    if not req:
        raise HTTPException(404)
    return GenerationStatusResponse(
        request_id=req.id, status=req.status,
        course_id=getattr(req, "course_id", None),
        error_message=req.error_message,
        latency_ms=req.latency_ms
    )

@router.get("/requests", response_model=list[GenerationStatusResponse])
async def list_generation_requests(db=Depends(get_db), admin=Depends(require_admin)):
    result = await db.execute(
        select(ContentGenerationRequest).order_by(ContentGenerationRequest.created_at.desc())
    )
    return [GenerationStatusResponse(...) for req in result.scalars().all()]
```

## API Changes

| Endpoint                          | Method | Auth  | Description                                  |
|-----------------------------------|--------|-------|----------------------------------------------|
| `/api/v1/ai/generate-course`      | POST   | Admin | Trigger course generation (202 + requestId)  |
| `/api/v1/ai/requests/{id}`        | GET    | Admin | Poll generation status                       |
| `/api/v1/ai/requests`             | GET    | Admin | List all generation requests (audit log)     |

## Data Model Changes

N/A — uses `content_generation_requests` and `content_generation_artifacts` tables (defined in TASK-005).

## Dependencies

| Prerequisite Task | Reason                                           |
|-------------------|--------------------------------------------------|
| TASK-028          | Prompt service (render_course_generation_prompt) |
| TASK-029          | GitHub Models client (GitHubModelsClient)        |
| TASK-031          | Content persistence layer (persist_generated_course) |
| TASK-010          | RBAC (require_admin)                             |

**Wave:** 7

## Acceptance Criteria

- [ ] `POST /api/v1/ai/generate-course` returns 202 within 500ms
- [ ] `ContentGenerationRequest` created in DB with `status=pending` before background task starts
- [ ] After successful background task, `GET /api/v1/ai/requests/{id}` returns `status=completed` with `courseId`
- [ ] After failed task, status is `failed` with `errorMessage`
- [ ] `GET /api/v1/ai/requests/{id}` by Learner returns 403
- [ ] `latencyMs` is recorded on completion

## Test Requirements

- **Unit tests:** Test 202 response and immediate return; test status poll responses
- **Integration tests:** Mock `GitHubModelsClient.generate()` with `respx`; full generation flow with mock; test failure flow
- **Edge cases:** Poll non-existent request ID → 404; generation with missing required fields → 422

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-014        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-029, BRD-FR-031, BRD-FR-032, BRD-NFR-002, BRD-NFR-014, BRD-INT-010 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
