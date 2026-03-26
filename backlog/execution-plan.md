# Execution Plan

Generated from `backlog/dependency-graph.json`
Orchestrated by: `3.5-build-orchestrator-agent`
Date: 2026-03-26

## DAG Validation

| Check | Result |
|-------|--------|
| All dependency references exist | ✅ Pass |
| No circular dependencies | ✅ Pass |
| All task types defined (backend/frontend) | ✅ Pass |
| Total tasks | 46 (37 backend, 9 frontend) |

---

## Wave 0 — Foundation (no dependencies)
**Branch:** `wave-0/foundation`

### Backend Tasks
| Task ID  | Title                                        | Files                                                              |
|----------|----------------------------------------------|--------------------------------------------------------------------|
| TASK-001 | Initialise project structure and pyproject.toml | `pyproject.toml`, `src/__init__.py`, `src/config/__init__.py`, `.env.example`, `README.md`, `.gitignore`, `tests/__init__.py`, `tests/conftest.py` |

### Frontend Tasks
_None in this wave_

---

## Wave 1 — Config & Sanitiser & Prompt Templates (depends on Wave 0)
**Branch:** `wave-1/config-sanitiser-prompts`

### Backend Tasks
| Task ID  | Title                                           | Dependencies | Files                                   |
|----------|-------------------------------------------------|--------------|-----------------------------------------|
| TASK-002 | Implement pydantic-settings configuration module | TASK-001     | `src/config/settings.py`, `src/config/__init__.py` |
| TASK-014 | Implement Markdown sanitiser (bleach wrapper)   | TASK-001     | `src/course_management/sanitiser.py`    |
| TASK-027 | Implement 5 prompt templates (PT-001–PT-005)    | TASK-001     | `src/ai_generation/__init__.py`, `src/ai_generation/prompt_templates.py` |

> Note: TASK-002, TASK-014, TASK-027 all depend only on TASK-001 and can run in parallel.

### Frontend Tasks
_None in this wave_

---

## Wave 2 — FastAPI App + DB Engine (depends on Wave 1)
**Branch:** `wave-2/app-and-db`

### Backend Tasks
| Task ID  | Title                                        | Dependencies | Files                        |
|----------|----------------------------------------------|--------------|------------------------------|
| TASK-003 | Bootstrap FastAPI application with middleware | TASK-002     | `src/main.py`                |
| TASK-004 | Implement SQLAlchemy base, engine, and session | TASK-002    | `src/database.py`            |

> Note: TASK-003 and TASK-004 both depend only on TASK-002 and can run in parallel.

### Frontend Tasks
_None in this wave_

---

## Wave 3 — ORM Models + Pydantic Models + Base Template (depends on Waves 0–2)
**Branch:** `wave-3/models-and-base-template`

### Backend Tasks
| Task ID  | Title                                        | Dependencies              | Files                                           |
|----------|----------------------------------------------|---------------------------|-------------------------------------------------|
| TASK-005 | Implement all 10 SQLAlchemy ORM models        | TASK-004                  | `src/models.py`                                 |
| TASK-008 | Implement auth Pydantic models               | TASK-003                  | `src/auth/schemas.py`, `src/auth/__init__.py`   |
| TASK-013 | Implement course management Pydantic models  | TASK-003                  | `src/course_management/schemas.py`              |
| TASK-020 | Implement progress tracking Pydantic models  | TASK-003                  | `src/progress/schemas.py`, `src/progress/__init__.py` |
| TASK-030 | Implement AI generation Pydantic models      | TASK-003                  | `src/ai_generation/schemas.py`                  |
| TASK-035 | Implement reporting Pydantic models          | TASK-003                  | `src/reporting/schemas.py`, `src/reporting/__init__.py` |

> Note: TASK-008, TASK-013, TASK-020, TASK-030, TASK-035 all depend on TASK-003; TASK-005 depends on TASK-004. All can run in parallel.

### Frontend Tasks
| Task ID  | Title                                        | Dependencies | Files                                                     |
|----------|----------------------------------------------|--------------|-----------------------------------------------------------|
| TASK-038 | Create base HTML template and CSS design system | TASK-003  | `src/templates/base.html`, `src/static/css/styles.css`    |

---

## Wave 4 — Alembic + Service Layer Foundations (depends on Waves 0–3)
**Branch:** `wave-4/alembic-and-services`

### Backend Tasks
| Task ID  | Title                                            | Dependencies                       | Files                                              |
|----------|--------------------------------------------------|------------------------------------|----------------------------------------------------|
| TASK-006 | Set up Alembic and initial schema migration      | TASK-005                           | `alembic/`, `alembic.ini`                          |
| TASK-009 | Implement auth service (password, JWT, authenticate_user) | TASK-005, TASK-008        | `src/auth/service.py`                              |
| TASK-015 | Implement course management service (course CRUD + catalog) | TASK-005, TASK-013, TASK-014 | `src/course_management/service.py`            |
| TASK-021 | Implement enrollment service                     | TASK-005, TASK-020                 | `src/progress/enrollment_service.py`               |
| TASK-028 | Implement prompt service (template rendering)    | TASK-027, TASK-030                 | `src/ai_generation/prompt_service.py`              |
| TASK-029 | Implement GitHub Models API client               | TASK-002, TASK-030                 | `src/ai_generation/github_models_client.py`        |
| TASK-036 | Implement reporting service (dashboard + CSV export) | TASK-005, TASK-035            | `src/reporting/service.py`                         |

> Note: All service layer tasks in this wave depend only on Wave 0–3 tasks. They can run in parallel.

### Frontend Tasks
_None in this wave_

---

## Wave 5 — Auth RBAC + Module/Lesson/Progress Services + Frontend Router (depends on Waves 0–4)
**Branch:** `wave-5/rbac-services-frontend-router`

### Backend Tasks
| Task ID  | Title                                          | Dependencies               | Files                              |
|----------|------------------------------------------------|----------------------------|------------------------------------|
| TASK-007 | Implement database seed script for 3 starter courses | TASK-006, TASK-013   | `src/seed.py`                      |
| TASK-010 | Implement RBAC dependency functions            | TASK-009                   | `src/auth/dependencies.py`         |
| TASK-016 | Implement module and lesson service functions  | TASK-015                   | `src/course_management/module_service.py`, `src/course_management/lesson_service.py` |
| TASK-022 | Implement progress recording service           | TASK-021, TASK-005         | `src/progress/progress_service.py` |

### Frontend Tasks
| Task ID  | Title                                | Dependencies         | Files                                |
|----------|--------------------------------------|----------------------|--------------------------------------|
| TASK-039 | Implement frontend page router       | TASK-038, TASK-009   | `src/frontend/router.py`             |

---

## Wave 6 — Auth Router + Quiz Service + Reporting Router (depends on Waves 0–5)
**Branch:** `wave-6/auth-quiz-reporting-routers`

### Backend Tasks
| Task ID  | Title                                        | Dependencies         | Files                          |
|----------|----------------------------------------------|----------------------|--------------------------------|
| TASK-011 | Implement auth router (login, logout, me)    | TASK-009, TASK-010   | `src/auth/router.py`           |
| TASK-017 | Implement quiz question service functions    | TASK-016             | `src/course_management/quiz_service.py` |
| TASK-037 | Implement reporting router and tests         | TASK-036, TASK-010   | `src/reporting/router.py`, `tests/test_reporting.py` |

### Frontend Tasks
_None in this wave_

---

## Wave 7 — Course Router + Auto-Completion + Content Persistence + Login/Reporting Templates (depends on Waves 0–6)
**Branch:** `wave-7/course-router-completion-templates`

### Backend Tasks
| Task ID  | Title                                        | Dependencies                                       | Files                                              |
|----------|----------------------------------------------|----------------------------------------------------|----------------------------------------------------|
| TASK-012 | Write auth service tests                     | TASK-011                                           | `tests/test_auth.py`                               |
| TASK-018 | Implement course management router           | TASK-015, TASK-016, TASK-017, TASK-010, TASK-011   | `src/course_management/router.py`                  |
| TASK-023 | Implement auto-completion and enrollment status machine | TASK-022, TASK-017                      | `src/progress/completion_service.py`               |
| TASK-031 | Implement content persistence layer (AI generation) | TASK-028, TASK-030, TASK-015, TASK-016, TASK-017, TASK-014 | `src/ai_generation/persistence.py`  |

### Frontend Tasks
| Task ID  | Title                                              | Dependencies              | Files                                          |
|----------|----------------------------------------------------|---------------------------|------------------------------------------------|
| TASK-040 | Create authentication login template               | TASK-038, TASK-039, TASK-011 | `src/templates/login.html`                   |
| TASK-046 | Create admin reporting dashboard template          | TASK-038, TASK-039, TASK-037 | `src/templates/admin/reporting.html`         |

---

## Wave 8 — Quiz Submission + AI Generation Router + Course Tests + Admin Course Template (depends on Waves 0–7)
**Branch:** `wave-8/quiz-ai-router-tests`

### Backend Tasks
| Task ID  | Title                                        | Dependencies                          | Files                                              |
|----------|----------------------------------------------|---------------------------------------|----------------------------------------------------|
| TASK-019 | Write course management tests                | TASK-018, TASK-007                    | `tests/test_course_management.py`                  |
| TASK-024 | Implement quiz submission service            | TASK-021, TASK-017, TASK-023          | `src/progress/quiz_service.py`                     |
| TASK-032 | Implement AI generation router (trigger + status poll) | TASK-028, TASK-029, TASK-031, TASK-010 | `src/ai_generation/router.py`            |

### Frontend Tasks
| Task ID  | Title                                              | Dependencies              | Files                                              |
|----------|----------------------------------------------------|---------------------------|----------------------------------------------------|
| TASK-044 | Create admin course management templates and course-editor.js | TASK-038, TASK-039, TASK-018 | `src/templates/admin/courses.html`, `src/static/js/course-editor.js` |

---

## Wave 9 — Progress Router + Section Regeneration (depends on Waves 0–8)
**Branch:** `wave-9/progress-router-regeneration`

### Backend Tasks
| Task ID  | Title                                        | Dependencies                                | Files                       |
|----------|----------------------------------------------|---------------------------------------------|-----------------------------|
| TASK-025 | Implement progress tracking router           | TASK-021, TASK-022, TASK-023, TASK-024, TASK-010 | `src/progress/router.py` |
| TASK-033 | Implement section regeneration router        | TASK-032, TASK-028, TASK-031               | `src/ai_generation/regeneration_router.py` |

### Frontend Tasks
_None in this wave_

---

## Wave 10 — Tests + Learner Templates + AI/Reporting Templates (depends on Waves 0–9)
**Branch:** `wave-10/tests-and-frontend-templates`

### Backend Tasks
| Task ID  | Title                              | Dependencies         | Files                            |
|----------|------------------------------------|----------------------|----------------------------------|
| TASK-026 | Write progress tracking tests      | TASK-025             | `tests/test_progress.py`         |
| TASK-034 | Write AI generation tests with mocks | TASK-032, TASK-033 | `tests/test_ai_generation.py`    |

### Frontend Tasks
| Task ID  | Title                                              | Dependencies                         | Files                                                      |
|----------|----------------------------------------------------|--------------------------------------|------------------------------------------------------------|
| TASK-041 | Create learner dashboard and catalog templates     | TASK-038, TASK-039, TASK-018, TASK-025 | `src/templates/learner/dashboard.html`, `src/templates/learner/catalog.html` |
| TASK-042 | Create course detail and lesson viewer templates + progress.js | TASK-038, TASK-039, TASK-025, TASK-018 | `src/templates/learner/course_detail.html`, `src/templates/learner/lesson.html`, `src/static/js/progress.js` |
| TASK-043 | Create quiz template and quiz.js                   | TASK-038, TASK-039, TASK-025         | `src/templates/learner/quiz.html`, `src/static/js/quiz.js` |
| TASK-045 | Create admin AI generation templates and ai-generation.js | TASK-038, TASK-039, TASK-032, TASK-034 | `src/templates/admin/ai_generation.html`, `src/static/js/ai-generation.js` |

---

## Summary

| Wave | Branch                                   | Tasks                                                          | Type           |
|------|------------------------------------------|----------------------------------------------------------------|----------------|
| 0    | wave-0/foundation                        | TASK-001                                                       | Backend        |
| 1    | wave-1/config-sanitiser-prompts          | TASK-002, TASK-014, TASK-027                                   | Backend        |
| 2    | wave-2/app-and-db                        | TASK-003, TASK-004                                             | Backend        |
| 3    | wave-3/models-and-base-template          | TASK-005, TASK-008, TASK-013, TASK-020, TASK-030, TASK-035, TASK-038 | Backend + Frontend |
| 4    | wave-4/alembic-and-services              | TASK-006, TASK-009, TASK-015, TASK-021, TASK-028, TASK-029, TASK-036 | Backend   |
| 5    | wave-5/rbac-services-frontend-router     | TASK-007, TASK-010, TASK-016, TASK-022, TASK-039              | Backend + Frontend |
| 6    | wave-6/auth-quiz-reporting-routers       | TASK-011, TASK-017, TASK-037                                   | Backend        |
| 7    | wave-7/course-router-completion-templates | TASK-012, TASK-018, TASK-023, TASK-031, TASK-040, TASK-046   | Backend + Frontend |
| 8    | wave-8/quiz-ai-router-tests              | TASK-019, TASK-024, TASK-032, TASK-044                        | Backend + Frontend |
| 9    | wave-9/progress-router-regeneration      | TASK-025, TASK-033                                             | Backend        |
| 10   | wave-10/tests-and-frontend-templates     | TASK-026, TASK-034, TASK-041, TASK-042, TASK-043, TASK-045   | Backend + Frontend |
