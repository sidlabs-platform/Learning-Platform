"""GitHub Models API client — async HTTP client for LLM content generation.

Wraps the GitHub Models API (OpenAI-compatible chat completions endpoint) with:

- Configurable model selection and token limits.
- Exponential back-off retry logic for ``429 Too Many Requests`` responses.
- Retry on transient network timeouts.
- Structured logging of request metadata (no sensitive content or API keys).

Usage::

    from src.services.ai_client import AIClient

    client = AIClient()
    response_text = await client.generate_content(
        prompt="Write a course outline for GitHub Actions.",
        model="gpt-4o",
        max_tokens=2048,
    )

The client reads its configuration from :func:`~src.config.get_settings` at
instantiation time — no secrets are passed as arguments.
"""

import asyncio
import logging

import httpx
from fastapi import HTTPException, status

from src.config import get_settings

logger = logging.getLogger(__name__)


class AIClient:
    """Async client for the GitHub Models API (OpenAI-compatible).

    The client is designed to be instantiated once (e.g. at application
    startup or as a FastAPI dependency) and reused across requests.  All
    network I/O is performed inside :meth:`generate_content`, which creates
    a fresh :class:`httpx.AsyncClient` per call to avoid connection-pool
    lifecycle issues in long-running processes.

    Attributes:
        _settings: Cached :class:`~src.config.Settings` instance.
    """

    def __init__(self) -> None:
        """Initialise the client, loading settings from the environment."""
        self._settings = get_settings()

    async def generate_content(
        self,
        prompt: str,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to the GitHub Models API and return the text response.

        Implements exponential back-off on ``429 Too Many Requests`` and on
        transient ``TimeoutException`` failures up to ``ai_max_retries``
        additional attempts (i.e. at most ``ai_max_retries + 1`` total
        attempts are made).

        Args:
            prompt: The user-role prompt string to send to the model.
            model: GitHub Models model identifier (default ``"gpt-4o"``).
            max_tokens: Maximum tokens to generate in the response.

        Returns:
            The generated text content string from the first choice.

        Raises:
            HTTPException: 503 Service Unavailable after exhausting all retries
                due to rate-limiting.
            HTTPException: 502 Bad Gateway for non-retryable HTTP errors from
                the GitHub Models API.
            RuntimeError: Should never be raised in practice — acts as a
                safety net if retry logic is exhausted without raising.
        """
        api_key = self._settings.github_models_api_key.get_secret_value()
        endpoint = self._settings.github_models_endpoint.rstrip("/")
        max_retries: int = self._settings.ai_max_retries
        timeout: int = self._settings.ai_request_timeout_seconds

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }

        logger.info(
            "GitHub Models API request: model=%s max_tokens=%d endpoint=%s",
            model,
            max_tokens,
            endpoint,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(max_retries + 1):
                try:
                    response = await client.post(
                        f"{endpoint}/chat/completions",
                        json=payload,
                        headers=headers,
                    )

                    if response.status_code == 429:
                        wait_seconds = 2**attempt
                        logger.warning(
                            "Rate limited by GitHub Models API, retrying in %ds "
                            "(attempt %d/%d)",
                            wait_seconds,
                            attempt + 1,
                            max_retries + 1,
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(wait_seconds)
                            continue
                        # Exhausted retries on rate limit
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="GitHub Models API is rate-limited. Please retry later.",
                        )

                    response.raise_for_status()
                    data = response.json()
                    content: str = data["choices"][0]["message"]["content"]
                    logger.info(
                        "GitHub Models API response received: model=%s tokens_used=%s",
                        model,
                        data.get("usage", {}).get("total_tokens", "unknown"),
                    )
                    return content

                except httpx.TimeoutException:
                    logger.warning(
                        "GitHub Models API request timed out (attempt %d/%d)",
                        attempt + 1,
                        max_retries + 1,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="GitHub Models API request timed out. Please retry later.",
                    )

                except httpx.HTTPStatusError as exc:
                    logger.error(
                        "GitHub Models API error %d (attempt %d/%d)",
                        exc.response.status_code,
                        attempt + 1,
                        max_retries + 1,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"GitHub Models API returned HTTP {exc.response.status_code}.",
                    )

        # Should never reach here — all paths either return or raise above.
        raise RuntimeError("Exhausted retries calling GitHub Models API")
