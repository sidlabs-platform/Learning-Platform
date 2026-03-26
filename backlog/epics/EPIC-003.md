# Epic: Course Management

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-003             |
| **Status**  | Ready                |
| **Owner**   | 4-develop-agent      |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 2             |

## Goal / Objective

Deliver the full CRUD API for the course content hierarchy (Course → Module → Lesson → QuizQuestion), publish/unpublish workflow, learner-facing catalog with filtering, and server-side Markdown sanitisation — enabling Admins to author and publish courses and Learners to discover published content.

## Business Value

Course Management is the central capability of the platform. Without it, there is no content to learn, no catalog to browse, and no structure for progress tracking to operate against. It directly enables the core learner journey and the admin content governance workflow.

## BRD Requirements Mapped

| BRD ID        | Description                                                                         |
|---------------|-------------------------------------------------------------------------------------|
| BRD-FR-005    | Published course catalog with title, description, difficulty, duration, tags        |
| BRD-FR-006    | Filter catalog by topic (tag) and difficulty                                        |
| BRD-FR-007    | Admin publish course (draft → published)                                            |
| BRD-FR-008    | Admin unpublish course (published → draft)                                          |
| BRD-FR-009    | Four-level hierarchy: Course → Module → Lesson → QuizQuestion                      |
| BRD-FR-010    | Course record fields: title, description, status, difficulty, duration, audience, objectives, tags |
| BRD-FR-011    | Lesson supports Markdown content with XSS-safe rendering                            |
| BRD-FR-012    | Module includes QuizQuestions (question, options[], correctAnswer, explanation)     |
| BRD-FR-013    | Modules and Lessons ordered by `sortOrder`                                          |
| BRD-FR-037    | Server-side Markdown sanitisation (XSS prevention)                                 |
| BRD-FR-038    | Draft/published course states; editing a published course creates a new draft       |
| BRD-FR-039    | AI-generated sections flagged with `isAiGenerated` boolean                          |
| BRD-NFR-001   | Non-AI endpoints respond in < 2 seconds                                             |
| BRD-NFR-006   | Markdown sanitised via bleach before storage and at render                          |

## Features

| Feature ID | Name                              | Priority (P0/P1/P2) | Status  |
|------------|-----------------------------------|----------------------|---------|
| FEAT-012   | Course CRUD (create, read, update, delete) | P0           | Planned |
| FEAT-013   | Module CRUD                       | P0                   | Planned |
| FEAT-014   | Lesson CRUD with Markdown support | P0                   | Planned |
| FEAT-015   | QuizQuestion CRUD                 | P0                   | Planned |
| FEAT-016   | Course catalog with filtering     | P0                   | Planned |
| FEAT-017   | Publish / Unpublish workflow      | P0                   | Planned |
| FEAT-018   | Markdown sanitiser (bleach)       | P0                   | Planned |

## Acceptance Criteria

1. `GET /api/v1/courses` returns only `published` courses; draft courses are excluded for Learner sessions.
2. `GET /api/v1/courses?difficulty=beginner&tag=github-actions` correctly filters results.
3. `POST /api/v1/courses` (Admin) creates a course with `status=draft`; missing required fields return `422`.
4. `PATCH /api/v1/courses/{id}/publish` transitions status to `published` and records `publishedAt`.
5. `PATCH /api/v1/courses/{id}/unpublish` transitions to `draft`; learner catalog no longer shows the course; existing progress records are preserved.
6. Lesson content with `<script>alert(1)</script>` is stripped by `sanitise_markdown()` before storage.
7. Course detail endpoint returns full nested structure: modules → lessons → quiz_questions, ordered by `sortOrder`.

## Dependencies & Risks

**Dependencies:**
- EPIC-001 (ORM models, database schema)
- EPIC-002 (RBAC dependencies for admin-only routes)

**Risks:**
- JSON TypeDecorator for `learning_objectives` and `tags` must be tested carefully for round-trip fidelity
- Cascade delete behaviour on Course deletion must be verified to avoid orphaned Progress Records

## Out of Scope

- AI-generated course creation (EPIC-005)
- Enrollment logic (EPIC-004)
- Frontend UI (EPIC-007)

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
