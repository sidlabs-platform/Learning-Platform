# Test Plan — AI-Powered Learning Platform

| Field         | Value                                        |
|---------------|----------------------------------------------|
| **Version**   | 1.0                                          |
| **Date**      | 2026-03-26                                   |
| **Author**    | 6-automation-test-agent                      |
| **BRD Ref**   | BRD-FR-001–BRD-FR-044, BRD-INT-001–BRD-INT-010 |
| **Status**    | Active                                       |

---

## 1. Test Scope & Objectives

### 1.1 Scope

This test plan covers the MVP of the AI-powered Learning Platform built with Python 3.11+, FastAPI, SQLite, and GitHub Models API integration.

**In scope:**
- Authentication & authorisation (register, login, logout, JWT, RBAC)
- Course Management API (CRUD, publish/unpublish, catalog)
- Module & Lesson API (CRUD, XSS sanitisation)
- Quiz Question API (creation and learner access)
- Learner Progress Tracking (enrollment, lesson view/complete, quiz submission)
- AI Content Generation (request creation, status polling, GitHub Models mock)
- Admin Reporting (dashboard, CSV export)
- Pydantic v2 schema validation
- XSS sanitisation and log injection prevention

**Out of scope:**
- Frontend Jinja2 template rendering (visual regression)
- Load/performance testing
- End-to-end browser testing
- Alembic migration correctness

### 1.2 Objectives

- Verify all 44 Functional Requirements (BRD-FR-001 – BRD-FR-044) have test coverage
- Confirm GitHub Models API integration is properly mocked and exercised
- Validate RBAC: admin-only endpoints reject learner tokens with 403
- Ensure XSS prevention is enforced at write-time via `sanitise_markdown`
- Achieve ≥ 80% line coverage on `src/` service and router modules
- All 222 test cases pass on every CI run

---

## 2. Test Strategy

### 2.1 Unit Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | Service functions, schema validators, sanitiser, JWT helpers  |
| **Framework**   | pytest 8/9 + pytest-asyncio (asyncio_mode=auto)               |
| **Approach**    | Direct function calls with in-memory SQLite, all external APIs mocked |
| **Coverage**    | Target 80%+ line coverage on `src/` modules                   |

### 2.2 Integration / API Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | All REST endpoints end-to-end from HTTP request to DB         |
| **Framework**   | pytest + httpx AsyncClient + ASGITransport                    |
| **Approach**    | Full app stack with in-memory DB; GitHub Models calls mocked via `unittest.mock` |

### 2.3 External Service Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | `generate_content`, `generate_with_retry`, `_execute_request` |
| **Framework**   | pytest + unittest.mock                                        |
| **Approach**    | Patch `httpx.AsyncClient` to return controlled mock responses  |

---

## 3. Test Environment

### 3.1 Local / CI Setup

| Component               | Detail                                          |
|-------------------------|-------------------------------------------------|
| **Python version**      | 3.11+                                           |
| **Database**            | SQLite in-memory (`sqlite+aiosqlite:///:memory:`) |
| **External APIs**       | GitHub Models API — fully mocked (unittest.mock) |
| **Test runner**         | `pytest tests/ -v`                              |

### 3.2 Required Dependencies

```
pytest==8.3.4+
pytest-asyncio==0.24.0+
httpx==0.28.1
respx==0.21.1
aiosqlite==0.20.0
```

### 3.3 Environment Variables (Test Values)

| Variable                    | Test Value                                    |
|-----------------------------|-----------------------------------------------|
| `SECRET_KEY`                | `test-secret-key-at-least-32-characters-long!` |
| `GITHUB_MODELS_API_KEY`     | `test-api-key`                                |
| `GITHUB_MODELS_ENDPOINT`    | `https://models.inference.ai.azure.com`       |
| `DATABASE_URL`              | `sqlite+aiosqlite:///:memory:`                |

---

## 4. Test Cases

| TC ID   | File                              | Test Name                                                           | Type        | BRD/Task Ref    | Status  |
|---------|-----------------------------------|---------------------------------------------------------------------|-------------|-----------------|---------|
| TC-001  | test_api/test_auth.py             | test_register_returns_201_with_user_data                           | API         | BRD-FR-001      | Passed  |
| TC-002  | test_api/test_auth.py             | test_register_admin_role_succeeds                                   | API         | BRD-FR-002      | Passed  |
| TC-003  | test_api/test_auth.py             | test_register_duplicate_email_returns_409                          | API         | BRD-FR-001      | Passed  |
| TC-004  | test_api/test_auth.py             | test_register_missing_email_returns_422                            | API         | BRD-FR-001      | Passed  |
| TC-005  | test_api/test_auth.py             | test_register_invalid_email_format_returns_422                     | API         | BRD-FR-001      | Passed  |
| TC-006  | test_api/test_auth.py             | test_register_invalid_role_returns_422                             | API         | BRD-FR-002      | Passed  |
| TC-007  | test_api/test_auth.py             | test_login_with_valid_credentials_returns_token                    | API         | BRD-FR-001      | Passed  |
| TC-008  | test_api/test_auth.py             | test_login_sets_httponly_cookie                                     | API         | BRD-FR-001      | Passed  |
| TC-009  | test_api/test_auth.py             | test_login_wrong_password_returns_401                              | API         | BRD-FR-001      | Passed  |
| TC-010  | test_api/test_auth.py             | test_login_unknown_email_returns_401                               | API         | BRD-FR-001      | Passed  |
| TC-011  | test_api/test_auth.py             | test_logout_clears_cookie_and_returns_200                          | API         | BRD-FR-001      | Passed  |
| TC-012  | test_api/test_auth.py             | test_get_me_returns_current_user_profile                           | API         | BRD-FR-001      | Passed  |
| TC-013  | test_api/test_auth.py             | test_get_me_without_token_returns_401                              | API         | BRD-FR-003      | Passed  |
| TC-014  | test_api/test_auth.py             | test_change_password_with_correct_current_password_returns_200     | API         | BRD-FR-001      | Passed  |
| TC-015  | test_api/test_courses.py          | test_admin_create_course_returns_201                               | API         | BRD-FR-003,010  | Passed  |
| TC-016  | test_api/test_courses.py          | test_learner_cannot_create_course_returns_403                      | API         | BRD-FR-003      | Passed  |
| TC-017  | test_api/test_courses.py          | test_admin_list_courses_sees_draft_and_published                   | API         | BRD-FR-005      | Passed  |
| TC-018  | test_api/test_courses.py          | test_learner_list_courses_sees_only_published                      | API         | BRD-FR-005      | Passed  |
| TC-019  | test_api/test_courses.py          | test_admin_publish_course_changes_status_to_published              | API         | BRD-FR-007      | Passed  |
| TC-020  | test_api/test_courses.py          | test_learner_cannot_publish_course_returns_403                     | API         | BRD-FR-003,007  | Passed  |
| TC-021  | test_api/test_courses.py          | test_publish_already_published_course_returns_409                  | API         | BRD-FR-007      | Passed  |
| TC-022  | test_api/test_courses.py          | test_admin_unpublish_course_changes_status_to_draft                | API         | BRD-FR-008      | Passed  |
| TC-023  | test_api/test_courses.py          | test_unpublished_course_not_visible_to_learner                     | API         | BRD-FR-008      | Passed  |
| TC-024  | test_api/test_modules.py          | test_admin_create_module_returns_201                               | API         | BRD-FR-009      | Passed  |
| TC-025  | test_api/test_modules.py          | test_list_modules_returns_sorted_by_sort_order                     | API         | BRD-FR-013      | Passed  |
| TC-026  | test_api/test_lessons.py          | test_admin_create_lesson_returns_201                               | API         | BRD-FR-011      | Passed  |
| TC-027  | test_api/test_lessons.py          | test_create_lesson_xss_content_is_sanitised                        | API         | BRD-FR-011      | Passed  |
| TC-028  | test_api/test_progress.py         | test_learner_enroll_in_published_course_returns_201                | API         | BRD-FR-015      | Passed  |
| TC-029  | test_api/test_progress.py         | test_learner_duplicate_enrollment_returns_400                      | API         | BRD-FR-015      | Passed  |
| TC-030  | test_api/test_progress.py         | test_list_enrollments_does_not_return_others_enrollments           | API         | BRD-FR-004      | Passed  |
| TC-031  | test_api/test_progress.py         | test_record_lesson_view_returns_progress_record                    | API         | BRD-FR-017      | Passed  |
| TC-032  | test_api/test_progress.py         | test_complete_lesson_sets_completed_flag                           | API         | BRD-FR-017      | Passed  |
| TC-033  | test_api/test_progress.py         | test_complete_lesson_is_idempotent                                 | API         | BRD-FR-017      | Passed  |
| TC-034  | test_api/test_progress.py         | test_get_course_progress_returns_summary                           | API         | BRD-FR-019      | Passed  |
| TC-035  | test_api/test_progress.py         | test_submit_correct_quiz_answer_returns_is_correct_true            | API         | BRD-FR-020      | Passed  |
| TC-036  | test_api/test_progress.py         | test_submit_wrong_quiz_answer_returns_is_correct_false             | API         | BRD-FR-020      | Passed  |
| TC-037  | test_api/test_progress.py         | test_multiple_quiz_attempts_are_stored_independently               | API         | BRD-FR-020      | Passed  |
| TC-038  | test_api/test_ai_generation.py    | test_admin_trigger_generation_returns_202                          | API         | BRD-FR-029      | Passed  |
| TC-039  | test_api/test_ai_generation.py    | test_get_generation_status_returns_status_object                   | API         | BRD-FR-030      | Passed  |
| TC-040  | test_api/test_ai_generation.py    | test_regenerate_section_returns_501                                | API         | TASK-018        | Passed  |
| TC-041  | test_api/test_reporting.py        | test_admin_get_dashboard_returns_200                               | API         | BRD-FR-025      | Passed  |
| TC-042  | test_api/test_reporting.py        | test_learner_cannot_access_dashboard_returns_403                   | API         | BRD-FR-003      | Passed  |
| TC-043  | test_api/test_reporting.py        | test_admin_export_enrollments_csv_returns_csv                      | API         | BRD-FR-026      | Passed  |
| TC-044  | test_api/test_reporting.py        | test_admin_export_learner_progress_csv_returns_csv                 | API         | BRD-FR-027      | Passed  |
| TC-045  | test_services/test_auth_service.py| test_hash_password_returns_non_plaintext                           | Unit        | BRD-FR-001      | Passed  |
| TC-046  | test_services/test_auth_service.py| test_create_and_decode_access_token_round_trip                     | Unit        | BRD-FR-001      | Passed  |
| TC-047  | test_services/test_auth_service.py| test_authenticate_inactive_user_returns_none                       | Unit        | BRD-FR-001      | Passed  |
| TC-048  | test_services/test_course_service.py| test_create_course_sets_draft_status                             | Unit        | BRD-FR-007      | Passed  |
| TC-049  | test_services/test_course_service.py| test_publish_course_changes_status_to_published                  | Unit        | BRD-FR-007      | Passed  |
| TC-050  | test_services/test_course_service.py| test_create_lesson_sanitises_xss_content                         | Unit        | BRD-FR-011      | Passed  |
| TC-051  | test_services/test_progress_service.py| test_enroll_user_duplicate_raises_400                          | Unit        | BRD-FR-014      | Passed  |
| TC-052  | test_services/test_progress_service.py| test_complete_lesson_second_call_preserves_completed_at        | Unit        | BRD-FR-017      | Passed  |
| TC-053  | test_services/test_ai_service.py  | test_create_generation_request_creates_pending_record              | Unit        | BRD-FR-029      | Passed  |
| TC-054  | test_services/test_ai_service.py  | test_generate_with_retry_succeeds_after_retry                      | Unit        | BRD-INT-007     | Passed  |
| TC-055  | test_models/test_schemas.py       | test_correct_answer_not_in_options_raises_error                    | Unit        | BRD-FR-012      | Passed  |
| TC-056  | test_models/test_schemas.py       | test_only_two_roles_exist                                          | Unit        | BRD-FR-002      | Passed  |
| TC-057  | test_models/test_sanitization.py  | test_script_tag_and_content_is_stripped                            | Unit        | BRD-NFR-005     | Passed  |
| TC-058  | test_models/test_sanitization.py  | test_javascript_href_is_stripped                                   | Unit        | BRD-NFR-005     | Passed  |
| TC-059  | test_models/test_sanitization.py  | test_removes_newlines (sanitize_log)                               | Unit        | BRD-NFR-005     | Passed  |

*(Full list: 222 test cases across 8 test files — see `tests/` for the complete set.)*

---

## 5. Test Data Requirements

| Data Category          | Description                                               | Source           |
|------------------------|-----------------------------------------------------------|------------------|
| Admin user             | Admin with known credentials and JWT token                | `conftest.py` fixtures |
| Learner user           | Learner with known credentials and JWT token              | `conftest.py` fixtures |
| Draft course           | Course with `status=draft`                                | `conftest.py` fixtures |
| Published course       | Course with `status=published`                            | `conftest.py` fixtures |
| Module + Lesson        | Module with a lesson under a draft course                 | `conftest.py` fixtures |
| Quiz question          | Quiz question with correct/wrong answer options           | `conftest.py` fixtures |
| Enrollment             | Learner enrolled in published course                      | `conftest.py` fixtures |
| AI generation mocks    | Mocked GitHub Models responses via `unittest.mock`        | In-test patches  |

---

## 6. Entry / Exit Criteria

### 6.1 Entry Criteria

- [x] Application builds and starts without errors
- [x] In-memory SQLite DB initialised with all ORM models
- [x] All external API calls mocked (GitHub Models)
- [x] Test fixtures provide admin and learner users with valid JWT tokens

### 6.2 Exit Criteria

- [x] All 222 test cases pass (`pytest tests/ -v`)
- [x] No test raises an unhandled exception or DB error
- [x] Coverage target ≥ 80% on `src/` service/router modules
- [x] No critical or high-severity defects remain open

---

## 7. Defect Management

### 7.1 Severity Levels

| Severity | Definition                                                     |
|----------|----------------------------------------------------------------|
| **S1**   | System crash, data loss, security bypass                       |
| **S2**   | Major feature broken (auth, enrollment, course CRUD)           |
| **S3**   | Partial feature impaired, workaround exists                    |
| **S4**   | Minor, cosmetic, or non-critical edge case                     |

---

## 8. Tools & Frameworks

| Tool / Framework    | Purpose                                            |
|---------------------|----------------------------------------------------|
| **pytest**          | Test runner (asyncio_mode=auto)                    |
| **pytest-asyncio**  | Async test support for FastAPI                     |
| **httpx AsyncClient** | ASGI transport for API endpoint testing          |
| **unittest.mock**   | Mock GitHub Models API calls                       |
| **respx**           | Available for httpx-level HTTP mocking if needed   |
| **aiosqlite**       | In-memory async SQLite for test isolation          |
| **SQLAlchemy async** | DB session override via FastAPI dependency_overrides |

---

## 9. Traceability Matrix

| BRD Requirement                               | Test File(s)                              | Test Count |
|-----------------------------------------------|-------------------------------------------|------------|
| BRD-FR-001: Sign-in with email/password        | test_auth.py, test_auth_service.py        | 18         |
| BRD-FR-002: Two roles (learner/admin)          | test_auth.py, test_schemas.py             | 8          |
| BRD-FR-003: Admin-only endpoint enforcement    | test_courses.py, test_modules.py, etc.    | 22         |
| BRD-FR-004: Learner sees own data only         | test_progress.py, test_progress_service.py| 4          |
| BRD-FR-005: Published course catalog           | test_courses.py, test_course_service.py   | 6          |
| BRD-FR-007: Publish course                     | test_courses.py, test_course_service.py   | 5          |
| BRD-FR-008: Unpublish course                   | test_courses.py, test_course_service.py   | 3          |
| BRD-FR-009: Course structure hierarchy         | test_courses.py, test_modules.py          | 6          |
| BRD-FR-010: Course required fields             | test_courses.py, test_schemas.py          | 5          |
| BRD-FR-011: Lesson markdown + sanitisation     | test_lessons.py, test_course_service.py   | 8          |
| BRD-FR-012: Quiz question options/answer       | test_schemas.py                           | 3          |
| BRD-FR-013: Module/lesson sort order           | test_modules.py                           | 2          |
| BRD-FR-014: Enrollment creation                | test_progress.py, test_progress_service.py| 5          |
| BRD-FR-015: Self-enrollment                    | test_progress.py                          | 3          |
| BRD-FR-016: Enrollment status transitions      | test_progress_service.py                  | 4          |
| BRD-FR-017: Progress records                   | test_progress.py, test_progress_service.py| 12         |
| BRD-FR-019: Course completion percentage       | test_progress.py                          | 2          |
| BRD-FR-020: Quiz submission/scoring            | test_progress.py                          | 5          |
| BRD-FR-025: Admin dashboard                    | test_reporting.py                         | 5          |
| BRD-FR-026: CSV enrollments export             | test_reporting.py                         | 3          |
| BRD-FR-027: CSV learner progress export        | test_reporting.py                         | 1          |
| BRD-FR-029: AI generation request              | test_ai_generation.py, test_ai_service.py | 7          |
| BRD-FR-030: Generation status polling          | test_ai_generation.py, test_ai_service.py | 4          |
| BRD-NFR-005: XSS prevention                   | test_sanitization.py, test_lessons.py     | 14         |
| BRD-INT-001–010: GitHub Models integration     | test_ai_service.py                        | 4          |

---

## 10. Risks & Assumptions

### 10.1 Risks

| Risk                                                   | Impact | Mitigation                                      |
|--------------------------------------------------------|--------|-------------------------------------------------|
| `asyncio.create_task` scheduling real background tasks | Medium | Patch `process_generation` with AsyncMock       |
| In-memory DB state leaking between tests               | High   | Per-test table truncation via `_clean_db` fixture |
| GitHub Models API key missing in CI                    | Low    | Environment defaults set in conftest.py          |

### 10.2 Assumptions

- All tests use in-memory SQLite; production uses file-based SQLite
- GitHub Models API is never called in tests (fully mocked)
- JWT tokens are valid for the duration of a test run
- `pytest-asyncio` `asyncio_mode=auto` is configured in `pyproject.toml`
