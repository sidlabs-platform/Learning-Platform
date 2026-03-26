"""
Progress Tracking API router for the Learning Platform MVP.

Provides endpoints for course enrollment, lesson progress recording,
lesson completion, course progress summaries, and quiz submissions.

All endpoints require learner-level authentication.  The router is mounted
at ``/api/v1/progress`` by :func:`src.main.create_app`.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_learner
from src.database import get_db
from src.models import QuizAttempt, QuizQuestion, User
from src.progress.enrollment_service import (
    enroll_user,
    get_enrollment_by_id,
    get_user_enrollments,
)
from src.progress.progress_service import (
    complete_lesson,
    get_course_progress_summary,
    get_lesson_progress,
    record_lesson_view,
)
from src.progress.schemas import (
    CourseProgressSummary,
    EnrollmentCreate,
    EnrollmentRead,
    ProgressRecordRead,
    QuizAttemptRead,
    QuizSubmission,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helper schema for lesson-view body
# ---------------------------------------------------------------------------


class LessonViewBody(BaseModel):
    """Request body for recording a lesson view."""

    module_id: str


# ---------------------------------------------------------------------------
# Enrollment endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/enroll",
    response_model=EnrollmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in a course",
)
async def enroll_in_course(
    body: EnrollmentCreate,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> EnrollmentRead:
    """Enroll the current authenticated user in a course.

    Accepts a course ID and creates an enrollment record with status
    ``not_started``.  Returns HTTP 400 if the user is already enrolled.

    Args:
        body: Request body containing the ``course_id`` to enroll in.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        The newly created enrollment record.
    """
    enrollment = await enroll_user(
        user_id=current_user.id,
        course_id=body.course_id,
        db=db,
    )
    await db.commit()
    logger.info(
        "User %s enrolled in course %s", current_user.id, body.course_id
    )
    return EnrollmentRead.model_validate(enrollment)


@router.get(
    "/enrollments",
    response_model=list[EnrollmentRead],
    summary="List my enrollments",
)
async def list_enrollments(
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> list[EnrollmentRead]:
    """List all enrollments for the current authenticated user.

    Returns enrollments ordered by ``enrolled_at`` descending.

    Args:
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        A list of enrollment records.
    """
    enrollments = await get_user_enrollments(
        user_id=current_user.id,
        db=db,
    )
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get(
    "/enrollments/{enrollment_id}",
    response_model=EnrollmentRead,
    summary="Get enrollment detail",
)
async def get_enrollment_detail(
    enrollment_id: str,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> EnrollmentRead:
    """Retrieve a single enrollment by its ID.

    Returns HTTP 404 if the enrollment does not exist or does not belong
    to the current user.

    Args:
        enrollment_id: UUID of the enrollment to retrieve.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        The enrollment record.
    """
    enrollment = await get_enrollment_by_id(
        enrollment_id=enrollment_id,
        db=db,
    )
    if enrollment is None or enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found.",
        )
    return EnrollmentRead.model_validate(enrollment)


# ---------------------------------------------------------------------------
# Lesson progress endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/lessons/{lesson_id}/view",
    response_model=ProgressRecordRead,
    summary="Record lesson view",
)
async def record_lesson_view_endpoint(
    lesson_id: str,
    body: LessonViewBody,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> ProgressRecordRead:
    """Record that the current user viewed a lesson.

    Creates or updates a progress record with the current timestamp.

    Args:
        lesson_id: UUID of the lesson being viewed.
        body: Request body containing the ``module_id``.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        The created or updated progress record.
    """
    record = await record_lesson_view(
        user_id=current_user.id,
        lesson_id=lesson_id,
        module_id=body.module_id,
        db=db,
    )
    await db.commit()
    logger.info(
        "User %s viewed lesson %s", current_user.id, lesson_id
    )
    return ProgressRecordRead.model_validate(record)


@router.post(
    "/lessons/{lesson_id}/complete",
    response_model=ProgressRecordRead,
    summary="Complete a lesson",
)
async def complete_lesson_endpoint(
    lesson_id: str,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> ProgressRecordRead:
    """Mark a lesson as completed for the current user.

    If no progress record exists, one is created.  The ``completed_at``
    timestamp is set on first completion and not overwritten on subsequent
    calls (idempotent).

    Args:
        lesson_id: UUID of the lesson to mark complete.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        The updated or created progress record.
    """
    record = await complete_lesson(
        user_id=current_user.id,
        lesson_id=lesson_id,
        db=db,
    )
    await db.commit()
    logger.info(
        "User %s completed lesson %s", current_user.id, lesson_id
    )
    return ProgressRecordRead.model_validate(record)


@router.get(
    "/lessons/{lesson_id}",
    response_model=ProgressRecordRead,
    summary="Get lesson progress",
)
async def get_lesson_progress_endpoint(
    lesson_id: str,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> ProgressRecordRead:
    """Get the current user's progress for a specific lesson.

    Returns HTTP 404 if the user has not viewed the lesson yet.

    Args:
        lesson_id: UUID of the lesson.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        The progress record for the lesson.
    """
    record = await get_lesson_progress(
        user_id=current_user.id,
        lesson_id=lesson_id,
        db=db,
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress record found for this lesson.",
        )
    return ProgressRecordRead.model_validate(record)


# ---------------------------------------------------------------------------
# Course progress endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/courses/{course_id}",
    response_model=CourseProgressSummary,
    summary="Get course progress summary",
)
async def get_course_progress_endpoint(
    course_id: str,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> CourseProgressSummary:
    """Get an aggregate progress summary for the current user in a course.

    Returns total lessons, completed lessons, progress percentage, and
    the current enrollment status.

    Args:
        course_id: UUID of the course.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        A course progress summary object.
    """
    summary = await get_course_progress_summary(
        user_id=current_user.id,
        course_id=course_id,
        db=db,
    )
    return summary


# ---------------------------------------------------------------------------
# Quiz submission endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/quiz",
    response_model=QuizAttemptRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a quiz answer",
)
async def submit_quiz_answer(
    body: QuizSubmission,
    current_user: User = Depends(require_learner),
    db: AsyncSession = Depends(get_db),
) -> QuizAttemptRead:
    """Submit an answer to a quiz question and get immediate feedback.

    Looks up the quiz question, compares the selected answer against the
    correct answer, creates a :class:`~src.models.QuizAttempt` record,
    and returns the result.

    Args:
        body: Request body with ``quiz_question_id`` and ``selected_answer``.
        current_user: The authenticated learner.
        db: Async database session.

    Returns:
        The quiz attempt record including whether the answer was correct.

    Raises:
        :class:`fastapi.HTTPException` (404) if the quiz question is not found.
    """
    # 1. Look up the QuizQuestion
    result = await db.execute(
        select(QuizQuestion).where(QuizQuestion.id == body.quiz_question_id)
    )
    question = result.scalar_one_or_none()

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz question not found.",
        )

    # 2. Evaluate correctness
    is_correct: bool = body.selected_answer == question.correct_answer

    # 3. Create a QuizAttempt record
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        quiz_question_id=body.quiz_question_id,
        selected_answer=body.selected_answer,
        is_correct=is_correct,
        attempted_at=now,
    )
    db.add(attempt)
    await db.commit()

    logger.info(
        "User %s submitted quiz answer for question %s (correct=%s)",
        current_user.id,
        body.quiz_question_id,
        is_correct,
    )
    return QuizAttemptRead.model_validate(attempt)
