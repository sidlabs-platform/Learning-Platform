# Story: Starter Course Seed Data

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-003            |
| **Epic**     | EPIC-001             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** Learner,
**I want** three published starter courses — GitHub Foundations, GitHub Advanced Security, and GitHub Actions — to be available in the catalog on first launch,
**so that** I can start learning immediately without waiting for admins to manually create content.

## Acceptance Criteria

1. **Given** the seed migration `002_seed_starter_courses` is run,
   **When** `GET /api/v1/courses` is called,
   **Then** exactly 3 published courses appear: GitHub Foundations, GitHub Advanced Security, GitHub Actions.

2. **Given** the GitHub Foundations course,
   **When** its modules are retrieved,
   **Then** it has exactly 5 modules (Introduction to Git and GitHub; Repositories, Branches, and Commits; Pull Requests and Code Reviews; Issues and Project Basics; Collaboration Best Practices), each with ≥ 1 lesson.

3. **Given** the seed migration is run twice,
   **When** the courses are counted,
   **Then** still only 3 courses exist (idempotent seed).

4. **Given** any of the 3 seeded courses,
   **When** its quiz questions are queried,
   **Then** at least 1 quiz question exists for the course.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                  |
|---------------|----------------------------------------------------|
| BRD-FR-041    | COMP-006 Data Layer — GitHub Foundations seed      |
| BRD-FR-042    | COMP-006 Data Layer — GitHub Advanced Security seed|
| BRD-FR-043    | COMP-006 Data Layer — GitHub Actions seed          |
| BRD-FR-044    | COMP-006 Data Layer — seed structure requirements  |

## Tasks Breakdown

| Task ID  | Description                                                   | Estimate |
|----------|---------------------------------------------------------------|----------|
| TASK-007 | Implement database seed script for 3 starter courses          | 5h       |

## UI/UX Notes

N/A — database seed only. The resulting data will be visible in the learner catalog.

## Technical Notes

- **Stack:** Python, SQLAlchemy, Alembic migration
- **Key considerations:** Seed runs inside `002_seed_starter_courses.py` Alembic migration using `run_sync()`; use `INSERT OR IGNORE` / check-before-insert for idempotency; mark all seeded courses as `status=published` and `isAiGenerated=False`
- **Configuration:** None — seed data is hardcoded content constants

## Dependencies

- STORY-002 (ORM models and initial schema migration must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
