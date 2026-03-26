"""Prompt templates for GitHub Models (GPT-4o) content generation.

Each ``PromptTemplate`` wraps a single LLM prompt string that instructs GPT-4o
to return *only* valid JSON conforming to a defined schema.  The templates use
standard Python ``str.format_map`` / ``str.format`` ``{placeholder}`` syntax so
callers can substitute values at call-time.

Usage example::

    from src.ai_generation.prompt_templates import PROMPT_TEMPLATES

    pt = PROMPT_TEMPLATES["PT-001"]
    prompt = pt.template.format(
        topic="GitHub Actions",
        target_audience="DevOps engineers",
        learning_objectives="Understand CI/CD pipelines",
        difficulty="intermediate",
        desired_module_count=4,
        preferred_tone="professional",
    )
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    """Immutable container for a single LLM prompt template.

    Attributes:
        id: Unique identifier (e.g. ``"PT-001"``).
        name: Human-readable name for the template.
        template: The prompt string containing ``{placeholder}`` tokens that
            must be substituted before the prompt is sent to the model.
    """

    id: str
    name: str
    template: str


# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------

PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    # ------------------------------------------------------------------
    # PT-001 — Generate a full course outline
    # ------------------------------------------------------------------
    "PT-001": PromptTemplate(
        id="PT-001",
        name="Generate Course Outline",
        template=(
            "You are an expert GitHub training course designer.\n"
            "Generate a complete structured course on the topic: {topic}\n\n"
            "Target audience: {target_audience}\n"
            "Learning objectives: {learning_objectives}\n"
            "Difficulty level: {difficulty}\n"
            "Number of modules: {desired_module_count}\n"
            "Preferred tone: {preferred_tone}\n\n"
            "Return ONLY valid JSON conforming to this exact schema:\n"
            "{{\n"
            '  "title": "string",\n'
            '  "description": "string (100-500 chars)",\n'
            '  "target_audience": "string",\n'
            '  "learning_objectives": ["string"],\n'
            '  "modules": [\n'
            "    {{\n"
            '      "title": "string",\n'
            '      "summary": "string",\n'
            '      "lessons": [\n'
            "        {{\n"
            '          "title": "string",\n'
            '          "markdown_content": "string (full lesson in Markdown)",\n'
            '          "estimated_minutes": integer\n'
            "        }}\n"
            "      ],\n"
            '      "quiz_questions": [\n'
            "        {{\n"
            '          "question": "string",\n'
            '          "options": ["string", "string", "string", "string"],\n'
            '          "correct_answer": "string (must be one of options)",\n'
            '          "explanation": "string"\n'
            "        }}\n"
            "      ]\n"
            "    }}\n"
            "  ]\n"
            "}}\n"
            "Do not include any text outside the JSON object."
        ),
    ),

    # ------------------------------------------------------------------
    # PT-002 — Generate detailed content for a single lesson
    # ------------------------------------------------------------------
    "PT-002": PromptTemplate(
        id="PT-002",
        name="Generate Lesson Content",
        template=(
            "Generate detailed Markdown lesson content for:\n"
            "Course: {course_title}\n"
            "Module: {module_title}\n"
            "Lesson: {lesson_title}\n"
            "Difficulty: {difficulty}\n"
            "Target audience: {target_audience}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"markdown_content": "string", "estimated_minutes": integer}}'
        ),
    ),

    # ------------------------------------------------------------------
    # PT-003 — Generate multiple-choice quiz questions for a module
    # ------------------------------------------------------------------
    "PT-003": PromptTemplate(
        id="PT-003",
        name="Generate Quiz Questions",
        template=(
            "Generate {question_count} multiple-choice quiz questions for:\n"
            "Module: {module_title}\n"
            "Course: {course_title}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"quiz_questions": [{{'
            '"question": "string", '
            '"options": ["string", "string", "string", "string"], '
            '"correct_answer": "string", '
            '"explanation": "string"'
            "}}]}}"
        ),
    ),

    # ------------------------------------------------------------------
    # PT-004 — Write a concise summary paragraph for a module
    # ------------------------------------------------------------------
    "PT-004": PromptTemplate(
        id="PT-004",
        name="Summarise Module",
        template=(
            "Write a 2-3 sentence summary paragraph for this module:\n"
            "Module title: {module_title}\n"
            "Lesson titles: {lesson_titles}\n\n"
            'Return ONLY valid JSON: {{"summary": "string"}}'
        ),
    ),

    # ------------------------------------------------------------------
    # PT-005 — Rewrite lesson content for a different skill level
    # ------------------------------------------------------------------
    "PT-005": PromptTemplate(
        id="PT-005",
        name="Rewrite for Different Skill Level",
        template=(
            "Rewrite the following lesson content for a {target_difficulty} audience.\n"
            "Original content:\n"
            "{original_content}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"markdown_content": "string", "estimated_minutes": integer}}'
        ),
    ),
}
