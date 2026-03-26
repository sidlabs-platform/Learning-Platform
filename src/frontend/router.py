"""
Frontend page routes — Jinja2 template rendering for the Learning Platform.

Provides GET routes for all user-facing pages: auth (login, register, logout),
learner dashboard, course catalog, course detail, lesson viewer, and quiz.

Data is fetched server-side using service functions (not HTTP API calls) and
passed to Jinja2 templates for rendering.  Authentication is enforced via
``get_current_user``; unauthenticated requests redirect to ``/auth/login``.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, require_admin
from src.course_management.service import (
    get_course,
    get_course_with_modules,
    get_lesson,
    get_module,
    list_courses,
    list_lessons,
    list_published_courses,
)
from src.database import get_db
from src.models import QuizQuestion, User
from src.reporting.service import get_admin_dashboard
from src.progress.enrollment_service import get_enrollment, get_user_enrollments
from src.progress.progress_service import (
    get_course_progress_summary,
    get_lesson_progress,
)
from src.sanitize import is_safe_id

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


# ---------------------------------------------------------------------------
# Helper: get user or None (does not raise)
# ---------------------------------------------------------------------------


async def _get_user_or_none(request: Request, db: AsyncSession):
    """Attempt to extract the current user; return ``None`` on failure."""
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@router.get("/", include_in_schema=False)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Redirect authenticated users to the dashboard, others to login."""
    user = await _get_user_or_none(request, db)
    if user is not None:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/auth/login", status_code=302)


# ---------------------------------------------------------------------------
# Auth pages
# ---------------------------------------------------------------------------


@router.get("/auth/login", include_in_schema=False)
async def login_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Render the login page.  If already authenticated, redirect to dashboard."""
    user = await _get_user_or_none(request, db)
    if user is not None:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "user": None,
    })


@router.get("/auth/register", include_in_schema=False)
async def register_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Render the registration page.  If already authenticated, redirect to dashboard."""
    user = await _get_user_or_none(request, db)
    if user is not None:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "user": None,
    })


@router.get("/auth/logout", include_in_schema=False)
async def logout_page(request: Request):
    """Clear the access_token cookie and redirect to login."""
    response = RedirectResponse(
        url="/auth/login?success=You+have+been+logged+out",
        status_code=302,
    )
    response.delete_cookie(key="access_token")
    return response


# ---------------------------------------------------------------------------
# Learner Dashboard
# ---------------------------------------------------------------------------


@router.get("/dashboard", include_in_schema=False)
async def dashboard_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Render the learner dashboard with enrolled courses and progress."""
    user = await _get_user_or_none(request, db)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    enrollments_raw = await get_user_enrollments(user.id, db)

    enrollment_data = []
    for enrollment in enrollments_raw:
        course = await get_course(enrollment.course_id, db)
        if course is None:
            continue
        progress = await get_course_progress_summary(user.id, course.id, db)
        enrollment_data.append({
            "enrollment": enrollment,
            "course": course,
            "progress": progress,
        })

    return templates.TemplateResponse("learner/dashboard.html", {
        "request": request,
        "user": user,
        "enrollments": enrollment_data,
    })


# ---------------------------------------------------------------------------
# Course Catalog
# ---------------------------------------------------------------------------


@router.get("/catalog", include_in_schema=False)
async def catalog_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Render the course catalog showing all published courses."""
    user = await _get_user_or_none(request, db)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    courses = await list_published_courses(db)

    return templates.TemplateResponse("learner/catalog.html", {
        "request": request,
        "user": user,
        "courses": courses,
    })


# ---------------------------------------------------------------------------
# Course Detail
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}", include_in_schema=False)
async def course_detail_page(
    course_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Render the course detail page with modules, lessons, and progress."""
    user = await _get_user_or_none(request, db)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    course = await get_course_with_modules(course_id, db)
    if course is None:
        return RedirectResponse(url="/catalog?error=Course+not+found", status_code=302)

    # Sort modules and their lessons by sort_order
    modules = sorted(course.modules, key=lambda m: m.sort_order)
    for module in modules:
        module.lessons = sorted(module.lessons, key=lambda l: l.sort_order)

    # Enrollment & progress
    enrollment = await get_enrollment(user.id, course_id, db)
    progress = await get_course_progress_summary(user.id, course_id, db)

    # Build progress map: lesson_id -> completed (bool)
    progress_map: dict[str, bool] = {}
    for module in modules:
        for lesson in module.lessons:
            record = await get_lesson_progress(user.id, lesson.id, db)
            progress_map[lesson.id] = record.completed if record else False

    return templates.TemplateResponse("learner/course_detail.html", {
        "request": request,
        "user": user,
        "course": course,
        "modules": modules,
        "enrollment": enrollment,
        "progress": progress,
        "progress_map": progress_map,
    })


# ---------------------------------------------------------------------------
# Lesson Viewer
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/lessons/{lesson_id}", include_in_schema=False)
async def lesson_viewer_page(
    course_id: str,
    lesson_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Render the lesson content viewer with sidebar navigation."""
    user = await _get_user_or_none(request, db)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    course = await get_course_with_modules(course_id, db)
    if course is None:
        return RedirectResponse(url="/catalog?error=Course+not+found", status_code=302)

    lesson = await get_lesson(lesson_id, db)
    if lesson is None:
        if not is_safe_id(course_id):
            return RedirectResponse(url="/catalog?error=Invalid+course", status_code=302)
        return RedirectResponse(
            url=f"/courses/{course_id}?error=Lesson+not+found",
            status_code=302,
        )

    module = await get_module(lesson.module_id, db)

    # All modules sorted for sidebar
    all_modules = sorted(course.modules, key=lambda m: m.sort_order)
    for m in all_modules:
        m.lessons = sorted(m.lessons, key=lambda l: l.sort_order)

    # Progress map across the full course
    progress_map: dict[str, bool] = {}
    for m in all_modules:
        for l in m.lessons:
            record = await get_lesson_progress(user.id, l.id, db)
            progress_map[l.id] = record.completed if record else False

    # Build a flat list for prev/next navigation
    all_lessons_flat = []
    for m in all_modules:
        for l in m.lessons:
            all_lessons_flat.append(l)

    current_idx = next(
        (i for i, l in enumerate(all_lessons_flat) if l.id == lesson_id), -1
    )
    prev_lesson = all_lessons_flat[current_idx - 1] if current_idx > 0 else None
    next_lesson = (
        all_lessons_flat[current_idx + 1]
        if current_idx < len(all_lessons_flat) - 1
        else None
    )

    # Count completed lessons for progress bar
    total_lessons = len(all_lessons_flat)
    completed_count = sum(1 for v in progress_map.values() if v)

    return templates.TemplateResponse("learner/lesson_viewer.html", {
        "request": request,
        "user": user,
        "course": course,
        "module": module,
        "lesson": lesson,
        "all_modules": all_modules,
        "progress_map": progress_map,
        "prev_lesson": prev_lesson,
        "next_lesson": next_lesson,
        "total_lessons": total_lessons,
        "completed_count": completed_count,
    })


# ---------------------------------------------------------------------------
# Module Quiz
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/modules/{module_id}/quiz", include_in_schema=False)
async def quiz_page(
    course_id: str,
    module_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Render the quiz page for a module (questions without correct answers)."""
    user = await _get_user_or_none(request, db)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    course = await get_course(course_id, db)
    if course is None:
        return RedirectResponse(url="/catalog?error=Course+not+found", status_code=302)

    module = await get_module(module_id, db)
    if module is None:
        if not is_safe_id(course_id):
            return RedirectResponse(url="/catalog?error=Invalid+course", status_code=302)
        return RedirectResponse(
            url=f"/courses/{course_id}?error=Module+not+found",
            status_code=302,
        )

    # Fetch quiz questions — do NOT expose correct_answer to the client
    result = await db.execute(
        select(QuizQuestion).where(QuizQuestion.module_id == module_id)
    )
    questions_raw = list(result.scalars().all())

    questions_data = [
        {
            "id": q.id,
            "question": q.question,
            "options": q.options,
        }
        for q in questions_raw
    ]

    return templates.TemplateResponse("learner/quiz.html", {
        "request": request,
        "user": user,
        "course": course,
        "module": module,
        "questions": questions_data,
    })


# ===========================================================================
# Admin Pages
# ===========================================================================


@router.get("/admin", include_in_schema=False)
async def admin_dashboard_page(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Render the admin dashboard with platform-wide stats and reports."""
    dashboard = await get_admin_dashboard(db)
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": user,
        "dashboard": dashboard,
    })


@router.get("/admin/courses", include_in_schema=False)
async def admin_course_list_page(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Render the admin course management list with all courses."""
    courses = await list_courses(db)
    return templates.TemplateResponse("admin/course_list.html", {
        "request": request,
        "user": user,
        "courses": courses,
    })


@router.get("/admin/courses/new", include_in_schema=False)
async def admin_course_create_page(
    request: Request,
    user: User = Depends(require_admin),
):
    """Render the empty course editor form for creating a new course."""
    return templates.TemplateResponse("admin/course_editor.html", {
        "request": request,
        "user": user,
        "course": None,
        "modules": [],
    })


@router.get("/admin/courses/{course_id}/edit", include_in_schema=False)
async def admin_course_edit_page(
    course_id: str,
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Render the pre-populated course editor form for editing."""
    course = await get_course_with_modules(course_id, db)
    if course is None:
        return RedirectResponse(
            url="/admin/courses?error=Course+not+found", status_code=302,
        )
    modules = sorted(course.modules, key=lambda m: m.sort_order)
    for module in modules:
        module.lessons = sorted(module.lessons, key=lambda l: l.sort_order)
    return templates.TemplateResponse("admin/course_editor.html", {
        "request": request,
        "user": user,
        "course": course,
        "modules": modules,
    })


@router.get("/admin/lessons/{lesson_id}/edit", include_in_schema=False)
async def admin_lesson_edit_page(
    lesson_id: str,
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Render the lesson markdown editor."""
    lesson = await get_lesson(lesson_id, db)
    if lesson is None:
        return RedirectResponse(
            url="/admin/courses?error=Lesson+not+found", status_code=302,
        )
    module = await get_module(lesson.module_id, db)
    course = await get_course(module.course_id, db) if module else None
    return templates.TemplateResponse("admin/lesson_editor.html", {
        "request": request,
        "user": user,
        "lesson": lesson,
        "module": module,
        "course": course,
    })


@router.get("/admin/ai/generate", include_in_schema=False)
async def admin_ai_generate_page(
    request: Request,
    user: User = Depends(require_admin),
):
    """Render the AI content generation page."""
    return templates.TemplateResponse("admin/ai_generate.html", {
        "request": request,
        "user": user,
    })
