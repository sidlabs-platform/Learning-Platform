"""Prompt templates for AI-assisted course content generation.

This module defines five reusable prompt templates (PT-001 through PT-005) as
:class:`PromptTemplate` dataclass instances.  Each template contains a
``{placeholder}`` formatted string that callers fill with domain-specific
values before sending to the GitHub Models API.

All templates instruct the model to return **only valid JSON**, with an explicit
schema to ensure consistent, parseable output.

Usage::

    from src.ai_generation.prompt_templates import PROMPT_TEMPLATES

    template = PROMPT_TEMPLATES["PT-001"]
    prompt = template.template.format(
        topic="GitHub Actions",
        target_audience="Developers new to CI/CD",
        learning_objectives="Understand workflows; Create pipelines",
        difficulty="beginner",
        desired_module_count=4,
        preferred_tone="practical",
    )
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# PromptTemplate dataclass
# ---------------------------------------------------------------------------


@dataclass
class PromptTemplate:
    """A named, versioned prompt template for the GitHub Models API.

    Attributes:
        id: Short identifier string, e.g. ``"PT-001"``.
        name: Human-readable name for display in admin UIs.
        template: The raw template string.  Use Python's ``str.format()`` to
            substitute ``{placeholder}`` variables before sending to the model.
    """

    id: str
    name: str
    template: str


# ---------------------------------------------------------------------------
# Template registry — PT-001 through PT-005
# ---------------------------------------------------------------------------

PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "PT-001": PromptTemplate(
        id="PT-001",
        name="Generate Course Outline",
        template=(
            "You are an expert curriculum designer creating a structured online learning course.\n\n"
            "Topic: {topic}\n"
            "Target Audience: {target_audience}\n"
            "Learning Objectives: {learning_objectives}\n"
            "Difficulty Level: {difficulty}\n"
            "Number of Modules: {desired_module_count}\n"
            "Preferred Tone: {preferred_tone}\n\n"
            "Generate a complete course outline in JSON format with the following structure:\n"
            '{{\n'
            '  "title": "Course Title",\n'
            '  "description": "Course description (2-3 sentences)",\n'
            '  "target_audience": "string",\n'
            '  "learning_objectives": ["string"],\n'
            '  "modules": [\n'
            '    {{\n'
            '      "title": "Module Title",\n'
            '      "summary": "Module summary",\n'
            '      "lessons": [\n'
            '        {{"title": "Lesson Title", "estimated_minutes": 15}}\n'
            '      ],\n'
            '      "quiz_questions": [\n'
            '        {{\n'
            '          "question": "string",\n'
            '          "options": ["string", "string", "string", "string"],\n'
            '          "correct_answer": "string (must be one of options)",\n'
            '          "explanation": "string"\n'
            '        }}\n'
            '      ]\n'
            '    }}\n'
            '  ]\n'
            "}}\n\n"
            "Requirements:\n"
            "- Include {desired_module_count} modules\n"
            "- Each module should have 1-3 lessons\n"
            "- Lesson titles should be specific and actionable\n"
            "- Return ONLY valid JSON, no additional text"
        ),
    ),
    "PT-002": PromptTemplate(
        id="PT-002",
        name="Generate Module Summary",
        template=(
            "You are an expert curriculum designer writing a concise module summary.\n\n"
            "Course Title: {course_title}\n"
            "Module Title: {module_title}\n"
            "Lessons in this module: {lesson_titles}\n"
            "Difficulty Level: {difficulty}\n"
            "Target Audience: {target_audience}\n\n"
            "Write a 2-4 sentence summary paragraph that describes what learners will study "
            "in this module and highlights the key skills or concepts covered.\n\n"
            "Return ONLY valid JSON:\n"
            '{{"summary": "Your 2-4 sentence module summary here"}}\n\n'
            "No additional text outside the JSON object."
        ),
    ),
    "PT-003": PromptTemplate(
        id="PT-003",
        name="Generate Lesson Content",
        template=(
            "You are an expert technical writer creating detailed lesson content for an online learning course.\n\n"
            "Course Title: {course_title}\n"
            "Module Title: {module_title}\n"
            "Lesson Title: {lesson_title}\n"
            "Difficulty Level: {difficulty}\n"
            "Target Audience: {target_audience}\n"
            "Estimated Duration: {estimated_minutes} minutes\n\n"
            "Write comprehensive lesson content in Markdown that:\n"
            "- Opens with a brief introduction\n"
            "- Uses clear headings to organize content\n"
            "- Includes practical examples and step-by-step instructions\n"
            "- Ends with a summary of key takeaways\n\n"
            "Return ONLY valid JSON:\n"
            '{{"markdown_content": "Full lesson content in Markdown", "estimated_minutes": {estimated_minutes}}}\n\n'
            "No additional text outside the JSON object."
        ),
    ),
    "PT-004": PromptTemplate(
        id="PT-004",
        name="Generate Quiz Questions",
        template=(
            "You are an expert instructional designer creating assessment questions.\n\n"
            "Course Title: {course_title}\n"
            "Module Title: {module_title}\n"
            "Lesson Titles covered: {lesson_titles}\n"
            "Difficulty Level: {difficulty}\n"
            "Number of questions: {question_count}\n\n"
            "Generate {question_count} multiple-choice quiz questions with exactly 4 options each.\n\n"
            "Return ONLY valid JSON:\n"
            '{{\n'
            '  "quiz_questions": [\n'
            '    {{\n'
            '      "question": "string",\n'
            '      "options": ["string", "string", "string", "string"],\n'
            '      "correct_answer": "string (must exactly match one of the options)",\n'
            '      "explanation": "string"\n'
            '    }}\n'
            '  ]\n'
            "}}\n\n"
            "Return ONLY valid JSON, no additional text."
        ),
    ),
    "PT-005": PromptTemplate(
        id="PT-005",
        name="Regenerate Content Section",
        template=(
            "You are an expert curriculum designer improving existing course content.\n\n"
            "Course Title: {course_title}\n"
            "Module Title: {module_title}\n"
            "Section to Regenerate: {section_title}\n"
            "Original Content:\n{original_content}\n\n"
            "Regeneration Instructions: {regeneration_instructions}\n"
            "Target Difficulty Level: {difficulty}\n"
            "Target Audience: {target_audience}\n\n"
            "Rewrite the specified section according to the instructions, maintaining the same "
            "topic scope and learning objectives.\n\n"
            "Return ONLY valid JSON:\n"
            '{{\n'
            '  "markdown_content": "Rewritten section in Markdown",\n'
            '  "estimated_minutes": 15,\n'
            '  "changes_summary": "Brief description of changes made"\n'
            "}}\n\n"
            "No additional text outside the JSON object."
        ),
    ),
}
