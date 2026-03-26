# Story: Admin AI Generation Form and Status Polling UI

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-025            |
| **Epic**     | EPIC-007             |
| **Status**   | Ready                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin,
**I want** an AI generation form where I enter course parameters and trigger generation, see a live progress indicator while generation runs, and be notified when the draft is ready or if an error occurred,
**so that** I can use AI-assisted authoring without confusion about whether generation succeeded.

## Acceptance Criteria

1. **Given** `/admin/ai/generate` is loaded,
   **When** the page renders,
   **Then** form fields for topic, targetAudience, learningObjectives, difficulty, desiredModuleCount, and preferredTone are displayed.

2. **Given** the form is submitted,
   **When** `POST /api/v1/ai/generate-course` returns `202`,
   **Then** a spinner/progress indicator is shown and polling begins against `GET /api/v1/ai/requests/{id}`.

3. **Given** polling returns `status=completed`,
   **When** the UI updates,
   **Then** the spinner is replaced with a success message and a "Review Draft Course" link.

4. **Given** polling returns `status=failed`,
   **When** the UI updates,
   **Then** the spinner is replaced with the error message and a "Retry" button that re-submits the form.

5. **Given** `/admin/ai/log` is loaded,
   **When** the page renders,
   **Then** a table of past generation requests is shown with status, prompt preview, model, and timestamp.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                          |
|---------------|------------------------------------------------------------|
| BRD-FR-033    | COMP-007 Frontend — AI-generated draft label               |
| BRD-FR-035    | COMP-007 Frontend — error display + retry button           |
| BRD-NFR-002   | COMP-003 AI Generation — generation status polling         |

## Tasks Breakdown

| Task ID  | Description                                                              | Estimate |
|----------|--------------------------------------------------------------------------|----------|
| TASK-046 | Create AI generation templates (ai-generate.html, generation-log.html)   | 4h       |
| TASK-050 | Implement ai-generation.js (triggerGeneration, pollStatus, showResult)   | 3h       |

## UI/UX Notes

- Generation form: clean form card with labeled inputs; "Generate Course" CTA button
- Progress state: animated spinner with status text "Generating your course..." and progress indicator
- Success state: green banner with course title and "Review Draft" button
- Error state: red banner with error message and "Retry" button; details collapsible
- Generation log: table with truncated prompt preview (100 chars), status pill, model name, date/time

## Technical Notes

- **Stack:** Jinja2, Vanilla JS fetch with polling via `setInterval` or recursive `setTimeout`
- **Key considerations:** `ai-generation.js` stores `generationRequestId` after 202 response; polls every 3 seconds; clears interval on `completed` or `failed`; handles network errors in polling gracefully

## Dependencies

- STORY-019 (base template)
- STORY-014 (AI generation trigger + status poll API)
- STORY-016 (generation audit log API)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
