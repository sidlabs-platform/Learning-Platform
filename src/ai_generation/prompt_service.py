"""Prompt rendering service for the Learning Platform MVP.

Provides functions to look up prompt templates from the registry
(:data:`~src.ai_generation.prompt_templates.PROMPT_TEMPLATES`) and render
them with caller-supplied variables.

All external-facing functions raise :class:`fastapi.HTTPException` so that
route handlers can forward errors directly to the HTTP client without
additional try/except wrappers.
"""

import logging
from typing import Any

from fastapi import HTTPException, status

from src.ai_generation.prompt_templates import PROMPT_TEMPLATES, PromptTemplate
from src.sanitize import sanitize_log

logger = logging.getLogger(__name__)


def render_prompt(template_id: str, variables: dict[str, Any]) -> str:
    """Render a registered prompt template with the supplied variables.

    Uses ``str.format(**variables)`` to substitute ``{placeholder}`` tokens in
    the template string.

    Args:
        template_id: The identifier of the template to render (e.g. ``"PT-001"``).
        variables: A mapping of placeholder names to their replacement values.

    Returns:
        The fully rendered prompt string ready for submission to the AI model.

    Raises:
        :class:`fastapi.HTTPException` (404) if *template_id* is not registered
            in :data:`PROMPT_TEMPLATES`.
        :class:`fastapi.HTTPException` (400) if a required placeholder variable
            is missing from *variables*.
    """
    template = _get_template(template_id)
    try:
        rendered = template.template.format(**variables)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required variable for template '{template_id}': {exc}",
        ) from exc

    logger.info("Prompt rendered: template_id=%s variable_keys=%s", sanitize_log(template_id), list(variables.keys()))
    return rendered


def get_available_templates() -> list[dict[str, str]]:
    """Return metadata for all registered prompt templates.

    Returns:
        A list of dicts, each with ``"id"`` and ``"name"`` keys corresponding
        to the registered templates in :data:`PROMPT_TEMPLATES`.
    """
    return [
        {"id": pt.id, "name": pt.name}
        for pt in PROMPT_TEMPLATES.values()
    ]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_template(template_id: str) -> PromptTemplate:
    """Look up a template by ID, raising HTTP 404 if not found.

    Args:
        template_id: The template identifier to look up.

    Returns:
        The matching :class:`~src.ai_generation.prompt_templates.PromptTemplate`.

    Raises:
        :class:`fastapi.HTTPException` (404) if *template_id* is not in
            :data:`PROMPT_TEMPLATES`.
    """
    if template_id not in PROMPT_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{template_id}' not found.",
        )
    return PROMPT_TEMPLATES[template_id]
