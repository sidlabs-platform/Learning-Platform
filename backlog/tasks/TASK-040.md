# Task: Create Authentication Login Template

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-040             |
| **Story**    | STORY-020            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 3h                   |

## Description

Create the `login.html` Jinja2 template — a clean, centered login form with email/password fields, a "Sign In" button, inline error display, and Vanilla JS handling for the API call and redirect on success.

## Implementation Details

**Files to create/modify:**
- `src/templates/auth/login.html` — login form template extending `base.html`
- `src/static/js/utils.js` — ensure `apiFetch()` is available (may already exist from TASK-038)

**Approach:**
The login form submits via Vanilla JS `fetch()` to `POST /api/v1/auth/login` (not native form POST):
```html
{% extends "base.html" %}
{% block title %}Sign In — Learning Platform{% endblock %}
{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h1>🎓 Learning Platform</h1>
        <h2>Sign In</h2>
        <form id="login-form">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required autocomplete="email">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <div id="error-message" class="error-message" style="display:none"></div>
            <button type="submit" class="btn-primary btn-full" id="submit-btn">Sign In</button>
        </form>
    </div>
</div>
<script>
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    const errorDiv = document.getElementById('error-message');
    btn.disabled = true;
    btn.textContent = 'Signing in...';
    errorDiv.style.display = 'none';
    
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: document.getElementById('email').value,
                password: document.getElementById('password').value
            }),
            credentials: 'same-origin'
        });
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            errorDiv.textContent = data.detail || 'Invalid credentials. Please try again.';
            errorDiv.style.display = 'block';
        }
    } catch (err) {
        errorDiv.textContent = 'Network error. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Sign In';
    }
});
</script>
{% endblock %}
```

## API Changes

N/A — frontend only, calls existing `POST /api/v1/auth/login`.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                        |
|-------------------|-----------------------------------------------|
| TASK-038          | Base template and CSS must exist              |
| TASK-039          | Frontend router must serve `/login` route     |
| TASK-011          | Auth login endpoint must exist                |

**Wave:** 7

## Acceptance Criteria

- [ ] `GET /login` renders the login form with email and password fields
- [ ] Submitting valid credentials redirects to `/dashboard`
- [ ] Submitting invalid credentials shows inline error message without page reload
- [ ] "Sign In" button shows loading state while request is in flight
- [ ] Already-authenticated users visiting `/login` are redirected to `/dashboard`
- [ ] Form is responsive and centered on both mobile and desktop

## Test Requirements

- **Unit tests:** N/A — visual/functional
- **Integration tests:** Submit valid credentials → verify redirect; submit invalid → verify error display
- **Edge cases:** Network failure during login → error message shown; form submission with empty fields (HTML5 required validation)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-020        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-001, BRD-NFR-009 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
