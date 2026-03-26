# Task: Create Admin AI Generation Templates and ai-generation.js

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-045             |
| **Story**    | STORY-025            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5h                   |

## Description

Create the admin AI generation form template (`ai-generate.html`), the generation audit log template (`generation-log.html`), and `ai-generation.js` with generation trigger, status polling, and result/error display logic.

## Implementation Details

**Files to create/modify:**
- `src/templates/admin/ai-generate.html` — AI generation form with status polling UI
- `src/templates/admin/generation-log.html` — audit log table of past generation requests
- `src/static/js/ai-generation.js` — `triggerGeneration()`, `pollGenerationStatus()`, `showGenerationResult()`, `showGenerationError()`

**Approach:**

**ai-generate.html:**
```html
{% extends "base.html" %}
{% block content %}
<h1>🤖 AI Course Generator</h1>
<div id="generation-form-section">
    <form id="generation-form">
        <div class="form-group">
            <label>Topic *</label>
            <input type="text" name="topic" placeholder="e.g. GitHub Actions for CI/CD" required>
        </div>
        <div class="form-group">
            <label>Target Audience *</label>
            <input type="text" name="target_audience" placeholder="e.g. Junior developers" required>
        </div>
        <div class="form-group">
            <label>Learning Objectives * (one per line)</label>
            <textarea name="learning_objectives" rows="4" placeholder="Understand GitHub Actions&#10;Create workflows&#10;Debug CI failures"></textarea>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Difficulty *</label>
                <select name="difficulty">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate" selected>Intermediate</option>
                    <option value="advanced">Advanced</option>
                </select>
            </div>
            <div class="form-group">
                <label>Number of Modules</label>
                <input type="number" name="desired_module_count" min="1" max="10" value="5">
            </div>
        </div>
        <div class="form-group">
            <label>Preferred Tone</label>
            <input type="text" name="preferred_tone" placeholder="professional" value="professional">
        </div>
        <button type="submit" class="btn-primary btn-lg" id="generate-btn">🚀 Generate Course</button>
    </form>
</div>
<div id="generation-status" style="display:none">
    <!-- Loading, success, or error state shown here -->
</div>
{% endblock %}
{% block extra_js %}<script src="/static/js/ai-generation.js"></script>{% endblock %}
```

**ai-generation.js:**
```javascript
let pollInterval = null;

document.getElementById('generation-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    await triggerGeneration();
});

async function triggerGeneration() {
    const form = document.getElementById('generation-form');
    const data = new FormData(form);
    const objectives = data.get('learning_objectives').split('\n').filter(o => o.trim());
    
    const payload = {
        topic: data.get('topic'),
        target_audience: data.get('target_audience'),
        learning_objectives: objectives,
        difficulty: data.get('difficulty'),
        desired_module_count: parseInt(data.get('desired_module_count')),
        preferred_tone: data.get('preferred_tone') || 'professional'
    };
    
    showLoadingState();
    
    try {
        const result = await apiFetch('/api/v1/ai/generate-course', {
            method: 'POST', body: JSON.stringify(payload)
        });
        startPolling(result.request_id);
    } catch (e) {
        showError(e.message || 'Failed to start generation. Please try again.');
    }
}

function startPolling(requestId) {
    pollInterval = setInterval(async () => {
        const status = await apiFetch(`/api/v1/ai/requests/${requestId}`);
        if (status.status === 'completed') {
            clearInterval(pollInterval);
            showSuccess(status.course_id);
        } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            showError(status.error_message || 'Generation failed.', requestId);
        }
        // else in_progress/pending: keep polling
    }, 3000);
}

function showLoadingState() {
    document.getElementById('generation-form-section').style.display = 'none';
    document.getElementById('generation-status').innerHTML = `
        <div class="loading-card">
            <div class="spinner"></div>
            <h3>Generating your course...</h3>
            <p>This may take up to 60 seconds. Please wait.</p>
        </div>`;
    document.getElementById('generation-status').style.display = 'block';
}

function showSuccess(courseId) {
    document.getElementById('generation-status').innerHTML = `
        <div class="success-card">
            <h3>✅ Course Generated Successfully!</h3>
            <p>Your draft course is ready for review.</p>
            <a href="/admin/courses/${courseId}/edit" class="btn-primary">Review Draft Course</a>
        </div>`;
}

function showError(errorMessage, requestId) {
    document.getElementById('generation-status').innerHTML = `
        <div class="error-card">
            <h3>❌ Generation Failed</h3>
            <p>${errorMessage}</p>
            <button onclick="retryGeneration()" class="btn-secondary">🔄 Retry</button>
        </div>`;
}

function retryGeneration() {
    document.getElementById('generation-form-section').style.display = 'block';
    document.getElementById('generation-status').style.display = 'none';
}
```

## API Changes

N/A — calls existing AI generation APIs.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                           |
|-------------------|--------------------------------------------------|
| TASK-038          | Base template and CSS must exist                 |
| TASK-039          | Frontend router serves admin AI routes           |
| TASK-032          | AI generation trigger + status poll API must work|
| TASK-034          | Generation audit log API must work               |

**Wave:** 8

## Acceptance Criteria

- [ ] Submitting the generation form calls `POST /api/v1/ai/generate-course`
- [ ] Spinner/loading state shows immediately after form submission
- [ ] Polling starts at 3-second intervals against status endpoint
- [ ] Success state shows course link when status is `completed`
- [ ] Error state shows error message and "Retry" button when status is `failed`
- [ ] Retry button restores the form to its pre-submission state
- [ ] Generation log table shows all past requests with status and timestamp

## Test Requirements

- **Unit tests:** Test `startPolling()` clears interval on completed/failed status
- **Integration tests:** Load `/admin/ai/generate` → submit form → verify 202; mock completion → verify success UI
- **Edge cases:** Network error during polling; page reload during generation (polls lost — user must check audit log)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-025        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-033, BRD-FR-035, BRD-NFR-002 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
