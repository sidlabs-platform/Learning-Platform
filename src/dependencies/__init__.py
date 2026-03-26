"""Dependencies package — FastAPI dependency injection helpers.

Exports:
    get_current_user           — Resolves and validates the JWT Bearer token.
    get_current_active_learner — Permits both learners and admins.
    require_admin              — Restricts access to admin-role users only.

Example::

    from src.dependencies import require_admin, get_current_active_learner
"""

from src.dependencies.rbac import (
    get_current_active_learner,
    get_current_user,
    require_admin,
)

__all__ = [
    "get_current_user",
    "get_current_active_learner",
    "require_admin",
]
