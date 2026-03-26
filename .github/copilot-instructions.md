# Copilot Instructions — Agentic SDLC Learning Platform

## Project Overview

A minimum viable learning platform where **Learners** enroll in and complete courses,
**Admins** create and manage courses (with AI-assisted content generation via GitHub Models),
and progress is tracked at lesson/module/course level.

The MVP ships with three starter courses: **GitHub Foundations**, **GitHub Advanced Security**,
and **GitHub Actions**. The SDLC is driven by 7 custom Copilot agents that chain together
to produce requirements → design → backlog → implementation → UI → tests → security review.

### Requirements Source

The authoritative product requirements live in `learning-platform-mvp-requirements.md` at the
repo root. All agents and contributors **must** read this document for scope, user journeys,
functional requirements, data entities, and acceptance criteria.

## Users & Roles

| Role       | Description                                                      |
|------------|------------------------------------------------------------------|
| **Learner** | Consumes courses, completes lessons/quizzes, tracks own progress |
| **Admin**   | Creates/edits/publishes courses, enrolls learners, views reports, triggers AI generation |

Role-based access control is required. Admins can perform all learner actions plus authoring,
publishing, enrollment, and reporting. Learners can only access their own data.

## Domain Model (Core Entities)

- **User** — id, name, email, role
- **Course** — id, title, description, status (draft/published), difficulty, estimatedDuration, tags
- **Module** — id, courseId, title, summary, sortOrder
- **Lesson** — id, moduleId, title, markdownContent, estimatedMinutes, sortOrder
- **QuizQuestion** — id, moduleId, question, options[], correctAnswer, explanation
- **Enrollment** — userId, courseId, enrolledAt, status (not_started/in_progress/completed)
- **ProgressRecord** — userId, lessonId, moduleId, completed, completedAt, lastViewedAt
- **QuizAttempt** — userId, quizQuestionId, selectedAnswer, isCorrect, attemptedAt
- **ContentGenerationRequest** — prompt, model, requesterId, status, createdAt
- **ContentGenerationArtifact** — generatedContent, sourceRequestId, approvedBy, approvedAt

## Course Structure

`Course → Module[] → Lesson[] + QuizQuestion[]`

Each starter course should have 3–5 modules, 1–3 lessons per module, and at least one quiz per course.
Lesson content is Markdown. AI-generated content starts as **draft** and requires admin review before publishing.

## Tech Stack & Conventions

- **Language**: Python 3.11+
- **Backend Framework**: FastAPI
- **Data Models**: Pydantic v2
- **Database**: SQLite (zero-config, file-based for MVP)
- **Frontend**: Vanilla HTML/CSS/JS with Jinja2 templates (no frameworks)
- **Testing**: pytest + httpx AsyncClient + respx/unittest.mock for external API mocks
- **AI Backend**: GitHub Models API (GPT-4o)
- **Project Structure**:
  - `src/` — application source code (backend + frontend static/templates)
  - `tests/` — test suite
  - `docs/` — SDLC artifacts (requirements/, design/, testing/)
  - `templates/` — SDLC document templates
  - `backlog/` — work items (epics/, stories/, tasks/)

## API / Service Boundaries

The backend should be organized into these service modules:

| Service               | Responsibility                                             |
|-----------------------|------------------------------------------------------------|
| Auth                  | Sign-in, role-based access control                         |
| Course Management     | CRUD courses/modules/lessons, publish/unpublish, catalog   |
| AI Generation         | GitHub Models integration, prompt management, draft content|
| Progress Tracking     | Enrollment, lesson/module/course progress, quiz scoring    |
| Reporting             | Admin dashboard data, enrollment/completion stats, export  |

REST endpoints live under `/api/v1/`. Frontend page routes return Jinja2 templates at root paths.

## Content Governance

1. Admin provides topic, audience, objectives, difficulty → system calls GitHub Models.
2. Generated content is saved as **draft** with metadata (prompt, model, timestamp).
3. Admin reviews, edits, and **publishes** — only then is content visible to learners.
4. Content labeled as AI-generated until explicitly approved.
5. Admins can regenerate individual sections without regenerating the whole course.

## Coding Standards

- Use type hints on all function signatures and variables where non-obvious.
- Define request/response schemas as Pydantic models (never raw dicts).
- Use `async def` for I/O-bound endpoints; sync is fine for pure computation.
- Raise `fastapi.HTTPException` with appropriate status codes for error handling.
- Load configuration from environment variables via `pydantic-settings` — never hardcode secrets.
- Add docstrings to all public functions and classes.
- Keep functions small and single-purpose.
- Sanitize all rendered lesson content to prevent XSS.

## Agent Workflow Rules

- SDLC document templates live in `templates/` — always start from a template.
- Generated artifacts go under `docs/`:
  - `docs/requirements/` — BRD, functional specs
  - `docs/design/` — architecture, API design, data models
  - `docs/testing/` — test plans, test cases, security review
- Backlog items go under `backlog/`:
  - `backlog/epics/` — high-level features
  - `backlog/stories/` — user stories
  - `backlog/tasks/` — implementation tasks
- Every artifact **must** trace back to a BRD requirement ID (`BRD-xxx`).
- Update `docs/change-log.md` when making key decisions or significant changes.
- Agents must read `learning-platform-mvp-requirements.md` to understand full scope.

## GitHub Models Integration

- **Auth**: Use environment variable `GITHUB_MODELS_API_KEY`.
- **Endpoint**: Configured via environment variable `GITHUB_MODELS_ENDPOINT`.
- **Preferred model**: GPT-4o for content generation tasks.
- Always handle rate limits with exponential backoff.
- Wrap API calls in try/except and return meaningful error responses.
- Never log or expose API keys in output or error messages.
- Store generated content as drafts with generation metadata for audit.
- Design the generation service as a pluggable module (MCP-ready for future).

## Non-Functional Requirements

- **Usability**: Learner reaches next lesson within 2 clicks from dashboard. Responsive for desktop and tablet.
- **Performance**: Non-AI API calls < 2s. AI generation may be async if long-running.
- **Security**: RBAC enforced on all endpoints. Secrets in env vars only. XSS prevention on rendered content. CORS scoped appropriately.
- **Reliability**: Progress never lost on page refresh. AI failures return retryable error states. Published courses available even if AI services are down.
- **Observability**: Log auth events, publishing actions, AI generation calls. Capture generation errors and latency.

## Do / Avoid

### Do

- Use templates from `templates/` for all SDLC documents.
- Read `learning-platform-mvp-requirements.md` for authoritative scope and acceptance criteria.
- Maintain requirement ID traceability (`BRD-xxx`) across all artifacts.
- Write tests for every new endpoint and service function.
- Keep dependencies minimal and justified.
- Implement draft → review → publish workflow for AI-generated content.

### Avoid

- Hardcoding API keys, secrets, or environment-specific values.
- Adding complexity beyond MVP scope — keep it simple.
- Introducing frameworks or libraries not needed for the MVP.
- Committing generated credentials or `.env` files.
- Skipping error handling on external API calls.
- Auto-publishing AI-generated content without admin review.
