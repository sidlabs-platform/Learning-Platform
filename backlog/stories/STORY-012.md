# Story: Prompt Templates and Orchestration Layer

| Field        | Value                |
|--------------|----------------------|
| **Story ID** | STORY-012            |
| **Epic**     | EPIC-005             |
| **Status**   | Ready                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 3 points             |
| **Priority** | P0                   |

## User Story

**As an** Admin triggering AI course generation,
**I want** the system to use well-structured, reusable prompt templates that produce consistent, schema-conformant JSON responses from GPT-4o,
**so that** the generated content can be reliably parsed, validated, and stored as draft course material.

## Acceptance Criteria

1. **Given** the `PROMPT_TEMPLATES` dict is imported,
   **When** it is inspected,
   **Then** five templates are present with IDs PT-001 through PT-005 (Generate Course Outline, Generate Lesson Content, Generate Quiz Questions, Summarise Module, Rewrite for Different Skill Level).

2. **Given** a `GenerationRequest` with topic, audience, objectives, difficulty, and module count,
   **When** `render_course_generation_prompt(request)` is called,
   **Then** the returned string contains the request values interpolated correctly and includes an explicit JSON schema instruction.

3. **Given** an unknown template ID,
   **When** `get_prompt_template("PT-999")` is called,
   **Then** `PromptTemplateNotFoundError` is raised.

## BRD & Design References

| BRD ID        | HLD/LLD Component                                           |
|---------------|-------------------------------------------------------------|
| BRD-FR-036    | COMP-003 AI Generation — 5 prompt template library         |
| BRD-INT-006   | COMP-003 AI Generation — JSON schema instruction in prompts |
| BRD-INT-007   | COMP-003 AI Generation — template storage as config        |
| BRD-INT-008   | COMP-003 AI Generation — layered MCP-ready architecture    |

## Tasks Breakdown

| Task ID  | Description                                               | Estimate |
|----------|-----------------------------------------------------------|----------|
| TASK-028 | Implement 5 prompt templates (prompt_templates.py)        | 3h       |
| TASK-029 | Implement prompt service (render functions + validation)  | 2h       |

## UI/UX Notes

N/A — backend prompt layer only.

## Technical Notes

- **Stack:** Python dataclasses/Pydantic, f-string template rendering
- **Key considerations:** Templates stored as constants in `prompt_templates.py`; each template includes explicit instruction to return valid JSON conforming to the `GeneratedCourseSchema`; template ID referenced in `ContentGenerationRequest` for audit traceability

## Dependencies

- STORY-001 (project structure)

## Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit and integration tests written and passing
- [ ] API documentation updated (if applicable)
- [ ] Code reviewed and approved
- [ ] No regressions in existing tests
