# Task: Implement pydantic-settings Configuration Module

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-002             |
| **Story**    | STORY-001            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement the `Settings` class using `pydantic-settings` that loads all configuration from environment variables, validates required secrets at startup, and provides typed access to every configurable value across the application.

## Implementation Details

**Files to create/modify:**
- `src/config/settings.py` — `Settings(BaseSettings)` class with all env var fields
- `src/config/__init__.py` — exports `get_settings()` function and `Settings` class

**Approach:**
Use `pydantic-settings` `BaseSettings` with `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")`. Declare all fields with appropriate types and defaults. Required fields (no default) cause `ValidationError` at startup if missing. Export a `get_settings()` function using `@lru_cache()` for singleton access.

Fields to include:
```python
class Settings(BaseSettings):
    # Required
    github_models_api_key: str
    github_models_endpoint: str
    secret_key: str  # min_length=32
    
    # Optional with defaults
    database_url: str = "sqlite+aiosqlite:///./learning_platform.db"
    environment: str = "development"
    ai_max_retries: int = 3
    ai_request_timeout_seconds: int = 60
    cors_origins: str = "http://localhost:8000"
    access_token_expire_minutes: int = 480
    
    model_config = SettingsConfigDict(env_file=".env", ...)
```

## API Changes

N/A — configuration module only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                              |
|-------------------|-------------------------------------|
| TASK-001          | Project structure must exist first  |

**Wave:** 1

## Acceptance Criteria

- [ ] `from src.config import get_settings; s = get_settings()` works when env vars are set
- [ ] Application raises `ValidationError` on startup if `GITHUB_MODELS_API_KEY`, `GITHUB_MODELS_ENDPOINT`, or `SECRET_KEY` are missing
- [ ] `get_settings()` is cached with `@lru_cache()` — returns same instance on repeated calls
- [ ] `cors_origins` is parseable as a list by splitting on comma
- [ ] No secrets are exposed in `__repr__` or `str()` output (use `SecretStr` for sensitive fields)

## Test Requirements

- **Unit tests:** Test `Settings` instantiation with all required vars; test `ValidationError` on missing required vars
- **Integration tests:** N/A
- **Edge cases:** Test default values when optional vars are absent; test `SecretStr` masking

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-001        |
| Epic     | EPIC-001         |
| BRD      | BRD-NFR-005      |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
