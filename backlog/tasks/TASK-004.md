# Task: Implement SQLAlchemy Base, Engine, and Session

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-004             |
| **Story**    | STORY-002            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Set up the SQLAlchemy async engine, session factory, `get_db()` FastAPI dependency, and the `Base` declarative class that all ORM models inherit from. This is the foundation of the data layer — all service code depends on these components.

## Implementation Details

**Files to create/modify:**
- `src/database/__init__.py` — package marker, exports `Base`, `get_db`, `AsyncSessionLocal`
- `src/database/base.py` — `DeclarativeBase` subclass (`Base`) and `JSONList` TypeDecorator
- `src/database/engine.py` — `create_async_engine()` call; `AsyncSessionLocal = async_sessionmaker()`
- `src/database/session.py` — `get_db()` FastAPI dependency as async generator

**Approach:**
```python
# engine.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
engine = create_async_engine(settings.database_url, echo=settings.environment == "development")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# session.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

`JSONList` TypeDecorator: stores `list[str]` as JSON string; `process_bind_param` = `json.dumps`; `process_result_value` = `json.loads`; `cache_ok = True`.

## API Changes

N/A

## Data Model Changes

- Establishes `Base` class for all ORM models
- Configures SQLite + aiosqlite async engine

## Dependencies

| Prerequisite Task | Reason                                        |
|-------------------|-----------------------------------------------|
| TASK-002          | Settings module needed for DATABASE_URL value |

**Wave:** 1

## Acceptance Criteria

- [ ] `get_db()` yields an `AsyncSession` and auto-commits on success
- [ ] `get_db()` rolls back on exception and re-raises
- [ ] `JSONList` TypeDecorator round-trips `["a", "b"]` correctly through the DB
- [ ] `Base` is importable from `src.database`
- [ ] Engine uses `aiosqlite` driver (URL prefix `sqlite+aiosqlite://`)

## Test Requirements

- **Unit tests:** Test `JSONList` TypeDecorator serialisation/deserialisation
- **Integration tests:** Test `get_db()` dependency commits and rolls back correctly
- **Edge cases:** Test `JSONList` with empty list `[]` and `None` value

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-002        |
| Epic     | EPIC-001         |
| BRD      | BRD-NFR-003      |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
