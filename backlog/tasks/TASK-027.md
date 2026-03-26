# Task: Implement Prompt Templates (PT-001 through PT-005)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-027             |
| **Story**    | STORY-012            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3h                   |

## Description

Implement the five reusable prompt templates as application-level configuration constants in `src/ai_generation/prompt_templates.py`. Each template instructs GPT-4o to return JSON conforming to the defined content schema.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/__init__.py` — empty package marker
- `src/ai_generation/prompt_templates.py` — five `PromptTemplate` dataclass instances in a `PROMPT_TEMPLATES` dict

**Approach:**
```python
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    id: str
    name: str
    template: str  # f-string template with {placeholders}

PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "PT-001": PromptTemplate(
        id="PT-001",
        name="Generate Course Outline",
        template="""You are an expert GitHub training course designer.
Generate a complete structured course on the topic: {topic}

Target audience: {target_audience}
Learning objectives: {learning_objectives}
Difficulty level: {difficulty}
Number of modules: {desired_module_count}
Preferred tone: {preferred_tone}

Return ONLY valid JSON conforming to this exact schema:
{{
  "title": "string",
  "description": "string (100-500 chars)",
  "target_audience": "string",
  "learning_objectives": ["string"],
  "modules": [
    {{
      "title": "string",
      "summary": "string",
      "lessons": [
        {{
          "title": "string",
          "markdown_content": "string (full lesson in Markdown)",
          "estimated_minutes": integer
        }}
      ],
      "quiz_questions": [
        {{
          "question": "string",
          "options": ["string", "string", "string", "string"],
          "correct_answer": "string (must be one of options)",
          "explanation": "string"
        }}
      ]
    }}
  ]
}}
Do not include any text outside the JSON object."""
    ),
    "PT-002": PromptTemplate(
        id="PT-002",
        name="Generate Lesson Content",
        template="""Generate detailed Markdown lesson content for:
Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}
Difficulty: {difficulty}
Target audience: {target_audience}

Return ONLY valid JSON: {{"markdown_content": "string", "estimated_minutes": integer}}"""
    ),
    "PT-003": PromptTemplate(
        id="PT-003",
        name="Generate Quiz Questions",
        template="""Generate {question_count} multiple-choice quiz questions for:
Module: {module_title}
Course: {course_title}

Return ONLY valid JSON:
{{"quiz_questions": [{{"question": "string", "options": ["string"x4], "correct_answer": "string", "explanation": "string"}}]}}"""
    ),
    "PT-004": PromptTemplate(
        id="PT-004",
        name="Summarise Module",
        template="""Write a 2-3 sentence summary paragraph for this module:
Module title: {module_title}
Lesson titles: {lesson_titles}
Return ONLY valid JSON: {{"summary": "string"}}"""
    ),
    "PT-005": PromptTemplate(
        id="PT-005",
        name="Rewrite for Different Skill Level",
        template="""Rewrite the following lesson content for a {target_difficulty} audience.
Original content:
{original_content}
Return ONLY valid JSON: {{"markdown_content": "string", "estimated_minutes": integer}}"""
    ),
}
```

## API Changes

N/A — configuration constants only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                               |
|-------------------|--------------------------------------|
| TASK-001          | Project structure must exist         |

**Wave:** 3

## Acceptance Criteria

- [ ] `PROMPT_TEMPLATES` dict contains exactly 5 entries with keys `PT-001` through `PT-005`
- [ ] Each template contains `{placeholder}` syntax for all required dynamic values
- [ ] Each template includes explicit JSON schema instruction
- [ ] Templates are importable from `src.ai_generation.prompt_templates`

## Test Requirements

- **Unit tests:** Import `PROMPT_TEMPLATES` and verify 5 entries; test each template renders with sample values without KeyError
- **Integration tests:** N/A
- **Edge cases:** Template with missing placeholder value should raise `KeyError` (expected — caller's responsibility to provide all values)

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-012        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-036, BRD-INT-006, BRD-INT-007 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
