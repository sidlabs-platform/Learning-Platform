# Task: Create Quiz Template and quiz.js

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-043             |
| **Story**    | STORY-023            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 5h                   |

## Description

Create `quiz.html` template (module quiz with multiple-choice questions) and implement `quiz.js` with `submitQuiz()` and `showResults()` functions that submit answers to the API and display the score summary with answer reveals.

## Implementation Details

**Files to create/modify:**
- `src/templates/learner/quiz.html` — quiz form with radio buttons per question
- `src/static/js/quiz.js` — `submitQuiz()`, `showResults()`, `revealAnswers()` functions

**Approach:**

**quiz.html:**
```html
{% extends "base.html" %}
{% block content %}
<div class="quiz-container" data-enrollment-id="{{ enrollment_id }}" data-module-id="{{ module_id }}">
    <h2>{{ module_title }} — Knowledge Check</h2>
    <form id="quiz-form">
        {% for i, question in enumerate(questions) %}
        <div class="question-block" data-question-id="{{ question.id }}" data-correct="{{ question.correct_answer }}">
            <p class="question-text">{{ i+1 }}. {{ question.question }}</p>
            {% for option in question.options %}
            <label class="option-label">
                <input type="radio" name="q_{{ question.id }}" value="{{ option }}"> {{ option }}
            </label>
            {% endfor %}
        </div>
        {% endfor %}
        <button type="submit" class="btn-primary" id="submit-quiz-btn">Submit Quiz</button>
    </form>
    <div id="quiz-results" style="display:none"></div>
</div>
<script src="/static/js/quiz.js"></script>
{% endblock %}
```

**quiz.js:**
```javascript
document.getElementById('quiz-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    await submitQuiz();
});

async function submitQuiz() {
    const container = document.querySelector('.quiz-container');
    const enrollmentId = container.dataset.enrollmentId;
    const moduleId = container.dataset.moduleId;
    
    const answers = [];
    document.querySelectorAll('.question-block').forEach(block => {
        const questionId = block.dataset.questionId;
        const selected = block.querySelector('input[type=radio]:checked');
        if (selected) answers.push({ question_id: questionId, selected_answer: selected.value });
    });
    
    document.getElementById('submit-quiz-btn').disabled = true;
    
    const result = await apiFetch(`/api/v1/enrollments/${enrollmentId}/quiz-submit`, {
        method: 'POST',
        body: JSON.stringify({ module_id: moduleId, answers })
    });
    
    showResults(result);
    revealAnswers();
}

function showResults(score) {
    const resultsDiv = document.getElementById('quiz-results');
    const passClass = score.passed ? 'pass-badge' : 'fail-badge';
    const passText = score.passed ? '✅ PASSED' : '❌ FAILED';
    resultsDiv.innerHTML = `
        <div class="score-card">
            <div class="score-number">${score.percentage.toFixed(0)}%</div>
            <p>${score.correct} / ${score.total} correct</p>
            <span class="badge ${passClass}">${passText}</span>
        </div>`;
    resultsDiv.style.display = 'block';
    document.getElementById('quiz-form').querySelector('button').style.display = 'none';
}

function revealAnswers() {
    document.querySelectorAll('.question-block').forEach(block => {
        const correctAnswer = block.dataset.correct;
        block.querySelectorAll('input[type=radio]').forEach(radio => {
            radio.disabled = true;
            const label = radio.parentElement;
            if (radio.value === correctAnswer) label.classList.add('correct-answer');
            else if (radio.checked) label.classList.add('wrong-answer');
        });
    });
}
```

## API Changes

N/A — calls existing quiz-submit API.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                         |
|-------------------|------------------------------------------------|
| TASK-038          | Base template and CSS must exist               |
| TASK-039          | Frontend router serves quiz route              |
| TASK-025          | Quiz submission API must be operational        |

**Wave:** 7

## Acceptance Criteria

- [ ] Quiz page renders all MCQ questions as radio button forms
- [ ] Submitting the quiz calls `POST /api/v1/enrollments/{id}/quiz-submit`
- [ ] Score card shows: percentage, correct/total, pass/fail badge
- [ ] Answer reveal shows green for correct, red for wrong selection after submit
- [ ] Informational quiz shows "No pass/fail requirement" instead of pass/fail badge
- [ ] Radio buttons are disabled after submission (no re-answer)

## Test Requirements

- **Unit tests:** Test `showResults()` with pass and fail scores; test `revealAnswers()` DOM manipulation
- **Integration tests:** Load quiz page → submit → verify results displayed
- **Edge cases:** Submit with not all questions answered (partial submission); network error during submit

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-023        |
| Epic     | EPIC-007         |
| BRD      | BRD-FR-022, BRD-FR-024, BRD-FR-025 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
