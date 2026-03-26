"""
Course management API router for the Learning Platform MVP.

Exposes REST endpoints for managing courses, modules, lessons, and quiz
questions.  The prefix ``/api/v1/courses`` is mounted by the main application
in :mod:`src.main`; all paths defined here are relative to that prefix.

Role-based access:

* **Admin** — full CRUD (create, update, delete, publish/unpublish).
* **Learner** — read-only access; course listings are restricted to published
  courses, and quiz question responses omit ``correct_answer``.
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user, require_admin
from src.course_management import service
from src.course_management.module_service import update_module as _update_module
from src.course_management.schemas import (
    CourseCreate,
    CourseRead,
    CourseStatus,
    CourseUpdate,
    LessonCreate,
    LessonRead,
    ModuleCreate,
    ModuleRead,
    ModuleUpdate,
    QuizQuestionCreate,
    QuizQuestionRead,
)
from src.database import get_db
from src.models import QuizQuestion, User

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Course CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course",
)
async def create_course(
    course_in: CourseCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CourseRead:
    """Create a new course in **draft** status.

    Only administrators may create courses.  The ``created_by`` field is
    automatically set to the authenticated admin's user ID.
    """
    course = await service.create_course(course_in, created_by=admin.id, db=db)
    await db.commit()
    logger.info("Admin %s created course %s", admin.id, course.id)
    return CourseRead.model_validate(course)


@router.get(
    "/",
    response_model=list[CourseRead],
    summary="List courses",
)
async def list_courses(
    status_filter: Optional[CourseStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[CourseRead]:
    """List courses with optional filtering and pagination.

    * **Admins** see all courses and may filter by ``status`` query parameter.
    * **Learners** see only published courses (``status`` filter is ignored).
    """
    if current_user.role == "admin":
        courses = await service.list_courses(
            db, status_filter=status_filter, skip=skip, limit=limit,
        )
    else:
        courses = await service.list_published_courses(
            db, skip=skip, limit=limit,
        )
    return [CourseRead.model_validate(c) for c in courses]


@router.get(
    "/{course_id}",
    summary="Get course detail with modules, lessons, and quiz questions",
)
async def get_course_detail(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return the full course tree: course metadata plus nested modules, each
    containing their lessons and quiz questions.

    Accessible by any authenticated user.
    """
    course = await service.get_course_with_modules(course_id, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )

    # Build nested response dict from eagerly loaded relationships.
    modules_data: list[dict[str, Any]] = []
    for module in sorted(course.modules, key=lambda m: m.sort_order):
        lessons_data = [
            LessonRead.model_validate(lesson).model_dump()
            for lesson in sorted(module.lessons, key=lambda ls: ls.sort_order)
        ]
        quiz_data = [
            QuizQuestionRead.model_validate(qq).model_dump()
            for qq in module.quiz_questions
        ]
        module_dict = ModuleRead.model_validate(module).model_dump()
        module_dict["lessons"] = lessons_data
        module_dict["quiz_questions"] = quiz_data
        modules_data.append(module_dict)

    course_dict: dict[str, Any] = CourseRead.model_validate(course).model_dump()
    course_dict["modules"] = modules_data
    return course_dict


@router.patch(
    "/{course_id}",
    response_model=CourseRead,
    summary="Update a course",
)
async def update_course(
    course_id: str,
    course_in: CourseUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CourseRead:
    """Apply a partial update to an existing course.

    Only administrators may update courses.  Only the fields present in the
    request body are modified; all others remain unchanged.
    """
    course = await service.update_course(course_id, course_in, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    await db.commit()
    return CourseRead.model_validate(course)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course",
)
async def delete_course(
    course_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a course and all its child modules, lessons, and quiz questions.

    Only administrators may delete courses.
    """
    deleted = await service.delete_course(course_id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{course_id}/publish",
    response_model=CourseRead,
    summary="Publish a course",
)
async def publish_course(
    course_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CourseRead:
    """Transition a course from **draft** to **published** status.

    Raises **409 Conflict** if the course is already published.
    """
    course = await service.publish_course(course_id, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    await db.commit()
    return CourseRead.model_validate(course)


@router.post(
    "/{course_id}/unpublish",
    response_model=CourseRead,
    summary="Unpublish a course",
)
async def unpublish_course(
    course_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CourseRead:
    """Transition a course from **published** back to **draft** status.

    Raises **409 Conflict** if the course is already in draft.
    """
    course = await service.unpublish_course(course_id, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    await db.commit()
    return CourseRead.model_validate(course)


# ---------------------------------------------------------------------------
# Module CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{course_id}/modules",
    response_model=ModuleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a module within a course",
)
async def create_module(
    course_id: str,
    module_in: ModuleCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ModuleRead:
    """Create a new module inside the specified course.

    The parent course must exist (the service raises 404 otherwise).
    Only administrators may create modules.
    """
    module = await service.create_module(course_id, module_in, db)
    await db.commit()
    return ModuleRead.model_validate(module)


@router.get(
    "/{course_id}/modules",
    response_model=list[ModuleRead],
    summary="List modules for a course",
)
async def list_modules(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[ModuleRead]:
    """List all modules belonging to a course, ordered by ``sort_order``.

    Accessible by any authenticated user.
    """
    course = await service.get_course(course_id, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    modules = await service.list_modules(course_id, db)
    return [ModuleRead.model_validate(m) for m in modules]


@router.patch(
    "/{course_id}/modules/{module_id}",
    response_model=ModuleRead,
    summary="Update a module",
)
async def update_module_endpoint(
    course_id: str,
    module_id: str,
    module_in: ModuleUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ModuleRead:
    """Apply a partial update to an existing module.

    Only administrators may update modules.  The parent course must exist.
    """
    course = await service.get_course(course_id, db)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    module = await _update_module(module_id, module_in, db)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found.",
        )
    await db.commit()
    return ModuleRead.model_validate(module)


# ---------------------------------------------------------------------------
# Lesson CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{course_id}/modules/{module_id}/lessons",
    response_model=LessonRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lesson within a module",
)
async def create_lesson(
    course_id: str,
    module_id: str,
    lesson_in: LessonCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> LessonRead:
    """Create a new lesson inside the specified module.

    The parent module must exist (the service raises 404 otherwise).
    Markdown content is sanitised before persistence to prevent XSS.
    Only administrators may create lessons.
    """
    lesson = await service.create_lesson(module_id, lesson_in, db)
    await db.commit()
    return LessonRead.model_validate(lesson)


@router.get(
    "/{course_id}/modules/{module_id}/lessons",
    response_model=list[LessonRead],
    summary="List lessons for a module",
)
async def list_lessons(
    course_id: str,
    module_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[LessonRead]:
    """List all lessons in a module, ordered by ``sort_order``.

    Accessible by any authenticated user.
    """
    module = await service.get_module(module_id, db)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found.",
        )
    lessons = await service.list_lessons(module_id, db)
    return [LessonRead.model_validate(ls) for ls in lessons]


@router.get(
    "/{course_id}/modules/{module_id}/lessons/{lesson_id}",
    response_model=LessonRead,
    summary="Get a single lesson",
)
async def get_lesson(
    course_id: str,
    module_id: str,
    lesson_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> LessonRead:
    """Retrieve a single lesson by its ID.

    Accessible by any authenticated user.
    """
    lesson = await service.get_lesson(lesson_id, db)
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found.",
        )
    return LessonRead.model_validate(lesson)


# ---------------------------------------------------------------------------
# Quiz Question CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{course_id}/modules/{module_id}/quiz",
    response_model=QuizQuestionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a quiz question within a module",
)
async def create_quiz_question(
    course_id: str,
    module_id: str,
    question_in: QuizQuestionCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> QuizQuestionRead:
    """Create a new multiple-choice quiz question inside the specified module.

    The parent module must exist (the service raises 404 otherwise).
    Only administrators may create quiz questions.
    """
    question = await service.create_quiz_question(module_id, question_in, db)
    await db.commit()
    return QuizQuestionRead.model_validate(question)


@router.get(
    "/{course_id}/modules/{module_id}/quiz",
    summary="List quiz questions for a module",
)
async def list_quiz_questions(
    course_id: str,
    module_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all quiz questions belonging to a module.

    * **Admins** receive the full question payload including
      ``correct_answer``.
    * **Learners** receive the same payload but with ``correct_answer``
      **excluded** to prevent answer leakage.
    """
    module = await service.get_module(module_id, db)
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found.",
        )

    result = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.module_id == module_id)
        .order_by(QuizQuestion.created_at)
    )
    questions = list(result.scalars().all())

    if current_user.role == "admin":
        return [
            QuizQuestionRead.model_validate(q).model_dump()
            for q in questions
        ]

    # Learners: omit correct_answer to prevent cheating.
    return [
        {
            "id": q.id,
            "module_id": q.module_id,
            "question": q.question,
            "options": q.options if isinstance(q.options, list) else [],
            "explanation": q.explanation,
        }
        for q in questions
    ]
