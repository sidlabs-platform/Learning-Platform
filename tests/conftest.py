"""Shared pytest fixtures for the Learning Platform test suite.

Sets up:
- In-memory SQLite async database per test
- FastAPI TestClient using httpx.AsyncClient
- DB session override (dependency injection)
- Convenience fixtures for admin and learner users with auth tokens
- Mock data factories for courses, modules, lessons, quiz questions
"""

import os
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set required environment variables BEFORE importing application modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-characters-long!")
os.environ.setdefault("GITHUB_MODELS_API_KEY", "test-api-key")
os.environ.setdefault("GITHUB_MODELS_ENDPOINT", "https://models.inference.ai.azure.com")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from src.auth.service import create_access_token, hash_password  # noqa: E402
from src.database.base import Base  # noqa: E402
from src.database.session import get_db  # noqa: E402
from src.main import create_app  # noqa: E402

# ---------------------------------------------------------------------------
# In-memory test database
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an in-memory DB session, replacing the production one."""
    async with _TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Session-scoped: create tables once per test session
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_tables():
    """Create all ORM tables in the in-memory database once per session."""
    import src.models  # noqa: F401 – registers all models with Base.metadata
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Per-test: clean all rows so tests are isolated
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def _clean_db():
    """Truncate all tables before each test for isolation."""
    yield
    async with _test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


# ---------------------------------------------------------------------------
# Test application and HTTP client
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def app():
    """Build the FastAPI app with the DB override applied."""
    _app = create_app()
    _app.dependency_overrides[get_db] = _override_get_db
    return _app


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Yield an httpx.AsyncClient wired to the test application."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# DB session fixture for direct DB manipulation in tests
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a raw async DB session for direct row inspection / insertion."""
    async with _TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# User factory helpers
# ---------------------------------------------------------------------------


def _make_user_dict(
    *,
    name: str = "Test User",
    email: str | None = None,
    password: str = "TestPass123!",
    role: str = "learner",
) -> dict[str, Any]:
    uid = str(uuid.uuid4())
    return {
        "id": uid,
        "name": name,
        "email": email or f"user_{uid[:8]}@example.com",
        "hashed_password": hash_password(password),
        "role": role,
        "created_at": datetime.utcnow(),
        "is_active": True,
    }


def _make_token(user_id: str, role: str) -> str:
    return create_access_token(data={"sub": user_id, "role": role})


# ---------------------------------------------------------------------------
# Admin and learner user fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Insert an admin user into the DB and return the ORM row + token."""
    from src.models import User

    data = _make_user_dict(name="Admin User", email="admin@example.com", role="admin")
    user = User(**data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = _make_token(user.id, "admin")
    return {"user": user, "token": token, "password": "TestPass123!"}


@pytest_asyncio.fixture
async def learner_user(db_session: AsyncSession):
    """Insert a learner user into the DB and return the ORM row + token."""
    from src.models import User

    data = _make_user_dict(name="Learner User", email="learner@example.com", role="learner")
    user = User(**data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = _make_token(user.id, "learner")
    return {"user": user, "token": token, "password": "TestPass123!"}


@pytest_asyncio.fixture
async def second_learner_user(db_session: AsyncSession):
    """Insert a second learner user for cross-user isolation tests."""
    from src.models import User

    data = _make_user_dict(name="Other Learner", email="other@example.com", role="learner")
    user = User(**data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = _make_token(user.id, "learner")
    return {"user": user, "token": token}


# ---------------------------------------------------------------------------
# Course / module / lesson / quiz fixture helpers
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def draft_course(db_session: AsyncSession, admin_user):
    """Create a draft course owned by the admin user."""
    from src.models import Course

    course = Course(
        id=str(uuid.uuid4()),
        title="Test Course",
        description="A course for testing.",
        status="draft",
        difficulty="beginner",
        estimated_duration=60,
        tags=["test", "beginner"],
        created_by=admin_user["user"].id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@pytest_asyncio.fixture
async def published_course(db_session: AsyncSession, admin_user):
    """Create a published course owned by the admin user."""
    from src.models import Course

    course = Course(
        id=str(uuid.uuid4()),
        title="Published Course",
        description="A published course for testing.",
        status="published",
        difficulty="intermediate",
        estimated_duration=90,
        tags=["published"],
        created_by=admin_user["user"].id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@pytest_asyncio.fixture
async def course_with_module(db_session: AsyncSession, draft_course):
    """Draft course + one module."""
    from src.models import Module

    module = Module(
        id=str(uuid.uuid4()),
        course_id=draft_course.id,
        title="Module 1",
        summary="First module summary",
        sort_order=0,
        created_at=datetime.utcnow(),
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return {"course": draft_course, "module": module}


@pytest_asyncio.fixture
async def course_with_lesson(db_session: AsyncSession, course_with_module):
    """Draft course + module + one lesson."""
    from src.models import Lesson

    module = course_with_module["module"]
    lesson = Lesson(
        id=str(uuid.uuid4()),
        module_id=module.id,
        title="Lesson 1",
        markdown_content="<p>Hello World</p>",
        estimated_minutes=10,
        sort_order=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)
    return {**course_with_module, "lesson": lesson}


@pytest_asyncio.fixture
async def course_with_quiz(db_session: AsyncSession, course_with_module):
    """Draft course + module + one quiz question."""
    from src.models import QuizQuestion

    module = course_with_module["module"]
    question = QuizQuestion(
        id=str(uuid.uuid4()),
        module_id=module.id,
        question="What is 2 + 2?",
        options=["1", "2", "4", "8"],
        correct_answer="4",
        explanation="Basic arithmetic.",
        created_at=datetime.utcnow(),
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    return {**course_with_module, "question": question}


@pytest_asyncio.fixture
async def enrollment(db_session: AsyncSession, learner_user, published_course):
    """Enrollment of learner_user in published_course."""
    from src.models import Enrollment

    enr = Enrollment(
        id=str(uuid.uuid4()),
        user_id=learner_user["user"].id,
        course_id=published_course.id,
        enrolled_at=datetime.utcnow(),
        status="not_started",
        completed_at=None,
    )
    db_session.add(enr)
    await db_session.commit()
    await db_session.refresh(enr)
    return enr


# ---------------------------------------------------------------------------
# Header helpers
# ---------------------------------------------------------------------------


def auth_headers(token: str) -> dict[str, str]:
    """Return Authorization header dict for the given token."""
    return {"Authorization": f"Bearer {token}"}
