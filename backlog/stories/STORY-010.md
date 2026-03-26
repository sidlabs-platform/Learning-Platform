# Story: Lesson Progress Recording and Course Resume

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-010            |
| **Epic**     | EPIC-004             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** Learner,
**I want** my lesson progress to be automatically saved when I open a lesson, and to be able to mark it complete when I finish reading,
**so that** I never lose my place and can resume exactly where I left off after a page refresh or return visit.

## Acceptance Criteria

1. **Given** an enrolled Learner opens a lesson,
   **When** `POST /api/v1/progress` is called with `{ lessonId, completed: false }`,
   **Then** a `ProgressRecord` is created or updated with `lastViewedAt=now()` and the enrollment status transitions to `in_progress` if it was `not_started`.

2. **Given** a Learner marks a lesson complete,
   **When** `POST /api/v1/progress` with `{ lessonId, completed: true }` is called,
   **Then** `ProgressRecord.completed=true` and `completedAt=now()` are set.

3. **Given** a Learner refreshes the lesson page,
   **When** `GET /api/v1/enrollments/{id}` is called,
   **Then** the `completionPercentage` is unchanged from before the refresh.

4. **Given** a Learner who has partially completed a course,
   **When** `GET /api/v1/enrollments/{id}/resume` is called,
   **Then** the response contains the `lessonId` of the most recently viewed lesson.

5. **Given** all lessons in a course are completed (and all mandatory quizzes passed),
   **When** the final lesson is marked complete,
   **Then** the enrollment `status` transitions to `completed` and `completedAt` is set.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                          |
|---------------|------------------------------------------------------------|
| BRD-FR-017    | COMP-004 Progress Tracking — ProgressRecord persistence    |
| BRD-FR-018    | COMP-004 Progress Tracking — resume last-accessed lesson   |
| BRD-FR-019    | COMP-004 Progress Tracking — completionPercentage          |
| BRD-FR-020    | COMP-004 Progress Tracking — auto-complete enrollment      |
| BRD-FR-021    | COMP-004 Progress Tracking — progress survives page refresh|
| BRD-NFR-010   | COMP-004 Progress Tracking — reliability on refresh        |

## Tasks Breakdown

| Task ID  | Description                                                        | Estimate |
|----------|--------------------------------------------------------------------|----------|
| TASK-023 | Implement progress recording service (record_lesson_view, mark_lesson_complete) | 4h |
| TASK-024 | Implement completion calculation and auto-complete enrollment       | 3h       |
| TASK-026 | Implement progress tracking router (progress endpoints)            | 2h       |

## UI/UX Notes

The lesson viewer calls `recordLessonView()` on page load and `markLessonComplete()` on button click (STORY-024, EPIC-007).

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy async upsert (INSERT OR REPLACE), Pydantic v2
- **Key considerations:** `record_lesson_view()` uses upsert pattern — idempotent even on rapid re-opens; `calculate_completion_percentage()` counts completed `ProgressRecord` rows vs total lesson count for the course; `auto_complete_enrollment()` checks `isQuizInformational` flag before requiring quiz pass

## Dependencies

- STORY-009 (enrollment must exist before recording progress)
- STORY-007 (lesson and quiz question data must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
