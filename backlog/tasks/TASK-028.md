# Task: Implement Prompt Service (Template Rendering)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-028             |
| **Story**    | STORY-012            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement the Prompt Orchestration Layer (`src/ai_generation/prompt_service.py`) with functions to select templates, render prompts with dynamic values, and log which template was used in each generation request.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/prompt_service.py` — `get_prompt_template()`, `render_course_generation_prompt()`, `render_section_regeneration_prompt()`
- `src/ai_generation/exceptions.py` — `GenerationFailedError`, `PromptTemplateNotFoundError`, `SchemaValidationError`

**Approach:**
```python
from .prompt_templates import PROMPT_TEMPLATES, PromptTemplate
from .exceptions import PromptTemplateNotFoundError

def get_prompt_template(template_id: str) -> PromptTemplate:
    if template_id not in PROMPT_TEMPLATES:
        raise PromptTemplateNotFoundError(f"Template '{template_id}' not found")
    return PROMPT_TEMPLATES[template_id]

def render_course_generation_prompt(request: GenerationRequest) -> tuple[str, str]:
    """Returns (rendered_prompt, template_id_used)."""
    template = get_prompt_template("PT-001")
    rendered = template.template.format(
        topic=request.topic,
        target_audience=request.target_audience,
        learning_objectives=", ".join(request.learning_objectives),
        difficulty=request.difficulty,
        desired_module_count=request.desired_module_count,
        preferred_tone=request.preferred_tone or "professional"
    )
    return rendered, "PT-001"

def render_section_regeneration_prompt(section_type: str, section_context: dict) -> tuple[str, str]:
    """Select appropriate template based on section_type and render."""
    template_map = {
        "lesson": "PT-002",
        "quiz": "PT-003",
        "module_summary": "PT-004",
        "skill_rewrite": "PT-005"
    }
    template_id = template_map.get(section_type, "PT-002")
    template = get_prompt_template(template_id)
    rendered = template.template.format(**section_context)
    return rendered, template_id
```

## API Changes

N/A — service layer only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                         |
|-------------------|------------------------------------------------|
| TASK-027          | Prompt templates constants must exist          |
| TASK-030          | AI generation Pydantic models (GenerationRequest) needed |

**Wave:** 4

## Acceptance Criteria

- [ ] `get_prompt_template("PT-001")` returns the correct template
- [ ] `get_prompt_template("PT-999")` raises `PromptTemplateNotFoundError`
- [ ] `render_course_generation_prompt(request)` returns rendered prompt with all request values interpolated
- [ ] Rendered PT-001 prompt contains the JSON schema instruction
- [ ] `render_section_regeneration_prompt("lesson", {...})` selects PT-002

## Test Requirements

- **Unit tests:** Test each `get_prompt_template` call; test `render_course_generation_prompt` with sample `GenerationRequest`; test unknown template ID raises error
- **Integration tests:** N/A
- **Edge cases:** Request with empty `learning_objectives` list; `preferredTone=None` defaults to "professional"

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-012        |
| Epic     | EPIC-005         |
| BRD      | BRD-FR-036, BRD-INT-007, BRD-INT-008 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
