"""Unit tests for the Course Management service layer.

Traceability:
    BRD-FR-005: Published course catalog
    BRD-FR-007: Admin publishes course
    BRD-FR-008: Admin unpublishes course
    BRD-FR-009: Course structure
    BRD-FR-011: Lesson creation with sanitisation
    TASK-009: Course service implementation
"""

import uuid
from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.course_management.schemas import (
    CourseCreate,
    CourseUpdate,
    DifficultyLevel,
    LessonCreate,
    ModuleCreate,
    QuizQuestionCreate,
)
from src.course_management import service
from src.models import Course, Module


# ---------------------------------------------------------------------------
# Course CRUD
# ---------------------------------------------------------------------------


async def test_create_course_sets_draft_status(db_session: AsyncSession, admin_user):
    """create_course initialises status to 'draft'. [BRD-FR-007]"""
    course_in = CourseCreate(
        title="New Course",
        description="Test description.",
        difficulty=DifficultyLevel.beginner,
        estimated_duration=60,
        tags=["test"],
    )
    course = await service.create_course(course_in, created_by=admin_user["user"].id, db=db_session)
    await db_session.flush()

    assert course.status == "draft"
    assert course.title == "New Course"
    assert course.created_by == admin_user["user"].id


async def test_get_course_returns_correct_course(db_session: AsyncSession, draft_course):
    """get_course returns the correct course by ID."""
    found = await service.get_course(draft_course.id, db_session)
    assert found is not None
    assert found.id == draft_course.id


async def test_get_course_unknown_id_returns_none(db_session: AsyncSession):
    """get_course returns None for unknown ID."""
    result = await service.get_course("00000000-0000-0000-0000-000000000000", db_session)
    assert result is None


async def test_update_course_applies_partial_update(
    db_session: AsyncSession, draft_course
):
    """update_course only changes provided fields."""
    course_in = CourseUpdate(title="Updated Title")
    updated = await service.update_course(draft_course.id, course_in, db_session)
    await db_session.flush()

    assert updated is not None
    assert updated.title == "Updated Title"
    # Unchanged fields should be preserved
    assert updated.description == draft_course.description


async def test_update_nonexistent_course_returns_none(db_session: AsyncSession):
    """update_course returns None for unknown course ID."""
    result = await service.update_course(
        "00000000-0000-0000-0000-000000000000",
        CourseUpdate(title="Ghost"),
        db_session,
    )
    assert result is None


async def test_delete_course_removes_from_db(db_session: AsyncSession, draft_course):
    """delete_course removes the course record."""
    deleted = await service.delete_course(draft_course.id, db_session)
    await db_session.flush()

    assert deleted is True
    found = await service.get_course(draft_course.id, db_session)
    assert found is None


async def test_delete_nonexistent_course_returns_false(db_session: AsyncSession):
    """delete_course returns False for unknown ID."""
    result = await service.delete_course(
        "00000000-0000-0000-0000-000000000000", db_session
    )
    assert result is False


# ---------------------------------------------------------------------------
# Publish / Unpublish
# ---------------------------------------------------------------------------


async def test_publish_course_changes_status_to_published(
    db_session: AsyncSession, draft_course
):
    """publish_course transitions status to 'published'. [BRD-FR-007]"""
    published = await service.publish_course(draft_course.id, db_session)
    await db_session.flush()

    assert published is not None
    assert published.status == "published"


async def test_publish_already_published_raises_409(
    db_session: AsyncSession, published_course
):
    """publish_course raises HTTPException 409 if already published. [BRD-FR-007]"""
    with pytest.raises(HTTPException) as exc_info:
        await service.publish_course(published_course.id, db_session)
    assert exc_info.value.status_code == 409


async def test_unpublish_course_changes_status_to_draft(
    db_session: AsyncSession, published_course
):
    """unpublish_course transitions status to 'draft'. [BRD-FR-008]"""
    unpublished = await service.unpublish_course(published_course.id, db_session)
    await db_session.flush()

    assert unpublished is not None
    assert unpublished.status == "draft"


async def test_unpublish_draft_course_raises_409(
    db_session: AsyncSession, draft_course
):
    """unpublish_course raises HTTPException 409 if already draft. [BRD-FR-008]"""
    with pytest.raises(HTTPException) as exc_info:
        await service.unpublish_course(draft_course.id, db_session)
    assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------


async def test_list_published_courses_returns_only_published(
    db_session: AsyncSession, draft_course, published_course
):
    """list_published_courses excludes draft courses. [BRD-FR-005]"""
    courses = await service.list_published_courses(db_session)
    ids = [c.id for c in courses]
    assert published_course.id in ids
    assert draft_course.id not in ids


async def test_list_courses_all_statuses_includes_draft(
    db_session: AsyncSession, draft_course, published_course
):
    """list_courses without filter returns all statuses."""
    courses = await service.list_courses(db_session)
    ids = [c.id for c in courses]
    assert draft_course.id in ids
    assert published_course.id in ids


# ---------------------------------------------------------------------------
# Module CRUD
# ---------------------------------------------------------------------------


async def test_create_module_links_to_course(
    db_session: AsyncSession, draft_course
):
    """create_module creates a module linked to the course. [BRD-FR-009]"""
    module_in = ModuleCreate(title="Mod 1", summary="A module.", sort_order=0)
    module = await service.create_module(draft_course.id, module_in, db_session)
    await db_session.flush()

    assert module.course_id == draft_course.id
    assert module.title == "Mod 1"


async def test_create_module_nonexistent_course_raises_404(db_session: AsyncSession):
    """create_module raises 404 for unknown course. [BRD-FR-009]"""
    module_in = ModuleCreate(title="Orphan", summary="No parent.", sort_order=0)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_module(
            "00000000-0000-0000-0000-000000000000", module_in, db_session
        )
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Lesson CRUD with sanitisation
# ---------------------------------------------------------------------------


async def test_create_lesson_sanitises_xss_content(
    db_session: AsyncSession, course_with_module
):
    """create_lesson strips script tags from markdown_content. [BRD-FR-011]"""
    module = course_with_module["module"]
    lesson_in = LessonCreate(
        title="XSS Lesson",
        markdown_content="<script>evil()</script><p>Safe content</p>",
        estimated_minutes=10,
        sort_order=0,
    )
    lesson = await service.create_lesson(module.id, lesson_in, db_session)
    await db_session.flush()

    assert "<script>" not in lesson.markdown_content
    assert "evil()" not in lesson.markdown_content
    assert "<p>Safe content</p>" in lesson.markdown_content


async def test_create_lesson_with_safe_markdown_preserved(
    db_session: AsyncSession, course_with_module
):
    """Safe markdown content is preserved after sanitisation. [BRD-FR-011]"""
    module = course_with_module["module"]
    lesson_in = LessonCreate(
        title="Safe Lesson",
        markdown_content="<h1>Title</h1><p>Paragraph</p><code>code</code>",
        estimated_minutes=5,
        sort_order=0,
    )
    lesson = await service.create_lesson(module.id, lesson_in, db_session)
    await db_session.flush()

    assert "<h1>Title</h1>" in lesson.markdown_content
    assert "<p>Paragraph</p>" in lesson.markdown_content


# ---------------------------------------------------------------------------
# Quiz Question
# ---------------------------------------------------------------------------


async def test_create_quiz_question_links_to_module(
    db_session: AsyncSession, course_with_module
):
    """create_quiz_question creates a question linked to the module. [BRD-FR-012]"""
    module = course_with_module["module"]
    question_in = QuizQuestionCreate(
        question="What is Git?",
        options=["A VCS", "An IDE", "A language", "A cloud service"],
        correct_answer="A VCS",
        explanation="Git is a distributed version control system.",
    )
    question = await service.create_quiz_question(module.id, question_in, db_session)
    await db_session.flush()

    assert question.module_id == module.id
    assert question.correct_answer == "A VCS"
