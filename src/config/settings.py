"""Application settings module using pydantic-settings v2.

Loads all configuration from environment variables (and optional .env file).
Required fields raise ``ValidationError`` at startup when missing.
The ``get_settings()`` factory is cached via ``@lru_cache`` so a single
``Settings`` instance is reused across the entire application lifetime.
"""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables.

    Required fields (no default) will cause a ``ValidationError`` on startup
    if the corresponding environment variable is absent.  Sensitive fields use
    ``SecretStr`` so that their values are never exposed in ``__repr__`` or
    log output.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------
    # Required fields — application will not start without these
    # ------------------------------------------------------------------

    #: API key for authenticating with the GitHub Models endpoint.
    github_models_api_key: SecretStr

    #: Base URL of the GitHub Models API (e.g. https://models.inference.ai.azure.com).
    github_models_endpoint: str

    #: Secret key used to sign and verify JWT tokens.  Must be at least 32 chars.
    secret_key: SecretStr

    # ------------------------------------------------------------------
    # Optional fields — safe defaults provided for local development
    # ------------------------------------------------------------------

    #: SQLAlchemy async database URL.
    database_url: str = "sqlite+aiosqlite:///./learning_platform.db"

    #: Runtime environment: ``development``, ``staging``, or ``production``.
    environment: str = "development"

    #: Maximum number of retry attempts for GitHub Models API requests.
    ai_max_retries: int = 3

    #: Per-request timeout (seconds) for GitHub Models API calls.
    ai_request_timeout_seconds: int = 60

    #: Comma-separated list of allowed CORS origins.
    cors_origins: str = "http://localhost:8000"

    #: JWT access token lifetime in minutes (default 8 hours).
    access_token_expire_minutes: int = 480

    #: JWT signing algorithm.
    algorithm: str = "HS256"


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application ``Settings`` singleton.

    The instance is constructed once on first call and reused for every
    subsequent call.  In tests, call ``get_settings.cache_clear()`` before
    injecting custom environment variables.
    """
    return Settings()
