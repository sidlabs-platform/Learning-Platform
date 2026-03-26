"""Quiz question service — CRUD operations for module quiz questions.

Provides all database-backed operations for managing quiz questions:

- Creating, reading, updating, and deleting individual quiz questions.
- Batch-fetching questions for multiple modules at once (used by progress
  and reporting services to avoid N+1 queries).

All functions are ``async`` and accept an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
as their first argument.  Business-logic errors are surfaced as
:class:`~fastapi.HTTPException` instances so they propagate cleanly through
FastAPI route handlers.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import QuizQuestion
from src.schemas.course import QuizQuestionCreate, QuizQuestionUpdate

logger = logging.getLogger(__name__)


async def create_quiz_question(
    db: AsyncSession,
    module_id: int,
    question_in: QuizQuestionCreate,
) -> QuizQuestion:
    """Create a quiz question for a module.

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the parent module.
        question_in: Validated creation payload.

    Returns:
        The newly persisted ``QuizQuestion`` ORM instance.
    """
    question = QuizQuestion(
        module_id=module_id,
        question=question_in.question,
        options=question_in.options,
        correct_answer=question_in.correct_answer,
        explanation=question_in.explanation,
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)
    logger.info(
        "QuizQuestion created: id=%d module_id=%d",
        question.id,
        module_id,
    )
    return question


async def get_quiz_question(
    db: AsyncSession,
    question_id: int,
) -> QuizQuestion:
    """Fetch a quiz question by primary key.

    Args:
        db: Active async SQLAlchemy session.
        question_id: Primary key of the quiz question to retrieve.

    Returns:
        The matching ``QuizQuestion`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no question with the given ID exists.
    """
    result = await db.execute(
        select(QuizQuestion).where(QuizQuestion.id == question_id)
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QuizQuestion {question_id} not found",
        )
    return question


async def list_quiz_questions(
    db: AsyncSession,
    module_id: int,
) -> list[QuizQuestion]:
    """List all quiz questions for a module.

    Args:
        db: Active async SQLAlchemy session.
        module_id: Primary key of the parent module.

    Returns:
        A list of ``QuizQuestion`` ORM instances ordered by creation date
        ascending (may be empty).
    """
    result = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.module_id == module_id)
        .order_by(QuizQuestion.id.asc())
    )
    return list(result.scalars().all())


async def update_quiz_question(
    db: AsyncSession,
    question_id: int,
    question_in: QuizQuestionUpdate,
) -> QuizQuestion:
    """Partially update a quiz question.

    Only fields explicitly set in ``question_in`` are applied (PATCH semantics).

    Args:
        db: Active async SQLAlchemy session.
        question_id: Primary key of the quiz question to update.
        question_in: Validated update payload (all fields optional).

    Returns:
        The updated ``QuizQuestion`` ORM instance.

    Raises:
        HTTPException: 404 Not Found if no question with the given ID exists.
    """
    question = await get_quiz_question(db, question_id)
    update_data = question_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    await db.flush()
    await db.refresh(question)
    logger.info(
        "QuizQuestion updated: id=%d fields=%s",
        question_id,
        list(update_data.keys()),
    )
    return question


async def delete_quiz_question(
    db: AsyncSession,
    question_id: int,
) -> None:
    """Delete a quiz question.

    Args:
        db: Active async SQLAlchemy session.
        question_id: Primary key of the quiz question to delete.

    Raises:
        HTTPException: 404 Not Found if no question with the given ID exists.
    """
    question = await get_quiz_question(db, question_id)
    await db.delete(question)
    await db.flush()
    logger.info("QuizQuestion deleted: id=%d", question_id)


async def get_questions_for_modules(
    db: AsyncSession,
    module_ids: list[int],
) -> list[QuizQuestion]:
    """Batch-fetch all quiz questions belonging to a set of modules.

    This helper avoids N+1 queries when retrieving quiz data for an entire
    course (used by progress and reporting services).

    Args:
        db: Active async SQLAlchemy session.
        module_ids: List of module primary keys to fetch questions for.

    Returns:
        A flat list of ``QuizQuestion`` ORM instances for the given modules.
        Returns an empty list if ``module_ids`` is empty.
    """
    if not module_ids:
        return []
    result = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.module_id.in_(module_ids))
        .order_by(QuizQuestion.module_id.asc(), QuizQuestion.id.asc())
    )
    return list(result.scalars().all())
