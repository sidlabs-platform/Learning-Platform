# Task: Initialise Project Structure and pyproject.toml

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-001             |
| **Story**    | STORY-001            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Create the complete Python project directory layout, `pyproject.toml` with all pinned dependencies, a `.env.example` documenting all environment variables, and a basic `README.md` with setup instructions. This is the first task in the project — it unblocks everything else.

## Implementation Details

**Files to create/modify:**
- `pyproject.toml` — project metadata, dependencies (fastapi, uvicorn, sqlalchemy, aiosqlite, alembic, pydantic-settings, python-jose, passlib[bcrypt], httpx, bleach, jinja2), dev dependencies (pytest, pytest-asyncio, httpx, respx)
- `src/__init__.py` — empty package marker
- `src/config/__init__.py` — empty package marker
- `.env.example` — template with all required/optional env vars documented
- `README.md` — quickstart instructions (uv sync, alembic upgrade head, uvicorn start)
- `.gitignore` — Python, .env, *.db, __pycache__ ignores
- `tests/__init__.py` — empty package marker
- `tests/conftest.py` — placeholder for shared pytest fixtures

**Approach:**
Use `uv init` pattern with `pyproject.toml`. Pin all dependency versions explicitly. Use `src/` layout (not flat). The `src/` directory contains all application packages. Tests live in `tests/` at root level. Match the directory structure defined in all LLD documents exactly.

## API Changes

N/A — project setup only.

## Data Model Changes

N/A — no database yet.

## Dependencies

> None — this is the root task with no prerequisites.

| Prerequisite Task | Reason |
|-------------------|--------|
| None              | —      |

**Wave:** 0

## Acceptance Criteria

- [ ] `pyproject.toml` lists all required production and dev dependencies with version pins
- [ ] `uv sync` completes without errors in a clean Python 3.11+ environment
- [ ] `src/` directory exists with correct package hierarchy
- [ ] `.env.example` documents `GITHUB_MODELS_API_KEY`, `GITHUB_MODELS_ENDPOINT`, `SECRET_KEY`, `DATABASE_URL`, `ENVIRONMENT`, `AI_MAX_RETRIES`, `AI_REQUEST_TIMEOUT_SECONDS`, `CORS_ORIGINS`
- [ ] `.gitignore` excludes `.env`, `*.db`, `__pycache__`, `.venv`

## Test Requirements

- **Unit tests:** No unit tests for project structure
- **Integration tests:** `uv sync && python -c "import src"` passes
- **Edge cases:** Verify `pyproject.toml` parses correctly with `uv pip check`

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-001        |
| Epic     | EPIC-001         |
| BRD      | BRD-NFR-005      |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
