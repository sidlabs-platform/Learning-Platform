# Epic: Learner Progress Tracking

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-004             |
| **Status**  | Ready                |
| **Owner**   | 4-develop-agent      |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 2             |

## Goal / Objective

Implement the complete enrollment, progress recording, quiz submission, and course completion workflow — enabling Learners to enroll in courses, track their lesson-by-lesson progress without data loss, submit quizzes, and automatically transition to a `completed` state when all requirements are satisfied.

## Business Value

Progress tracking is the mechanism that makes training measurable. It directly supports KPI-002 (end-to-end learner course completion) and KPI-003 (admin progress visibility). Without it, the platform is a static content viewer with no learning accountability.

## BRD Requirements Mapped

| BRD ID        | Description                                                                           |
|---------------|---------------------------------------------------------------------------------------|
| BRD-FR-014    | Admin enrollment: create Enrollment records with `status=not_started`                |
| BRD-FR-015    | Self-enrollment: Learner enrolls in any published course                              |
| BRD-FR-016    | Enrollment status progresses: `not_started` → `in_progress` → `completed`           |
| BRD-FR-017    | ProgressRecord persists `completed`, `completedAt`, `lastViewedAt` per lesson        |
| BRD-FR-018    | Resume last-accessed lesson via `GET /api/v1/enrollments/{id}/resume`                |
| BRD-FR-019    | `completionPercentage` (0–100) returned on enrollment retrieval                      |
| BRD-FR-020    | Auto-complete enrollment when all lessons and mandatory quizzes are done              |
| BRD-FR-021    | Progress not lost on page refresh (lastViewedAt written on lesson open)              |
| BRD-FR-022    | Multiple-choice quiz questions with 2–5 options, one correct answer, explanation     |
| BRD-FR-023    | QuizAttempt recorded: userId, quizQuestionId, selectedAnswer, isCorrect, attemptedAt |
| BRD-FR-024    | Quiz score summary: correct, total, percentage, pass/fail                            |
| BRD-FR-025    | Per-module quiz passing score threshold or informational-only flag                   |
| BRD-NFR-010   | Progress not lost on page refresh                                                     |

## Features

| Feature ID | Name                                   | Priority (P0/P1/P2) | Status  |
|------------|----------------------------------------|----------------------|---------|
| FEAT-019   | Enrollment management (admin + self)   | P0                   | Planned |
| FEAT-020   | Lesson progress recording (view + complete) | P0              | Planned |
| FEAT-021   | Resume-lesson endpoint                 | P0                   | Planned |
| FEAT-022   | Completion percentage calculation      | P0                   | Planned |
| FEAT-023   | Auto-complete enrollment               | P0                   | Planned |
| FEAT-024   | Quiz attempt recording and scoring     | P0                   | Planned |

## Acceptance Criteria

1. `POST /api/v1/enrollments` (Admin) creates an enrollment with `status=not_started`; duplicate returns `409`.
2. `POST /api/v1/enrollments` (Learner self-enrollment) works for published courses; returns `404` for unpublished.
3. On first lesson view, `ProgressRecord.lastViewedAt` is written and enrollment status becomes `in_progress`.
4. `GET /api/v1/enrollments/{id}/resume` returns the lessonId of the last-accessed lesson.
5. `GET /api/v1/enrollments/{id}` includes `completionPercentage` as an integer 0–100.
6. After all lessons and mandatory quizzes complete, enrollment status transitions to `completed` and `completedAt` is set.
7. Quiz submission returns `{ correct, total, percentage, passed }` with server-side evaluation.
8. Refreshing the lesson page does not reset progress.

## Dependencies & Risks

**Dependencies:**
- EPIC-001 (ORM models, `enrollments`, `progress_records`, `quiz_attempts` tables)
- EPIC-002 (RBAC dependencies)
- EPIC-003 (courses, modules, lessons, quiz_questions data must exist)

**Risks:**
- Concurrent lesson completion writes to SQLite — acceptable for MVP scale (≤ 50 learners)
- Auto-completion logic edge cases when `isQuizInformational=true` — must be tested explicitly

## Out of Scope

- Admin reporting aggregations (EPIC-006)
- Frontend UI (EPIC-007)

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
