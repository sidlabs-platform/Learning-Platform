# Task: Implement Reporting Router and Tests

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-037             |
| **Story**    | STORY-017            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 4h                   |

## Description

Implement the reporting FastAPI router (`src/reporting/router.py`) with `GET /api/v1/reports/dashboard` and `GET /api/v1/reports/export` endpoints, then write the reporting tests in `tests/test_reporting.py`.

## Implementation Details

**Files to create/modify:**
- `src/reporting/router.py` — FastAPI APIRouter with dashboard and export endpoints
- `src/main.py` — register `reporting.router`
- `tests/test_reporting.py` — reporting integration tests

**Approach:**
```python
router = APIRouter(prefix="/api/v1/reports", tags=["reporting"])

@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    course_id: str | None = None,
    user_id: str | None = None,
    db=Depends(get_db),
    admin=Depends(require_admin)
):
    logger.info(f"Dashboard requested: admin_id={admin.sub} course_id={course_id} user_id={user_id}")
    return await get_dashboard_metrics(db, course_id, user_id)

@router.get("/export")
async def export_csv(
    course_id: str | None = None,
    user_id: str | None = None,
    format: str = "csv",
    db=Depends(get_db),
    admin=Depends(require_admin)
):
    logger.info(f"CSV export requested: admin_id={admin.sub}")
    return await generate_csv_export(db, course_id, user_id)
```

Tests:
```python
class TestDashboard:
    async def test_dashboard_returns_all_metrics(admin_client): ...
    async def test_dashboard_filter_by_course_id(admin_client): ...
    async def test_dashboard_learner_returns_403(learner_client): ...
    async def test_dashboard_responds_within_2_seconds(admin_client): ...

class TestCsvExport:
    async def test_export_returns_csv_content_type(admin_client): ...
    async def test_export_has_correct_headers(admin_client): ...
    async def test_export_filter_by_course(admin_client): ...
    async def test_export_empty_dataset_returns_headers_only(admin_client): ...
    async def test_export_learner_returns_403(learner_client): ...

class TestAuditLogging:
    async def test_dashboard_request_logged_with_admin_id(admin_client, caplog): ...
```

## API Changes

| Endpoint                     | Method | Auth  | Description                                        |
|------------------------------|--------|-------|----------------------------------------------------|
| `/api/v1/reports/dashboard`  | GET    | Admin | Get aggregated training metrics                    |
| `/api/v1/reports/export`     | GET    | Admin | Download learner progress data as CSV              |

**Response body (dashboard):**
```json
{
  "total_learners": 10, "total_enrollments": 25,
  "overall_completion_rate": 40.0,
  "course_metrics": [...], "quiz_summaries": [...], "learner_summaries": [...]
}
```

## Data Model Changes

N/A — read-only.

## Dependencies

| Prerequisite Task | Reason                                      |
|-------------------|---------------------------------------------|
| TASK-036          | Reporting service must be implemented       |
| TASK-010          | RBAC (require_admin) required               |

**Wave:** 6

## Acceptance Criteria

- [ ] `GET /api/v1/reports/dashboard` returns 200 for Admin sessions
- [ ] `GET /api/v1/reports/dashboard` returns 403 for Learner sessions
- [ ] Dashboard response within 2 seconds (measured in test)
- [ ] CSV export response has `Content-Type: text/csv`
- [ ] Admin userId appears in log entries for reporting requests

## Test Requirements

- **Unit tests:** Router RBAC enforcement
- **Integration tests:** Dashboard with seeded data; CSV export correctness; filter params
- **Edge cases:** Dashboard with no data; CSV with special characters in user names

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-017        |
| Epic     | EPIC-006         |
| BRD      | BRD-FR-026, BRD-FR-027, BRD-FR-028, BRD-NFR-001, BRD-NFR-013, BRD-NFR-015 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
