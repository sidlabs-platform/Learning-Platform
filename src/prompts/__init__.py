"""Prompts package — AI prompt templates for GitHub Models integration.

Template files are stored as plain-text ``.txt`` files alongside this module.
Use :func:`load_prompt` to retrieve a template by its base filename (without
the ``.txt`` extension).

Available templates:

- ``pt001_course_outline`` — Generate a structured course outline (PT-001)
- ``pt002_module_summary`` — Generate a module summary paragraph (PT-002)
- ``pt003_lesson_content`` — Generate full Markdown lesson content (PT-003)
- ``pt004_quiz_questions`` — Generate multiple-choice quiz questions (PT-004)
- ``pt005_section_regeneration`` — Regenerate a specific content section (PT-005)

Example::

    from src.prompts import load_prompt

    template = load_prompt("pt001_course_outline")
    prompt = template.format(
        topic="GitHub Actions",
        audience="Developers new to CI/CD",
        objectives="- Understand workflows\\n- Create pipelines",
        difficulty="beginner",
    )
"""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(template_name: str) -> str:
    """Load a prompt template by filename (without the ``.txt`` extension).

    Args:
        template_name: The base name of the template file, e.g.
            ``"pt001_course_outline"`` (without the ``.txt`` suffix).

    Returns:
        The raw template string with ``{placeholder}`` variables intact.
        Use Python's :meth:`str.format` to substitute values.

    Raises:
        FileNotFoundError: If no ``.txt`` file with the given name exists in
            the prompts directory.

    Example::

        template = load_prompt("pt001_course_outline")
        prompt = template.format(topic="Git", audience="Beginners", ...)
    """
    path = PROMPTS_DIR / f"{template_name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_name}")
    return path.read_text(encoding="utf-8")

