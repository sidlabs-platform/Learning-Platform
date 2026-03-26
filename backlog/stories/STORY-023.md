# Story: Quiz UI Page

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-023            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As a** Learner,
**I want** a quiz page for each module that shows multiple-choice questions, submits my answers, and displays my score with pass/fail feedback,
**so that** I can test my understanding and know whether I need to review the material before moving on.

## Acceptance Criteria

1. **Given** a Learner visits `/courses/{id}/modules/{mid}/quiz`,
   **When** the page loads,
   **Then** all quiz questions for the module are displayed as radio-button multiple-choice forms.

2. **Given** a Learner selects answers and clicks "Submit Quiz",
   **When** the form is submitted,
   **Then** `POST /api/v1/enrollments/{id}/quiz-submit` is called and a score summary is displayed without a full page reload.

3. **Given** the score summary is displayed,
   **When** the Learner reads it,
   **Then** it shows: number correct, total questions, percentage, and a pass/fail badge.

4. **Given** a `isQuizInformational=true` module,
   **When** the score is displayed,
   **Then** "Informational — no pass/fail requirement" is shown instead of a pass/fail badge.

5. **Given** the quiz is submitted,
   **When** the results are shown,
   **Then** each question reveals the correct answer and the Learner's selected answer (with green/red highlighting).

## BRD & Design References

| BRD ID        | HLD/LLD Component                                       |
|---------------|---------------------------------------------------------|
| BRD-FR-022    | COMP-004 Progress Tracking — MCQ quiz format            |
| BRD-FR-024    | COMP-004 Progress Tracking — score summary response     |
| BRD-FR-025    | COMP-004 Progress Tracking — informational quiz flag    |

## Tasks Breakdown

| Task ID  | Description                                              | Estimate |
|----------|----------------------------------------------------------|----------|
| TASK-044 | Create quiz.html template                                | 3h       |
| TASK-049 | Implement quiz.js (submitQuiz, showResults functions)    | 3h       |

## UI/UX Notes

- One question per page or all questions scrollable — all scrollable for MVP simplicity
- Radio buttons for each option; disabled after submission
- Score card shows: large percentage number, correct/total text, green "PASSED" or red "FAILED" badge
- Answer reveal section below score card: each question with color-coded options (green = correct, red = wrong selection)

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch, CSS
- **Key considerations:** `quiz.js` collects `{questionId, selectedAnswer}` pairs from radio inputs; posts to quiz-submit endpoint; renders results by DOM manipulation; `isQuizInformational` passed from server into template context for conditional display

## Dependencies

- STORY-019 (base template)
- STORY-011 (quiz submission API)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
