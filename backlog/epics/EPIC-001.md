# Epic: Infrastructure & Project Setup

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-001             |
| **Status**  | Ready                |
| **Owner**   | 4-develop-agent      |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 1             |

## Goal / Objective

Establish the complete project skeleton — dependency manifest, application entry-point, configuration management, SQLAlchemy ORM layer, Alembic migration pipeline, and database seed script — so every downstream service team can build on a stable, runnable foundation from day one.

## Business Value

Without a working project structure, database schema, and seed data, no feature can be developed or tested. This epic is the bedrock that unblocks all parallel development streams and ensures the three mandatory starter courses (GitHub Foundations, GitHub Advanced Security, GitHub Actions) are available on first launch.

## BRD Requirements Mapped

| BRD ID        | Description                                                              |
|---------------|--------------------------------------------------------------------------|
| BRD-FR-041    | Seeded GitHub Foundations course with 5 modules on first launch          |
| BRD-FR-042    | Seeded GitHub Advanced Security course with 5 modules on first launch    |
| BRD-FR-043    | Seeded GitHub Actions course with 5 modules on first launch              |
| BRD-FR-044    | Each seeded course has summary, 3–5 modules, 1–3 lessons, ≥1 quiz       |
| BRD-NFR-003   | SQLite supports up to 50 concurrent learners                              |
| BRD-NFR-005   | Secrets never hardcoded; loaded from environment variables               |

## Features

| Feature ID | Name                                   | Priority (P0/P1/P2) | Status  |
|------------|----------------------------------------|----------------------|---------|
| FEAT-001   | Project structure and dependencies     | P0                   | Planned |
| FEAT-002   | Application settings via pydantic-settings | P0               | Planned |
| FEAT-003   | FastAPI application initialization     | P0                   | Planned |
| FEAT-004   | SQLAlchemy ORM models (all 10 entities)| P0                   | Planned |
| FEAT-005   | Alembic migrations (initial schema)    | P0                   | Planned |
| FEAT-006   | Database seed script (3 starter courses) | P0                 | Planned |

## Acceptance Criteria

1. Running `uv run alembic upgrade head` creates all 10 tables in `learning_platform.db` and seeds the 3 starter courses.
2. Running `uv run uvicorn src.main:app --reload --port 8000` starts the server without errors when required env vars are set.
3. All 10 ORM models have correct FK relationships, constraints (UNIQUE, CHECK), and cascade-delete behaviours as defined in the data-layer LLD.
4. The seed script is idempotent — running it twice does not duplicate data.
5. Application startup fails fast with a clear validation error if `GITHUB_MODELS_API_KEY`, `GITHUB_MODELS_ENDPOINT`, or `SECRET_KEY` are missing.

## Dependencies & Risks

**Dependencies:**
- Python 3.11+ runtime
- SQLite file system access
- uv package manager

**Risks:**
- SQLite async driver (`aiosqlite`) compatibility with SQLAlchemy 2.x async — mitigate by pinning versions in `pyproject.toml`
- Seed script complexity for three full courses — mitigate by iterative testing after each course is added

## Out of Scope

- Business logic for any feature (Auth, Course Management, AI, Progress, Reporting)
- Frontend templates or static assets
- Docker/container configuration

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
