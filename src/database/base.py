"""SQLAlchemy declarative base and custom type decorators.

All ORM model classes must inherit from ``Base`` defined here so that
``Base.metadata`` aggregates every table for schema creation and Alembic
migrations.
"""

import json
from typing import Any

from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator


class JSONList(TypeDecorator):
    """SQLAlchemy type that persists a ``list[str]`` as a JSON string.

    Stores the value as plain ``TEXT`` in the database.  On read, the JSON
    string is decoded back to a Python list.  ``None`` values are preserved
    as ``None`` (``NULL`` in SQL) — they are *not* coerced to an empty list.

    Usage::

        class MyModel(Base):
            tags: Mapped[list[str]] = mapped_column(JSONList, default=list)
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        """Serialize *value* to a JSON string before writing to the DB."""
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> list[str] | None:
        """Deserialize *value* from the JSON string returned by the DB."""
        if value is None:
            return None
        return json.loads(value)  # type: ignore[no-any-return]


class Base(DeclarativeBase):
    """Shared declarative base class for all ORM models.

    All model classes should inherit from this ``Base`` so that
    ``Base.metadata`` tracks every mapped table.
    """
