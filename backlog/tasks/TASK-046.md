# Task: Create Admin Reporting Dashboard Template

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-046             |
| **Story**    | STORY-026            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5h                   |

## Description

Create the admin reporting dashboard template (`admin/dashboard.html`) with KPI summary cards, per-course metrics table, quiz performance summary, filter controls, and a "Export CSV" download button.

## Implementation Details

**Files to create/modify:**
- `src/templates/admin/dashboard.html` — admin reporting dashboard page

**Approach:**
The page fetches `GET /api/v1/reports/dashboard` on load and renders metrics. Filter changes re-fetch with query params. CSV export triggers file download via `window.location.href`.

```html
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1>📊 Training Dashboard</h1>
    <a href="/admin/courses" class="btn-secondary">Manage Courses</a>
</div>

<!-- Filter Bar -->
<div class="filter-bar">
    <select id="course-filter"><option value="">All Courses</option></select>
    <button onclick="applyFilters()" class="btn-secondary">Apply Filter</button>
    <a id="export-btn" class="btn-secondary" href="/api/v1/reports/export?format=csv">📥 Export CSV</a>
</div>

<!-- KPI Cards -->
<div class="kpi-grid" id="kpi-cards">
    <div class="kpi-card"><div class="kpi-number" id="total-learners">—</div><div>Total Learners</div></div>
    <div class="kpi-card"><div class="kpi-number" id="total-enrollments">—</div><div>Total Enrollments</div></div>
    <div class="kpi-card"><div class="kpi-number" id="completion-rate">—</div><div>Completion Rate</div></div>
    <div class="kpi-card"><div class="kpi-number" id="in-progress-count">—</div><div>In Progress</div></div>
</div>

<!-- Per-Course Metrics Table -->
<section class="metrics-section">
    <h2>Course Metrics</h2>
    <table class="data-table" id="course-metrics-table">
        <thead>
            <tr><th>Course</th><th>Enrolled</th><th>Completed</th><th>In Progress</th><th>Completion %</th><th>Avg Quiz Score</th></tr>
        </thead>
        <tbody id="course-metrics-body"></tbody>
    </table>
</section>

<!-- Quiz Summary -->
<section class="metrics-section">
    <h2>Quiz Performance</h2>
    <table class="data-table" id="quiz-table">
        <thead><tr><th>Module</th><th>Total Attempts</th><th>Avg Score</th><th>Pass Rate</th></tr></thead>
        <tbody id="quiz-body"></tbody>
    </table>
</section>

<script>
async function loadDashboard(courseId = '', userId = '') {
    const params = new URLSearchParams();
    if (courseId) params.set('course_id', courseId);
    if (userId) params.set('user_id', userId);
    
    const data = await apiFetch(`/api/v1/reports/dashboard?${params}`);
    
    document.getElementById('total-learners').textContent = data.total_learners;
    document.getElementById('total-enrollments').textContent = data.total_enrollments;
    document.getElementById('completion-rate').textContent = data.overall_completion_rate.toFixed(1) + '%';
    
    // Populate course metrics table
    const tbody = document.getElementById('course-metrics-body');
    tbody.innerHTML = data.course_metrics.map(c => `
        <tr>
            <td>${c.course_title}</td>
            <td>${c.total_enrollments}</td>
            <td>${c.completed_count}</td>
            <td>${c.in_progress_count}</td>
            <td>${c.completion_rate.toFixed(1)}%</td>
            <td>${c.avg_quiz_score !== null ? c.avg_quiz_score.toFixed(1) + '%' : 'N/A'}</td>
        </tr>`).join('');
    
    // Populate course filter
    const select = document.getElementById('course-filter');
    data.course_metrics.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.course_id;
        opt.textContent = c.course_title;
        select.appendChild(opt);
    });
}

function applyFilters() {
    const courseId = document.getElementById('course-filter').value;
    loadDashboard(courseId);
    // Update CSV export link with filters
    document.getElementById('export-btn').href = `/api/v1/reports/export?format=csv${courseId ? '&course_id=' + courseId : ''}`;
}

document.addEventListener('DOMContentLoaded', () => loadDashboard());
</script>
{% endblock %}
```

## API Changes

N/A — calls existing reporting APIs.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                          |
|-------------------|-------------------------------------------------|
| TASK-038          | Base template and CSS must exist                |
| TASK-039          | Frontend router serves `/admin` route           |
| TASK-037          | Reporting dashboard API must be operational     |

**Wave:** 8

## Acceptance Criteria

- [ ] Dashboard loads and populates all 4 KPI cards
- [ ] Course metrics table shows per-course enrollment and completion data
- [ ] Course filter dropdown populates from API data
- [ ] Changing course filter and clicking "Apply" re-fetches scoped metrics
- [ ] "Export CSV" button triggers file download with current filter applied
- [ ] Learner accessing `/admin` is redirected (handled by frontend router TASK-039)

## Test Requirements

- **Unit tests:** Test `applyFilters()` builds correct query params
- **Integration tests:** Load `/admin` → verify KPI cards populated; verify CSV download link
- **Edge cases:** Dashboard with zero data (no enrollments); quiz summary with no attempts (shows "N/A")

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-026        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-026, BRD-FR-027, BRD-FR-028, BRD-NFR-009 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
