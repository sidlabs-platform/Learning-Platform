"""Unit tests for the Progress Tracking service layer.

Traceability:
    BRD-FR-014: Enrollment creation
    BRD-FR-016: Enrollment status transitions
    BRD-FR-017: Progress records
    BRD-FR-019: Course completion percentage
    TASK-021: Progress service
"""

import uuid
from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.progress.enrollment_service import (
    enroll_user,
    get_enrollment,
    get_enrollment_by_id,
    get_user_enrollments,
    update_enrollment_status,
)
from src.progress.progress_service import (
    complete_lesson,
    get_course_progress_summary,
    get_lesson_progress,
    record_lesson_view,
)
from src.progress.schemas import EnrollmentStatus


# ---------------------------------------------------------------------------
# Enrollment service
# ---------------------------------------------------------------------------


async def test_enroll_user_creates_enrollment(
    db_session: AsyncSession, learner_user, published_course
):
    """enroll_user creates an enrollment with status not_started. [BRD-FR-014]"""
    enrollment = await enroll_user(
        user_id=learner_user["user"].id,
        course_id=published_course.id,
        db=db_session,
    )
    await db_session.flush()

    assert enrollment.user_id == learner_user["user"].id
    assert enrollment.course_id == published_course.id
    assert enrollment.status == "not_started"
    assert enrollment.id is not None


async def test_enroll_user_duplicate_raises_400(
    db_session: AsyncSession, learner_user, enrollment
):
    """enroll_user raises 400 for duplicate enrollment. [BRD-FR-014]"""
    with pytest.raises(HTTPException) as exc_info:
        await enroll_user(
            user_id=learner_user["user"].id,
            course_id=enrollment.course_id,
            db=db_session,
        )
    assert exc_info.value.status_code == 400


async def test_get_enrollment_returns_correct_record(
    db_session: AsyncSession, learner_user, enrollment
):
    """get_enrollment returns the enrollment for a user/course pair."""
    found = await get_enrollment(
        learner_user["user"].id, enrollment.course_id, db_session
    )
    assert found is not None
    assert found.id == enrollment.id


async def test_get_enrollment_unknown_pair_returns_none(
    db_session: AsyncSession, learner_user
):
    """get_enrollment returns None when no enrollment exists."""
    result = await get_enrollment(
        learner_user["user"].id,
        "00000000-0000-0000-0000-000000000000",
        db_session,
    )
    assert result is None


async def test_get_enrollment_by_id_returns_correct_record(
    db_session: AsyncSession, enrollment
):
    """get_enrollment_by_id returns the correct enrollment."""
    found = await get_enrollment_by_id(enrollment.id, db_session)
    assert found is not None
    assert found.id == enrollment.id


async def test_get_user_enrollments_returns_all_user_enrollments(
    db_session: AsyncSession, learner_user, enrollment
):
    """get_user_enrollments returns all enrollments for a user."""
    enrollments = await get_user_enrollments(learner_user["user"].id, db_session)
    ids = [e.id for e in enrollments]
    assert enrollment.id in ids


async def test_update_enrollment_status_to_in_progress(
    db_session: AsyncSession, enrollment
):
    """update_enrollment_status transitions to in_progress. [BRD-FR-016]"""
    updated = await update_enrollment_status(
        enrollment.id, EnrollmentStatus.in_progress, db_session
    )
    await db_session.flush()

    assert updated is not None
    assert updated.status == "in_progress"
    assert updated.completed_at is None


async def test_update_enrollment_status_to_completed_sets_completed_at(
    db_session: AsyncSession, enrollment
):
    """Transitioning to completed sets completed_at. [BRD-FR-016]"""
    updated = await update_enrollment_status(
        enrollment.id, EnrollmentStatus.completed, db_session
    )
    await db_session.flush()

    assert updated is not None
    assert updated.status == "completed"
    assert updated.completed_at is not None


async def test_update_enrollment_status_back_to_not_started_clears_completed_at(
    db_session: AsyncSession, enrollment
):
    """Reverting from completed clears completed_at. [BRD-FR-016]"""
    # First complete
    await update_enrollment_status(
        enrollment.id, EnrollmentStatus.completed, db_session
    )
    await db_session.flush()
    # Then back to not_started
    updated = await update_enrollment_status(
        enrollment.id, EnrollmentStatus.not_started, db_session
    )
    await db_session.flush()
    assert updated.completed_at is None


# ---------------------------------------------------------------------------
# Progress recording service
# ---------------------------------------------------------------------------


async def test_record_lesson_view_creates_progress_record(
    db_session: AsyncSession, learner_user, course_with_lesson
):
    """record_lesson_view creates a new ProgressRecord. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]

    record = await record_lesson_view(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        module_id=module.id,
        db=db_session,
    )
    await db_session.flush()

    assert record.user_id == learner_user["user"].id
    assert record.lesson_id == lesson.id
    assert record.completed is False
    assert record.last_viewed_at is not None


async def test_record_lesson_view_updates_existing_record(
    db_session: AsyncSession, learner_user, course_with_lesson
):
    """Second record_lesson_view call updates last_viewed_at. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]

    record1 = await record_lesson_view(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        module_id=module.id,
        db=db_session,
    )
    await db_session.flush()

    record2 = await record_lesson_view(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        module_id=module.id,
        db=db_session,
    )
    await db_session.flush()

    # Same record (same id) should be updated
    assert record1.id == record2.id


async def test_complete_lesson_sets_completed_and_timestamp(
    db_session: AsyncSession, learner_user, course_with_lesson
):
    """complete_lesson marks completed=True and sets completed_at. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]

    # First view the lesson to create a record
    await record_lesson_view(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        module_id=module.id,
        db=db_session,
    )
    await db_session.flush()

    record = await complete_lesson(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        db=db_session,
    )
    await db_session.flush()

    assert record.completed is True
    assert record.completed_at is not None


async def test_complete_lesson_without_prior_view_creates_record(
    db_session: AsyncSession, learner_user, course_with_lesson
):
    """complete_lesson creates a new record if none exists. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]

    record = await complete_lesson(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        db=db_session,
    )
    await db_session.flush()

    assert record is not None
    assert record.completed is True


async def test_complete_lesson_second_call_preserves_completed_at(
    db_session: AsyncSession, learner_user, course_with_lesson
):
    """Second complete call does not change completed_at. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]

    r1 = await complete_lesson(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        db=db_session,
    )
    await db_session.flush()
    ts1 = r1.completed_at

    r2 = await complete_lesson(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        db=db_session,
    )
    await db_session.flush()

    assert r2.completed_at == ts1


async def test_get_lesson_progress_returns_none_when_not_viewed(
    db_session: AsyncSession, learner_user, course_with_lesson
):
    """get_lesson_progress returns None when no record exists."""
    lesson = course_with_lesson["lesson"]
    result = await get_lesson_progress(
        user_id=learner_user["user"].id,
        lesson_id=lesson.id,
        db=db_session,
    )
    assert result is None


async def test_get_course_progress_summary_returns_zero_before_any_activity(
    db_session: AsyncSession, learner_user, enrollment
):
    """get_course_progress_summary returns 0% before any lessons are completed. [BRD-FR-019]"""
    summary = await get_course_progress_summary(
        user_id=learner_user["user"].id,
        course_id=enrollment.course_id,
        db=db_session,
    )

    assert summary.course_id == enrollment.course_id
    assert summary.progress_percentage == 0.0
    assert summary.completed_lessons == 0
