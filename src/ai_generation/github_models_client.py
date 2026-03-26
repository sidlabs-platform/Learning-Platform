"""GitHub Models API client for the Learning Platform MVP.

Wraps the GitHub Models chat completions endpoint with:
- Async HTTP calls via ``httpx.AsyncClient``
- Configurable request timeout from ``settings.ai_request_timeout_seconds``
- Exponential backoff retry for 429 (rate limit) and 5xx server errors
- API key never exposed in log output (``SecretStr.get_secret_value()`` used
  only during header construction)

All public functions raise :class:`fastapi.HTTPException` (503) when the AI
service is unavailable after all retry attempts are exhausted.
"""

import asyncio
import logging
from typing import Optional

import httpx
from fastapi import HTTPException, status

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Statuses that are eligible for retry with exponential backoff.
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})


async def generate_content(prompt: str, model: str = "gpt-4o") -> str:
    """Call the GitHub Models chat completions API and return the response text.

    Constructs a single ``/chat/completions`` request with the supplied prompt
    and extracts ``choices[0].message.content`` from the response.

    Args:
        prompt: The full prompt string to send to the model.
        model: The model identifier to use (default: ``"gpt-4o"``).

    Returns:
        The raw text content returned by the model.

    Raises:
        :class:`fastapi.HTTPException` (503) if the request fails with a
            non-retryable status code or an HTTP error.
    """
    settings = get_settings()
    return await _execute_request(prompt=prompt, model=model, settings=settings)


async def generate_with_retry(
    prompt: str,
    model: str = "gpt-4o",
    max_retries: Optional[int] = None,
) -> str:
    """Call the GitHub Models API with exponential backoff retry.

    Retries on HTTP 429 and 5xx responses, waiting ``2^attempt`` seconds
    between attempts.  Stops after *max_retries* attempts (defaults to
    ``settings.ai_max_retries``).

    Args:
        prompt: The full prompt string to send to the model.
        model: The model identifier to use (default: ``"gpt-4o"``).
        max_retries: Override for the maximum retry count.  When ``None``,
            ``settings.ai_max_retries`` is used.

    Returns:
        The raw text content returned by the model.

    Raises:
        :class:`fastapi.HTTPException` (503) if all retry attempts are
            exhausted or the error is non-retryable.
    """
    settings = get_settings()
    effective_max_retries = max_retries if max_retries is not None else settings.ai_max_retries

    last_error: Optional[str] = None

    for attempt in range(effective_max_retries + 1):
        try:
            return await _execute_request(prompt=prompt, model=model, settings=settings)
        except HTTPException as exc:
            # Re-raise immediately if not a retryable service-unavailable error.
            if exc.status_code != status.HTTP_503_SERVICE_UNAVAILABLE:
                raise
            last_error = exc.detail

        if attempt < effective_max_retries:
            wait_seconds = 2 ** attempt
            logger.warning(
                "GitHub Models API unavailable, retrying in %ds (attempt %d/%d)",
                wait_seconds,
                attempt + 1,
                effective_max_retries,
            )
            await asyncio.sleep(wait_seconds)

    logger.error(
        "GitHub Models API failed after %d attempts: %s",
        effective_max_retries + 1,
        last_error,
    )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="AI service unavailable",
    )


# ---------------------------------------------------------------------------
# Internal implementation
# ---------------------------------------------------------------------------


async def _execute_request(prompt: str, model: str, settings) -> str:  # type: ignore[no-untyped-def]
    """Perform a single HTTP request to the GitHub Models completions endpoint.

    Args:
        prompt: The prompt string to send.
        model: The model identifier.
        settings: Application settings instance.

    Returns:
        The ``choices[0].message.content`` string from the response JSON.

    Raises:
        :class:`fastapi.HTTPException` (503) for retryable or unexpected failures.
    """
    headers = {
        "Authorization": f"Bearer {settings.github_models_api_key.get_secret_value()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    endpoint_url = f"{settings.github_models_endpoint.rstrip('/')}/chat/completions"

    logger.info("GitHub Models API request initiated: model=%s", model)

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.ai_request_timeout_seconds)
        ) as client:
            response = await client.post(endpoint_url, headers=headers, json=payload)
    except httpx.TimeoutException:
        logger.error("GitHub Models API request timed out: model=%s", model)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )
    except httpx.RequestError as exc:
        logger.error("GitHub Models API network error: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    if response.status_code == 200:
        try:
            data = response.json()
            content: str = data["choices"][0]["message"]["content"]
            logger.info("GitHub Models API request succeeded: model=%s", model)
            return content
        except (KeyError, IndexError, ValueError) as exc:
            logger.error(
                "GitHub Models API response parse error: %s", type(exc).__name__
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service unavailable",
            ) from exc

    if response.status_code in _RETRYABLE_STATUS_CODES:
        logger.warning(
            "GitHub Models API retryable error: status=%d", response.status_code
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    # Non-retryable client-side error (4xx other than 429).
    logger.error(
        "GitHub Models API unexpected error: status=%d", response.status_code
    )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="AI service unavailable",
    )
