# Story: Quiz Submission and Scoring

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-011            |
| **Epic**     | EPIC-004             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** Learner,
**I want** to submit answers to module quiz questions and immediately see my score with pass/fail feedback,
**so that** I can gauge my understanding of the module content before moving on.

## Acceptance Criteria

1. **Given** a Learner submits answers to all questions in a module,
   **When** `POST /api/v1/enrollments/{id}/quiz-submit` is called with `{ moduleId, answers: [...] }`,
   **Then** the response includes `{ correct, total, percentage, passed }` computed server-side.

2. **Given** an answer submitted for a `QuizQuestion`,
   **When** the server evaluates correctness,
   **Then** `isCorrect` is determined by comparing `selectedAnswer` to `correctAnswer` from the DB (not trusting client input).

3. **Given** a `Module` with `isQuizInformational=true`,
   **When** a quiz is submitted regardless of score,
   **Then** `passed=true` is returned and the quiz result does not block course completion.

4. **Given** a `Module` with `quizPassingScore=80` and a learner scoring 75%,
   **When** the quiz is submitted,
   **Then** `passed=false` is returned.

5. **Given** a quiz attempt,
   **When** `QuizAttempt` records are queried,
   **Then** each attempt includes `userId`, `quizQuestionId`, `selectedAnswer`, `isCorrect`, and `attemptedAt`.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                       |
|---------------|---------------------------------------------------------|
| BRD-FR-022    | COMP-004 Progress Tracking — quiz question schema       |
| BRD-FR-023    | COMP-004 Progress Tracking — QuizAttempt recording      |
| BRD-FR-024    | COMP-004 Progress Tracking — quiz score summary         |
| BRD-FR-025    | COMP-004 Progress Tracking — quiz passing threshold     |

## Tasks Breakdown

| Task ID  | Description                                                      | Estimate |
|----------|------------------------------------------------------------------|----------|
| TASK-025 | Implement quiz submission service (submit_quiz, evaluate_quiz_score) | 4h   |
| TASK-026 | Implement progress tracking router (quiz-submit endpoint)        | 2h       |

## UI/UX Notes

Quiz UI template is covered in STORY-024 (EPIC-007).

## Technical Notes

- **Stack:** FastAPI, SQLAlchemy, Pydantic v2
- **Key considerations:** Server-side evaluation only — never trust client `isCorrect`; `evaluate_quiz_score()` fetches `QuizQuestion.correctAnswer` from DB and compares; `isQuizInformational=true` means `passed=true` regardless of score; `quizPassingScore` is 0–100 integer

## Dependencies

- STORY-009 (enrollment must exist)
- STORY-007 (quiz questions must exist)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
