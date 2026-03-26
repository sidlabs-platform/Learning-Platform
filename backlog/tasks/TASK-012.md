# Task: Write Auth Service Tests

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-012             |
| **Story**    | STORY-004            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Write comprehensive pytest tests for the auth service, RBAC dependencies, and auth router endpoints using `httpx.AsyncClient` for integration tests and an in-memory SQLite test database via a shared pytest fixture.

## Implementation Details

**Files to create/modify:**
- `tests/conftest.py` — shared `async_client` fixture (httpx.AsyncClient with test app and in-memory DB), `admin_token_cookie` and `learner_token_cookie` fixtures
- `tests/test_auth.py` — all auth test cases

**Approach:**
```python
# conftest.py
@pytest.fixture
async def async_client():
    # Override DATABASE_URL with in-memory SQLite
    # Apply all migrations to test DB
    # Seed test users (admin and learner)
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# test_auth.py
async def test_login_success(async_client): ...
async def test_login_wrong_password(async_client): ...
async def test_login_unknown_email(async_client): ...
async def test_logout_clears_cookie(async_client): ...
async def test_me_requires_auth(async_client): ...
async def test_admin_only_route_with_learner_token(async_client): ...
async def test_learner_cannot_access_other_user_data(async_client): ...
```

## API Changes

N/A — test file only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                          |
|-------------------|-------------------------------------------------|
| TASK-011          | Auth router must be implemented                 |
| TASK-010          | RBAC dependencies must be implemented           |

**Wave:** 6

## Acceptance Criteria

- [ ] All test functions in `test_auth.py` pass with `pytest -v`
- [ ] Test coverage for auth module ≥ 80%
- [ ] In-memory SQLite test DB is used (not the production DB)
- [ ] Tests run in isolation (no shared state between tests via DB transactions rollback)
- [ ] `test_learner_cannot_access_other_user_data` verifies the 403 response

## Test Requirements

- **Unit tests:** `verify_password`, `hash_password`, `create_access_token`, `decode_access_token`
- **Integration tests:** Full login → me → logout flow; role-based 403; own-data 403
- **Edge cases:** Expired token; missing cookie; malformed JWT; password with special characters

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-004        |
| Epic     | EPIC-002         |
| BRD      | BRD-FR-001, BRD-FR-003, BRD-FR-004 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
