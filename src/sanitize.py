"""Shared sanitization helpers for the Learning Platform.

Provides utility functions to prevent log injection and URL redirection attacks.
"""

import re

# Pre-compiled UUID pattern for URL validation
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def sanitize_log(value: object) -> str:
    """Remove newlines and carriage returns to prevent log injection.

    Args:
        value: Any value destined for a log message.

    Returns:
        A single-line string safe for inclusion in log output.
    """
    return str(value).replace("\n", "").replace("\r", "")


def is_safe_id(value: str) -> bool:
    """Return ``True`` if *value* looks like a valid UUID (safe for URL use).

    Args:
        value: A candidate identifier string.

    Returns:
        ``True`` when *value* matches the UUID-4 hex pattern.
    """
    return bool(_UUID_RE.match(value))
