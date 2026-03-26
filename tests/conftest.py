"""
Shared pytest fixtures for the Learning Platform test suite.

This module provides common fixtures used across all test modules:
- Async test database session
- FastAPI AsyncClient with authentication helpers
- Factory fixtures for creating test users, courses, modules, lessons, etc.

Fixtures defined here are automatically discovered by pytest and available
to all test files without explicit imports.
"""

import pytest


# ---------------------------------------------------------------------------
# Placeholder — fixtures will be populated in subsequent waves as the
# application modules (database, app, auth) are implemented.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio as the async backend for the test session."""
    return "asyncio"
