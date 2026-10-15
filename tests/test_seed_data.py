"""Structural checks for the starter course seed data."""

import os

import pytest

# Importing src.seed loads app settings, which require these env vars.
os.environ.setdefault("GITHUB_MODELS_API_KEY", "test-key")
os.environ.setdefault("GITHUB_MODELS_ENDPOINT", "https://models.example.test")
os.environ.setdefault("SECRET_KEY", "x" * 32)

from src.seed import COURSES  # noqa: E402
from src import seed  # noqa: E402
from src.database import Base  # noqa: E402
from src.models import Course, Enrollment, Lesson, ProgressRecord, User  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402


@pytest.mark.parametrize("course", COURSES, ids=lambda c: c["title"])
def test_course_structure(course: dict) -> None:
    """Each course has 3–5 modules, 1–3 lessons per module and valid quiz answers."""
    assert 3 <= len(course["modules"]) <= 5
    assert any(m["quiz_questions"] for m in course["modules"])
    for module in course["modules"]:
        assert 1 <= len(module["lessons"]) <= 3
        for lesson in module["lessons"]:
            assert lesson["markdown_content"].strip()
        for q in module["quiz_questions"]:
            assert q["correct_answer"] in q["options"]


def test_copilot_course_covers_auto_mode_and_hydrafusion() -> None:
    """The GitHub Copilot course teaches Auto mode routing and HydraFusion."""
    course = next(c for c in COURSES if c["title"] == "GitHub Copilot")
    content = " ".join(
        lesson["markdown_content"]
        for module in course["modules"]
        for lesson in module["lessons"]
    )
    for term in ("Auto", "Efficiency", "Balance", "Intelligence", "HydraFusion", "Cascade", "Critique"):
        assert term in content


def test_hydrafusion_safety_and_client_eligibility() -> None:
    """Keep preview safety guarantees and plan eligibility scoped accurately."""
    course = next(c for c in COURSES if c["title"] == "GitHub Copilot")
    overview = course["modules"][1]["lessons"][0]["markdown_content"]
    setup = course["modules"][2]["lessons"][0]["markdown_content"]

    assert "no patch is applied if a workflow is cancelled or fails validation" in overview
    assert "all Copilot plans through Copilot CLI, including Free" in setup
    assert (
        "In VS Code and the GitHub Copilot app, it is available to Copilot Pro, Pro+, "
        "Business, and Enterprise users"
    ) in setup
    assert "an administrator must allow preview features" in setup


@pytest.mark.asyncio
async def test_seed_backfills_courses_without_changing_existing_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Backfill an old catalog once, preserving author edits and learner progress."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def init_test_db() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    monkeypatch.setattr(seed, "init_db", init_test_db)
    monkeypatch.setattr(seed, "AsyncSessionLocal", sessions)
    monkeypatch.setattr(seed, "hash_password", lambda password: "test-hash")
    monkeypatch.setattr(seed, "COURSES", COURSES[:3])
    try:
        await seed.main()
        async with sessions() as db:
            learner = await db.scalar(select(User).where(User.role == "learner"))
            course = await db.scalar(select(Course).limit(1))
            lesson = await db.scalar(select(Lesson).limit(1))
            assert learner is not None and course is not None and lesson is not None
            learner.hashed_password = "changed-password-hash"
            course.description = "Administrator-edited description"
            lesson.markdown_content = "Administrator-edited lesson"
            db.add(Enrollment(user_id=learner.id, course_id=course.id, status="in_progress"))
            db.add(ProgressRecord(
                user_id=learner.id, lesson_id=lesson.id,
                module_id=lesson.module_id, completed=True,
            ))
            await db.commit()

        async def snapshot() -> dict[str, dict[str, dict]]:
            async with sessions() as db:
                return {
                    table.name: {
                        row["id"]: dict(row)
                        for row in (await db.execute(select(table))).mappings()
                    }
                    for table in Base.metadata.sorted_tables
                }

        before = await snapshot()
        monkeypatch.setattr(seed, "COURSES", COURSES)
        await seed.main()
        after = await snapshot()
        for table, rows in before.items():
            for row_id, row in rows.items():
                assert after[table][row_id] == row
        assert len(after["users"]) == 2
        assert len(after["courses"]) == 4
        copilot = next(
            row for row in after["courses"].values() if row["title"] == "GitHub Copilot"
        )
        modules = {
            row["id"] for row in after["modules"].values()
            if row["course_id"] == copilot["id"]
        }
        assert len(modules) == 3
        assert sum(row["module_id"] in modules for row in after["lessons"].values()) == 5
        assert sum(row["module_id"] in modules for row in after["quiz_questions"].values()) == 5
        await seed.main()
        assert await snapshot() == after
    finally:
        await engine.dispose()
