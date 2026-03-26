# Task: Create Course Detail and Lesson Viewer Templates + progress.js

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-042             |
| **Story**    | STORY-022            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 6h                   |

## Description

Create `course-detail.html` (module/lesson structure with completion status), `lesson-viewer.html` (Markdown content with Mark Complete button), and implement `progress.js` with the `recordLessonView()` and `markLessonComplete()` functions that auto-save progress.

## Implementation Details

**Files to create/modify:**
- `src/templates/learner/course-detail.html` — course overview with module accordion and lesson checklist
- `src/templates/learner/lesson-viewer.html` — lesson content area with navigation and Mark Complete button
- `src/static/js/progress.js` — `recordLessonView()`, `markLessonComplete()`, progress bar update functions

**Approach:**

**progress.js:**
```javascript
const ENROLLMENT_ID = document.body.dataset.enrollmentId;
const LESSON_ID = document.body.dataset.lessonId;

// Called on DOMContentLoaded — records lesson view (lastViewedAt)
async function recordLessonView(lessonId, enrollmentId) {
    try {
        const result = await apiFetch('/api/v1/progress', {
            method: 'POST',
            body: JSON.stringify({ lesson_id: lessonId, enrollment_id: enrollmentId, completed: false })
        });
        console.log('Lesson view recorded');
    } catch (e) {
        console.warn('Could not record lesson view:', e);
    }
}

// Called on "Mark Complete" button click
async function markLessonComplete(lessonId, enrollmentId) {
    const btn = document.getElementById('mark-complete-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Saving...';
    try {
        const result = await apiFetch('/api/v1/progress', {
            method: 'POST',
            body: JSON.stringify({ lesson_id: lessonId, enrollment_id: enrollmentId, completed: true })
        });
        btn.textContent = '✅ Completed';
        btn.classList.add('completed');
        // Update module progress bar
        updateProgressBar(result.completion_percentage);
        if (result.enrollment_status === 'completed') {
            showCourseCompletionBanner();
        }
    } catch (e) {
        btn.disabled = false;
        btn.textContent = 'Mark Complete';
        showError('Could not save progress. Please try again.');
    }
}

function updateProgressBar(percentage) {
    const bar = document.querySelector('.module-progress-fill');
    if (bar) bar.style.width = percentage + '%';
    const label = document.querySelector('.progress-label');
    if (label) label.textContent = percentage + '% complete';
}

document.addEventListener('DOMContentLoaded', () => {
    if (ENROLLMENT_ID && LESSON_ID) {
        recordLessonView(LESSON_ID, ENROLLMENT_ID);
    }
});
```

**lesson-viewer.html:** Renders pre-sanitised Markdown HTML (server baked-in via bleach), navigation (prev/next lesson), and "Mark Complete" button. Passes `data-enrollment-id` and `data-lesson-id` as `body` dataset attributes for `progress.js`.

## API Changes

N/A — calls existing progress API.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                            |
|-------------------|---------------------------------------------------|
| TASK-038          | Base template and CSS must exist                  |
| TASK-039          | Frontend router serves course/lesson routes       |
| TASK-025          | Progress recording API must be operational        |
| TASK-018          | Course/lesson data API must be operational        |

**Wave:** 7

## Acceptance Criteria

- [ ] Opening a lesson page automatically calls `recordLessonView()` (no user action required)
- [ ] "Mark Complete" button calls `markLessonComplete()` and updates UI without page reload
- [ ] Progress bar updates immediately after lesson completion
- [ ] Lesson Markdown content is rendered as HTML (no raw Markdown visible)
- [ ] `<script>` tags are absent from rendered lesson HTML (XSS protection)
- [ ] Prev/Next lesson navigation links work correctly

## Test Requirements

- **Unit tests:** Test `progress.js` functions with mock `fetch` responses
- **Integration tests:** GET lesson page → verify progress record created; click Mark Complete → verify completion status
- **Edge cases:** Mark Complete on already-completed lesson (idempotent); network error on Mark Complete

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-022        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-011, BRD-FR-017, BRD-FR-021, BRD-NFR-006, BRD-NFR-008 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
