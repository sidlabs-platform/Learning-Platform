# Story: Project Skeleton and Dependency Setup

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-001            |
| **Epic**     | EPIC-001             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** developer,
**I want** a correctly structured Python project with all dependencies declared and a working FastAPI application skeleton,
**so that** every team member can clone the repository, install dependencies with a single command, and start the server locally.

## Acceptance Criteria

1. **Given** the repository is cloned and Python 3.11+ is available,
   **When** `uv sync` is run,
   **Then** all dependencies install without errors and a virtual environment is created.

2. **Given** the environment file `.env` is populated with required variables,
   **When** `uv run uvicorn src.main:app --reload --port 8000` is run,
   **Then** the server starts and `GET http://localhost:8000/health` returns `{"status": "ok"}`.

3. **Given** a missing required environment variable (e.g., `SECRET_KEY`),
   **When** the application starts,
   **Then** it fails immediately with a clear `pydantic-settings` validation error.

## BRD & Design References

| BRD ID        | HLD/LLD Component                        |
|---------------|------------------------------------------|
| BRD-NFR-005   | COMP-006 Data Layer — pydantic-settings config |
| BRD-NFR-003   | COMP-006 Data Layer — single process     |

## Tasks Breakdown

| Task ID  | Description                                        | Estimate |
|----------|----------------------------------------------------|----------|
| TASK-001 | Initialise project structure and pyproject.toml   | 3h       |
| TASK-002 | Implement pydantic-settings configuration module  | 2h       |
| TASK-003 | Bootstrap FastAPI application (main.py + middleware) | 3h     |

## UI/UX Notes

N/A — API only. Health endpoint is for readiness checking.

## Technical Notes

- **Stack:** Python 3.11, FastAPI, pydantic-settings, Uvicorn
- **Key considerations:** Use `uv` for dependency management; pin all versions in `pyproject.toml`; `.env.example` must document all required and optional vars
- **Configuration:** `GITHUB_MODELS_API_KEY`, `GITHUB_MODELS_ENDPOINT`, `SECRET_KEY`, `DATABASE_URL`, `ENVIRONMENT`, `AI_MAX_RETRIES`, `AI_REQUEST_TIMEOUT_SECONDS`, `CORS_ORIGINS`

## Dependencies

- None — this is the root story of the project

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
