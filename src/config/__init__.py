"""Configuration package — pydantic-settings based application settings.

Exports:
    Settings   — Pydantic ``BaseSettings`` subclass with all env-var fields.
    get_settings — Cached factory that returns the application-wide ``Settings``
                   singleton.  Use this everywhere instead of instantiating
                   ``Settings`` directly.

Example::

    from src.config import get_settings

    settings = get_settings()
    print(settings.environment)
"""

from src.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]

