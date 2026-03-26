"""Course management router — full REST API for courses, modules, lessons, and quizzes.

Provides endpoints for:
- Course CRUD (admin write, authenticated read)
- Module CRUD (admin write, authenticated read)
- Lesson CRUD (admin write, authenticated read)
- Quiz question CRUD (admin write, authenticated read)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies.rbac import get_current_active_learner, require_admin
from src.schemas.course import (
    CatalogResponse,
    CourseCreate,
    CourseDetailResponse,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
    LessonCreate,
    LessonResponse,
    LessonUpdate,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
    QuizQuestionCreate,
    QuizQuestionResponse,
    QuizQuestionUpdate,
)
from src.services.course_service import (
    create_course,
    delete_course,
    get_catalog,
    get_course,
    get_course_detail,
    list_courses,
    publish_course,
    unpublish_course,
    update_course,
)
from src.services.lesson_service import (
    create_lesson,
    create_module,
    delete_lesson,
    delete_module,
    get_lesson,
    get_module,
    list_lessons,
    list_modules,
    update_lesson,
    update_module,
)
from src.services.quiz_service import (
    create_quiz_question,
    delete_quiz_question,
    get_quiz_question,
    list_quiz_questions,
    update_quiz_question,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


# ---------------------------------------------------------------------------
# Course CRUD
# ---------------------------------------------------------------------------


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(
    course_in: CourseCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> CourseResponse:
    """Create a new course (admin only)."""
    course = await create_course(db, course_in, created_by=admin.id)
    await db.commit()
    await db.refresh(course)
    return course


@router.get("/catalog", response_model=list[CatalogResponse])
async def get_catalog_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> list[CatalogResponse]:
    """Get all published courses for the catalog (authenticated learners)."""
    return await get_catalog(db)


@router.get("", response_model=list[CourseResponse])
async def list_courses_endpoint(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> list[CourseResponse]:
    """List all courses with optional status filter (admin only)."""
    return await list_courses(db, status_filter=status_filter)


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course_endpoint(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> CourseDetailResponse:
    """Get full course detail (authenticated)."""
    return await get_course_detail(db, course_id)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course_endpoint(
    course_id: int,
    course_in: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> CourseResponse:
    """Update a course (admin only)."""
    course = await update_course(db, course_id, course_in)
    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_endpoint(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> None:
    """Delete a course (admin only)."""
    await delete_course(db, course_id)
    await db.commit()


@router.post("/{course_id}/publish", response_model=CourseResponse)
async def publish_course_endpoint(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> CourseResponse:
    """Publish a course (admin only)."""
    course = await publish_course(db, course_id)
    await db.commit()
    await db.refresh(course)
    return course


@router.post("/{course_id}/unpublish", response_model=CourseResponse)
async def unpublish_course_endpoint(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> CourseResponse:
    """Unpublish a course (admin only)."""
    course = await unpublish_course(db, course_id)
    await db.commit()
    await db.refresh(course)
    return course


# ---------------------------------------------------------------------------
# Module CRUD
# ---------------------------------------------------------------------------


@router.post("/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module_endpoint(
    course_id: int,
    module_in: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> ModuleResponse:
    """Create a module within a course (admin only)."""
    module = await create_module(db, course_id, module_in)
    await db.commit()
    await db.refresh(module)
    return module


@router.get("/{course_id}/modules", response_model=list[ModuleResponse])
async def list_modules_endpoint(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> list[ModuleResponse]:
    """List modules for a course (authenticated)."""
    return await list_modules(db, course_id)


@router.get("/{course_id}/modules/{module_id}", response_model=ModuleResponse)
async def get_module_endpoint(
    course_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> ModuleResponse:
    """Get a module (authenticated)."""
    return await get_module(db, module_id)


@router.put("/{course_id}/modules/{module_id}", response_model=ModuleResponse)
async def update_module_endpoint(
    course_id: int,
    module_id: int,
    module_in: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> ModuleResponse:
    """Update a module (admin only)."""
    module = await update_module(db, module_id, module_in)
    await db.commit()
    await db.refresh(module)
    return module


@router.delete("/{course_id}/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module_endpoint(
    course_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> None:
    """Delete a module (admin only)."""
    await delete_module(db, module_id)
    await db.commit()


# ---------------------------------------------------------------------------
# Lesson CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{course_id}/modules/{module_id}/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lesson_endpoint(
    course_id: int,
    module_id: int,
    lesson_in: LessonCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> LessonResponse:
    """Create a lesson within a module (admin only)."""
    lesson = await create_lesson(db, module_id, lesson_in)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.get("/{course_id}/modules/{module_id}/lessons", response_model=list[LessonResponse])
async def list_lessons_endpoint(
    course_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> list[LessonResponse]:
    """List lessons in a module (authenticated)."""
    return await list_lessons(db, module_id)


@router.get("/{course_id}/modules/{module_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson_endpoint(
    course_id: int,
    module_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> LessonResponse:
    """Get a lesson (authenticated)."""
    return await get_lesson(db, lesson_id)


@router.put("/{course_id}/modules/{module_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson_endpoint(
    course_id: int,
    module_id: int,
    lesson_id: int,
    lesson_in: LessonUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> LessonResponse:
    """Update a lesson (admin only)."""
    lesson = await update_lesson(db, lesson_id, lesson_in)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.delete(
    "/{course_id}/modules/{module_id}/lessons/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lesson_endpoint(
    course_id: int,
    module_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> None:
    """Delete a lesson (admin only)."""
    await delete_lesson(db, lesson_id)
    await db.commit()


# ---------------------------------------------------------------------------
# Quiz question CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{course_id}/modules/{module_id}/quiz",
    response_model=QuizQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz_question_endpoint(
    course_id: int,
    module_id: int,
    question_in: QuizQuestionCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> QuizQuestionResponse:
    """Create a quiz question in a module (admin only)."""
    question = await create_quiz_question(db, module_id, question_in)
    await db.commit()
    await db.refresh(question)
    return question


@router.get("/{course_id}/modules/{module_id}/quiz", response_model=list[QuizQuestionResponse])
async def list_quiz_questions_endpoint(
    course_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_learner),
) -> list[QuizQuestionResponse]:
    """List quiz questions in a module (authenticated)."""
    return await list_quiz_questions(db, module_id)


@router.put(
    "/{course_id}/modules/{module_id}/quiz/{question_id}",
    response_model=QuizQuestionResponse,
)
async def update_quiz_question_endpoint(
    course_id: int,
    module_id: int,
    question_id: int,
    question_in: QuizQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> QuizQuestionResponse:
    """Update a quiz question (admin only)."""
    question = await update_quiz_question(db, question_id, question_in)
    await db.commit()
    await db.refresh(question)
    return question


@router.delete(
    "/{course_id}/modules/{module_id}/quiz/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quiz_question_endpoint(
    course_id: int,
    module_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
) -> None:
    """Delete a quiz question (admin only)."""
    await delete_quiz_question(db, question_id)
    await db.commit()
