"""Application settings loaded from environment variables via pydantic-settings."""

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide configuration loaded from environment variables or a .env file.

    Required fields (application will fail to start if missing):
    - github_models_api_key
    - github_models_endpoint
    - secret_key (minimum 32 characters)

    All sensitive fields use ``SecretStr`` to prevent accidental exposure in logs
    or repr output.
    """

    # ------------------------------------------------------------------ #
    # Required — validation error raised at startup if absent             #
    # ------------------------------------------------------------------ #
    github_models_api_key: SecretStr = Field(
        ...,
        description="API key for GitHub Models (GPT-4o).",
    )
    github_models_endpoint: str = Field(
        ...,
        description="Base URL for the GitHub Models inference endpoint.",
    )
    secret_key: SecretStr = Field(
        ...,
        min_length=32,
        description="Secret key used for JWT signing — must be at least 32 chars.",
    )

    # ------------------------------------------------------------------ #
    # Optional — sensible defaults for development                        #
    # ------------------------------------------------------------------ #
    database_url: str = Field(
        default="sqlite+aiosqlite:///./learning_platform.db",
        description="SQLAlchemy async database URL.",
    )
    environment: str = Field(
        default="development",
        description="Deployment environment: development | staging | production.",
    )
    ai_max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts for GitHub Models API calls.",
    )
    ai_request_timeout_seconds: int = Field(
        default=60,
        ge=1,
        description="HTTP timeout (seconds) for GitHub Models API requests.",
    )
    cors_origins: str = Field(
        default="http://localhost:8000",
        description="Comma-separated list of allowed CORS origins.",
    )
    access_token_expire_minutes: int = Field(
        default=480,
        ge=1,
        description="JWT access token lifetime in minutes (default 8 hours).",
    )

    # ------------------------------------------------------------------ #
    # pydantic-settings configuration                                     #
    # ------------------------------------------------------------------ #
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Environment variables take precedence over the .env file.
        case_sensitive=False,
    )

    # ------------------------------------------------------------------ #
    # Convenience helpers                                                  #
    # ------------------------------------------------------------------ #
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        """Normalise environment name to lowercase."""
        return value.lower()

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list, splitting on commas."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """
    Return the application settings singleton.

    Uses ``@lru_cache`` so that the underlying ``Settings`` object is constructed
    only once per process lifetime, keeping env-var reads cheap.
    """
    return Settings()
