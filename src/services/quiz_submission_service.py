"""Quiz submission service — handling quiz answer submissions and attempt retrieval.

Provides functions for:
- Submitting quiz answers and recording attempts.
- Retrieving quiz attempts for a user/module.
- Computing quiz scores for a module.
"""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Enrollment, QuizAttempt, QuizQuestion
from src.schemas.progress import QuizAttemptResponse, QuizSubmission
from src.services.completion_service import update_enrollment_on_progress

logger = logging.getLogger(__name__)


async def submit_quiz_answer(
    db: AsyncSession,
    user_id: int,
    course_id: int,
    submission: QuizSubmission,
) -> QuizAttemptResponse:
    """Submit an answer to a quiz question.

    Verifies the question exists, checks correctness, stores the attempt,
    and triggers enrollment status update.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        course_id: Primary key of the course.
        submission: Validated quiz submission payload.

    Returns:
        QuizAttemptResponse with is_correct set appropriately.

    Raises:
        HTTPException: 404 if the quiz question is not found.
    """
    # Verify quiz question exists
    result = await db.execute(
        select(QuizQuestion).where(QuizQuestion.id == submission.quiz_question_id)
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz question {submission.quiz_question_id} not found",
        )

    is_correct = question.correct_answer.strip() == submission.selected_answer.strip()

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_question_id=submission.quiz_question_id,
        selected_answer=submission.selected_answer,
        is_correct=is_correct,
        attempted_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    await db.flush()
    await db.refresh(attempt)

    # Update enrollment status
    await update_enrollment_on_progress(db, user_id, course_id)

    logger.info(
        "Quiz attempt: user=%d question=%d correct=%s",
        user_id, submission.quiz_question_id, is_correct,
    )
    return QuizAttemptResponse.model_validate(attempt)


async def get_quiz_attempts(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> list[QuizAttemptResponse]:
    """Get all quiz attempts for a user in a module.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        module_id: Primary key of the module.

    Returns:
        List of QuizAttemptResponse objects.
    """
    result = await db.execute(
        select(QuizAttempt)
        .join(QuizQuestion, QuizAttempt.quiz_question_id == QuizQuestion.id)
        .where(
            QuizAttempt.user_id == user_id,
            QuizQuestion.module_id == module_id,
        )
        .order_by(QuizAttempt.attempted_at.asc())
    )
    attempts = result.scalars().all()
    return [QuizAttemptResponse.model_validate(a) for a in attempts]


async def get_quiz_score(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> dict:
    """Get quiz score for a module.

    Args:
        db: Active async SQLAlchemy session.
        user_id: Primary key of the learner.
        module_id: Primary key of the module.

    Returns:
        dict with keys: total, correct, score_percentage.
    """
    total_result = await db.execute(
        select(func.count(QuizAttempt.id))
        .join(QuizQuestion, QuizAttempt.quiz_question_id == QuizQuestion.id)
        .where(
            QuizAttempt.user_id == user_id,
            QuizQuestion.module_id == module_id,
        )
    )
    total = total_result.scalar() or 0

    correct_result = await db.execute(
        select(func.count(QuizAttempt.id))
        .join(QuizQuestion, QuizAttempt.quiz_question_id == QuizQuestion.id)
        .where(
            QuizAttempt.user_id == user_id,
            QuizQuestion.module_id == module_id,
            QuizAttempt.is_correct == True,  # noqa: E712
        )
    )
    correct = correct_result.scalar() or 0

    score_percentage = (correct / total * 100.0) if total > 0 else 0.0

    return {
        "total": total,
        "correct": correct,
        "score_percentage": score_percentage,
    }
