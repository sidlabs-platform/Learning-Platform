# Task: Set Up Alembic and Initial Schema Migration

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-006             |
| **Story**    | STORY-002            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Initialise Alembic for the project, configure it to use the async SQLAlchemy engine, and create the initial migration `001_initial_schema.py` that creates all 10 database tables with their indexes, constraints, and FK relationships.

## Implementation Details

**Files to create/modify:**
- `alembic.ini` — Alembic configuration (script location, DB URL reference via env)
- `src/database/migrations/env.py` — Alembic environment: configures async engine, imports `Base.metadata` from all ORM models
- `src/database/migrations/script.py.mako` — Migration script template
- `src/database/migrations/versions/001_initial_schema.py` — Initial DDL: CREATE TABLE statements for all 10 tables, indexes on FK columns and `users.email`

**Approach:**
Use `alembic init src/database/migrations` and configure `env.py` to use `AsyncEngine` with `run_sync()` pattern:
```python
# env.py
def run_migrations_online() -> None:
    connectable = engine
    with connectable.sync_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
```

The migration script uses `op.create_table()` calls for each of the 10 tables, exactly matching the ORM model definitions. Include explicit indexes:
- `idx_users_email` on `users(email)`
- `idx_enrollments_user_id` on `enrollments(user_id)`
- `idx_enrollments_course_id` on `enrollments(course_id)`
- `idx_progress_records_user_id` on `progress_records(user_id)`

## API Changes

N/A

## Data Model Changes

- Creates all 10 tables in `learning_platform.db` when migration is run
- Creates indexes for frequently queried FK columns

## Dependencies

| Prerequisite Task | Reason                                        |
|-------------------|-----------------------------------------------|
| TASK-005          | ORM models required to define table metadata  |

**Wave:** 3

## Acceptance Criteria

- [ ] `uv run alembic upgrade head` completes without errors on a fresh database
- [ ] All 10 tables exist after migration
- [ ] `idx_users_email` unique index exists
- [ ] `uv run alembic downgrade base` removes all tables
- [ ] Migration is idempotent (running twice with `upgrade head` is a no-op)
- [ ] `alembic current` shows the migration as applied

## Test Requirements

- **Unit tests:** N/A — migration tested by running it
- **Integration tests:** Run migration in test DB; verify all tables exist; run downgrade and confirm tables removed
- **Edge cases:** Test migration on existing DB (upgrade is no-op if already applied)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-002        |
| Epic     | EPIC-001         |
| BRD      | BRD-FR-041       |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
