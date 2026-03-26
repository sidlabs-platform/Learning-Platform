# Task: Create Admin Course Management Templates and course-editor.js

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-044             |
| **Story**    | STORY-024            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 8h                   |

## Description

Create the admin course management templates (`course-list.html`, `course-editor.html`, `lesson-editor.html`) and `course-editor.js` implementing all admin CRUD actions for courses, modules, lessons, and the publish/unpublish workflow.

## Implementation Details

**Files to create/modify:**
- `src/templates/admin/course-list.html` — table of all courses with status badges and action buttons
- `src/templates/admin/course-editor.html` — full course editor with module/lesson management
- `src/templates/admin/lesson-editor.html` — Markdown editor for a single lesson
- `src/static/js/course-editor.js` — all admin CRUD operations via fetch API

**Approach:**

**course-list.html** — fetches `GET /api/v1/courses` (admin sees all), renders table with:
- Columns: Title, Status (badge), Difficulty, Created, Actions (Edit, Publish/Unpublish, Delete)
- Publish/Unpublish button calls respective PATCH endpoints and updates badge inline

**course-editor.html** — complex page with:
- Top section: course metadata form (title, description, difficulty, duration, audience, objectives, tags)
- Middle section: module list with collapsible lessons per module
- Actions: Add Module, Add Lesson per module, Edit/Delete actions inline
- "AI-generated draft" badge (`badge-ai-draft`) next to AI-generated sections (`isAiGenerated=true`)
- "Publish Course" / "Unpublish Course" button at top

**lesson-editor.html** — textarea for Markdown with character count, optional preview toggle, Save button

**course-editor.js:**
```javascript
async function publishCourse(courseId) {
    const result = await apiFetch(`/api/v1/courses/${courseId}/publish`, { method: 'PATCH' });
    updateStatusBadge(courseId, result.status);
}

async function unpublishCourse(courseId) {
    const result = await apiFetch(`/api/v1/courses/${courseId}/unpublish`, { method: 'PATCH' });
    updateStatusBadge(courseId, result.status);
}

async function createModule(courseId, moduleData) {
    return apiFetch(`/api/v1/courses/${courseId}/modules`, {
        method: 'POST', body: JSON.stringify(moduleData)
    });
}

async function createLesson(courseId, moduleId, lessonData) {
    return apiFetch(`/api/v1/courses/${courseId}/modules/${moduleId}/lessons`, {
        method: 'POST', body: JSON.stringify(lessonData)
    });
}

async function saveLessonContent(lessonId, content) {
    return apiFetch(`/api/v1/lessons/${lessonId}`, {
        method: 'PATCH', body: JSON.stringify({ markdown_content: content })
    });
}
```

## API Changes

N/A — calls existing course management APIs.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                          |
|-------------------|-------------------------------------------------|
| TASK-038          | Base template and CSS must exist                |
| TASK-039          | Frontend router serves admin course routes      |
| TASK-018          | Course management API must be operational       |

**Wave:** 7

## Acceptance Criteria

- [ ] Course list shows all courses (draft and published) with correct status badges
- [ ] Publish button transitions course to published; badge updates inline without page reload
- [ ] Course editor shows "AI-generated draft" badge on AI-sourced sections
- [ ] Add module / add lesson forms work inline without navigation
- [ ] Lesson editor saves Markdown content via PATCH and shows confirmation

## Test Requirements

- **Unit tests:** Test `publishCourse()` function with mock API response
- **Integration tests:** Load `/admin/courses` → verify 3 seeded courses listed; publish a course; verify badge update
- **Edge cases:** Publish already-published course → handle 409 with user-friendly message; delete course with enrollments

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-024        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-007, BRD-FR-008, BRD-FR-033, BRD-FR-039 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
