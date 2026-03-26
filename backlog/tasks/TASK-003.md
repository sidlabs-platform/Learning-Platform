# Task: Bootstrap FastAPI Application with Middleware

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-003             |
| **Story**    | STORY-001            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Create the FastAPI application entry point (`src/main.py`) with CORS middleware, a `/health` readiness endpoint, Jinja2 template configuration, static file serving, and the application lifespan handler that creates database tables on startup.

## Implementation Details

**Files to create/modify:**
- `src/main.py` — FastAPI app factory, middleware registration, router inclusion, lifespan handler
- `src/static/` — directory placeholder (css/, js/ subdirs)
- `src/templates/` — directory placeholder

**Approach:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if not exist (Alembic handles migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Learning Platform MVP", lifespan=lifespan)

# Add CORSMiddleware with settings.cors_origins
# Mount /static for StaticFiles
# Include all service routers (auth, courses, ai, progress, reporting, frontend)
# Add GET /health endpoint
```

CORS: Parse `settings.cors_origins` as comma-separated list. Never use `allow_origins=["*"]`.

## API Changes

| Endpoint        | Method | Description              |
|-----------------|--------|--------------------------|
| `/health`       | GET    | Returns `{"status": "ok"}` |

**Response body:**
```json
{"status": "ok", "environment": "development"}
```

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                   |
|-------------------|------------------------------------------|
| TASK-002          | Settings module required for CORS config |

**Wave:** 1

## Acceptance Criteria

- [ ] `GET /health` returns `200 {"status": "ok"}` when server is running
- [ ] CORS middleware is configured from `settings.cors_origins` (no wildcard `*`)
- [ ] Static files are served from `/static/`
- [ ] Application starts and all imported routers load without import errors
- [ ] Jinja2Templates configured to load from `src/templates/`

## Test Requirements

- **Unit tests:** Test `/health` endpoint returns 200
- **Integration tests:** Test CORS headers present on response with Origin header
- **Edge cases:** Test that `cors_origins="*"` is not accepted in production environment

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-001        |
| Epic     | EPIC-001         |
| BRD      | BRD-NFR-007      |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
