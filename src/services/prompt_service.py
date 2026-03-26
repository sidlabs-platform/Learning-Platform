"""Prompt rendering service — builds LLM prompt strings from templates.

Each function maps a structured request or a set of named parameters onto
one of the five prompt templates stored under ``src/prompts/``:

- :func:`render_course_outline_prompt` — PT-001 full course outline
- :func:`render_module_summary_prompt` — PT-002 module summary paragraph
- :func:`render_lesson_content_prompt` — PT-003 full Markdown lesson
- :func:`render_quiz_questions_prompt` — PT-004 multiple-choice quiz questions
- :func:`render_section_regeneration_prompt` — PT-005 targeted section regeneration

All functions are pure (synchronous) — they load the template from disk and
return the rendered string without any I/O side effects.

Example::

    from src.services.prompt_service import render_course_outline_prompt
    from src.schemas.ai_generation import GenerateCourseRequest

    request = GenerateCourseRequest(
        topic="GitHub Actions",
        audience="junior developers",
        objectives=["Understand CI/CD", "Create workflows"],
        difficulty="beginner",
    )
    prompt = render_course_outline_prompt(request)
"""

from src.prompts import load_prompt
from src.schemas.ai_generation import GenerateCourseRequest, RegenerateSectionRequest


def render_course_outline_prompt(request: GenerateCourseRequest) -> str:
    """Render the PT-001 course outline template with course generation parameters.

    Args:
        request: A validated :class:`~src.schemas.ai_generation.GenerateCourseRequest`
            containing topic, audience, objectives, and difficulty.

    Returns:
        The fully rendered prompt string ready to send to the LLM.
    """
    template = load_prompt("pt001_course_outline")
    objectives_str = "\n".join(f"- {obj}" for obj in request.objectives)
    return template.format(
        topic=request.topic,
        audience=request.audience,
        objectives=objectives_str,
        difficulty=request.difficulty,
    )


def render_module_summary_prompt(
    module_title: str,
    course_title: str,
    audience: str,
) -> str:
    """Render the PT-002 module summary template.

    Args:
        module_title: Title of the module to summarise.
        course_title: Title of the parent course (for context).
        audience: Description of the intended learner audience.

    Returns:
        The fully rendered prompt string.
    """
    template = load_prompt("pt002_module_summary")
    return template.format(
        module_title=module_title,
        course_title=course_title,
        audience=audience,
    )


def render_lesson_content_prompt(
    lesson_title: str,
    module_title: str,
    course_title: str,
    audience: str,
    difficulty: str,
) -> str:
    """Render the PT-003 lesson content template.

    Args:
        lesson_title: Title of the specific lesson.
        module_title: Title of the module the lesson belongs to.
        course_title: Title of the parent course.
        audience: Description of the intended learner audience.
        difficulty: Difficulty level (``beginner``, ``intermediate``, or
            ``advanced``).

    Returns:
        The fully rendered prompt string.
    """
    template = load_prompt("pt003_lesson_content")
    return template.format(
        lesson_title=lesson_title,
        module_title=module_title,
        course_title=course_title,
        audience=audience,
        difficulty=difficulty,
    )


def render_quiz_questions_prompt(
    module_title: str,
    lesson_titles: list[str],
    difficulty: str,
) -> str:
    """Render the PT-004 quiz questions template.

    Args:
        module_title: Title of the module the quiz covers.
        lesson_titles: Ordered list of lesson titles within the module — used
            to scope question content to covered material.
        difficulty: Difficulty level for the quiz questions.

    Returns:
        The fully rendered prompt string.
    """
    template = load_prompt("pt004_quiz_questions")
    lessons_str = "\n".join(f"- {t}" for t in lesson_titles)
    return template.format(
        module_title=module_title,
        lessons=lessons_str,
        difficulty=difficulty,
    )


def render_section_regeneration_prompt(
    request: RegenerateSectionRequest,
    context: dict,
) -> str:
    """Render the PT-005 section regeneration template.

    Args:
        request: A validated :class:`~src.schemas.ai_generation.RegenerateSectionRequest`
            describing which section to regenerate and any additional instructions.
        context: A dictionary of extra template variables required by the
            ``pt005_section_regeneration`` template beyond the three standard
            fields.  Callers **must** supply all placeholders referenced in the
            template, e.g.::

                context = {
                    "course_title": "GitHub Actions",
                    "module_title": "Workflows",
                    "section_title": "Triggers",
                    "original_content": "...",
                }

    Returns:
        The fully rendered prompt string.
    """
    template = load_prompt("pt005_section_regeneration")
    return template.format(
        section_type=request.section_type,
        section_id=request.section_id,
        instructions=request.instructions or "Improve clarity and completeness",
        **context,
    )
