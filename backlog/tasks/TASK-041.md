# Task: Create Learner Dashboard and Catalog Templates

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-041             |
| **Story**    | STORY-021            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5h                   |

## Description

Create the learner `dashboard.html` (enrolled courses with progress) and `catalog.html` (published course catalog with search/filter) Jinja2 templates, including Vanilla JS for fetching data via the API and rendering dynamic updates.

## Implementation Details

**Files to create/modify:**
- `src/templates/learner/dashboard.html` — enrolled courses grid with completion progress bars
- `src/templates/learner/catalog.html` — published course catalog with difficulty and tag filters

**Approach:**

**dashboard.html** — loads enrolled courses via `GET /api/v1/enrollments?userId={userId}` + course data:
```html
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1>My Learning Dashboard</h1>
    <a href="/catalog" class="btn-primary">Browse Catalog</a>
</div>
<div id="enrolled-courses" class="courses-grid">
    <!-- Populated by JavaScript -->
    <div class="loading-spinner">Loading your courses...</div>
</div>
<script>
async function loadDashboard() {
    const enrollments = await apiFetch('/api/v1/enrollments?userId={{ user.id }}');
    const container = document.getElementById('enrolled-courses');
    if (!enrollments.length) {
        container.innerHTML = `<div class="empty-state">
            <p>You haven't enrolled in any courses yet.</p>
            <a href="/catalog" class="btn-primary">Browse Catalog</a>
        </div>`;
        return;
    }
    // Render course cards with progress bars
    container.innerHTML = enrollments.map(renderCourseCard).join('');
}
function renderCourseCard(enrollment) {
    const pct = enrollment.completion_percentage || 0;
    const btnText = enrollment.status === 'not_started' ? 'Start Course' : 'Continue';
    const btnHref = enrollment.last_lesson_id 
        ? `/courses/${enrollment.course_id}/lessons/${enrollment.last_lesson_id}`
        : `/courses/${enrollment.course_id}`;
    return `<div class="course-card">
        <h3>${enrollment.course_title || 'Course'}</h3>
        <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
        <span>${pct}% complete</span>
        <a href="${btnHref}" class="btn-primary">${btnText}</a>
    </div>`;
}
document.addEventListener('DOMContentLoaded', loadDashboard);
</script>
{% endblock %}
```

**catalog.html** — loads and filters courses:
- Difficulty dropdown filter
- Tag chip filters (dynamically extracted from courses)
- "Enroll" button calls `POST /api/v1/enrollments` then redirects to course detail

## API Changes

N/A — calls existing endpoints.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                         |
|-------------------|------------------------------------------------|
| TASK-038          | Base template and CSS must exist               |
| TASK-039          | Frontend router must serve `/dashboard`, `/catalog` |
| TASK-018          | Course catalog API must be operational         |
| TASK-025          | Enrollment API must be operational             |

**Wave:** 7

## Acceptance Criteria

- [ ] Dashboard shows all enrolled courses with progress bars
- [ ] "Continue" button on in-progress course links directly to last-accessed lesson (≤ 2 clicks)
- [ ] Empty state shown when no enrollments with "Browse Catalog" CTA
- [ ] Catalog shows all published courses with difficulty badges
- [ ] Difficulty filter updates the displayed course list
- [ ] "Enroll" button in catalog creates enrollment and redirects to course detail

## Test Requirements

- **Unit tests:** N/A — visual/functional
- **Integration tests:** Verify `/dashboard` page loads for authenticated learner; verify `/catalog` shows only published courses
- **Edge cases:** Dashboard with 0 enrollments; catalog with 0 matching filter results; enroll when already enrolled (409 error handling)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-021        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-005, BRD-FR-006, BRD-FR-015, BRD-NFR-008, BRD-NFR-009 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
