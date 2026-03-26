# Task: Create Base HTML Template and CSS Design System

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-038             |
| **Story**    | STORY-019            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 4h                   |

## Description

Create the base Jinja2 HTML template (`base.html`) and the CSS design system files (base.css, layout.css, components.css, learner.css, admin.css) that all pages extend, providing a consistent navigation bar, responsive grid layout, and reusable UI components.

## Implementation Details

**Files to create/modify:**
- `src/templates/base.html` — HTML skeleton with nav, content block, cookie-aware auth state
- `src/static/css/base.css` — CSS custom properties (colors, fonts, spacing), reset, typography
- `src/static/css/layout.css` — responsive grid, header, sidebar, main content area (breakpoints: 768px, 1280px)
- `src/static/css/components.css` — buttons (.btn-primary, .btn-secondary), cards, badges (.badge-draft, .badge-published), progress bars, modals
- `src/static/css/learner.css` — learner dashboard, lesson viewer, quiz page styles
- `src/static/css/admin.css` — admin course editor, AI generation form, reporting dashboard styles
- `src/static/js/utils.js` — shared `apiFetch(url, options)` wrapper with error handling and JSON parsing

**Approach:**
`base.html` template structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Learning Platform{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/base.css">
    <link rel="stylesheet" href="/static/css/layout.css">
    <link rel="stylesheet" href="/static/css/components.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">🎓 Learning Platform</a>
        <div class="nav-links">
            {% if user %}
                {% if user.role == "learner" %}
                    <a href="/dashboard">Dashboard</a>
                    <a href="/catalog">Catalog</a>
                {% else %}
                    <a href="/admin">Admin Dashboard</a>
                    <a href="/admin/courses">Courses</a>
                    <a href="/admin/ai/generate">AI Generate</a>
                {% endif %}
                <span class="nav-user">{{ user.name }}</span>
                <button onclick="logout()" class="btn-secondary btn-sm">Logout</button>
            {% endif %}
        </div>
    </nav>
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    <script src="/static/js/utils.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

CSS custom properties in `base.css`:
```css
:root {
    --color-primary: #0366d6;
    --color-secondary: #586069;
    --color-success: #28a745;
    --color-danger: #dc3545;
    --color-warning: #ffc107;
    --color-bg: #f6f8fa;
    --color-card-bg: #ffffff;
    --spacing-unit: 8px;
    --border-radius: 6px;
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

## API Changes

N/A — frontend only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                           |
|-------------------|--------------------------------------------------|
| TASK-003          | FastAPI app must serve /static files             |

**Wave:** 5

## Acceptance Criteria

- [ ] `base.html` renders correctly and extends to child templates via `{% block content %}`
- [ ] Navigation shows role-appropriate links when `user` is passed in template context
- [ ] Responsive layout works at 768px (tablet) and 1280px (desktop) — no horizontal scroll
- [ ] `.btn-primary`, `.btn-secondary`, `.badge-published`, `.badge-draft` classes are defined
- [ ] `utils.js` `apiFetch()` handles network errors and returns parsed JSON or throws

## Test Requirements

- **Unit tests:** N/A — visual/manual
- **Integration tests:** Verify `/` serves `Content-Type: text/html`; verify static CSS is served from `/static/css/base.css`
- **Edge cases:** Long user name in navbar doesn't break layout; empty nav links for unauthenticated user

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-019        |
| Epic     | EPIC-007         |
| BRD      | BRD-NFR-008, BRD-NFR-009 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
