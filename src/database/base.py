"""
SQLAlchemy declarative base and shared TypeDecorators for the Learning Platform.

All ORM models must inherit from :class:`Base`.  The :class:`JSONList`
TypeDecorator is used wherever a Python ``list[str]`` must be persisted in a
SQLite ``TEXT`` column as a JSON-encoded string.
"""

import json

from sqlalchemy import Text, TypeDecorator
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Project-wide SQLAlchemy declarative base.

    Every ORM model class must inherit from ``Base`` so that
    ``Base.metadata.create_all()`` discovers the full schema.
    """


class JSONList(TypeDecorator):
    """
    SQLAlchemy TypeDecorator that transparently stores a Python ``list``
    as a JSON string in a ``TEXT`` column.

    Handles ``None`` gracefully — both ``None`` input and an empty string
    stored in the DB are returned as ``[]`` on read.

    Set ``cache_ok = True`` because this decorator has no mutable state
    that would change SQL compilation results.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: list | None, dialect) -> str:
        """Serialise ``list`` → JSON string before writing to the DB."""
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value: str | None, dialect) -> list:
        """Deserialise JSON string → ``list`` after reading from the DB."""
        if not value:
            return []
        return json.loads(value)
