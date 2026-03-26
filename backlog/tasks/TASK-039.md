# Task: Implement Frontend Page Router

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-039             |
| **Story**    | STORY-019            |
| **Status**   | To Do                |
| **Assignee** | 5-ui-develop-agent   |
| **Estimate** | 3h                   |

## Description

Implement the `src/frontend/router.py` FastAPI page router that serves all Jinja2 `TemplateResponse` pages for both learner and admin routes. Handles role-based redirects (e.g., `/` → `/login` or `/dashboard`; admin accessing learner pages redirects to admin dashboard).

## Implementation Details

**Files to create/modify:**
- `src/frontend/__init__.py` — empty package marker
- `src/frontend/router.py` — FastAPI APIRouter with all page-level GET route handlers
- `src/main.py` — register `frontend.router`

**Approach:**
```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/templates")
router = APIRouter(tags=["frontend"])

def get_current_user_from_cookie(request: Request) -> dict | None:
    """Try to decode JWT from cookie; return user dict or None."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        return {"id": payload.sub, "role": payload.role}
    except Exception:
        return None

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user_from_cookie(request)
    if user:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user_from_cookie(request)
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login")
    template = "admin/dashboard.html" if user["role"] == "admin" else "learner/dashboard.html"
    return templates.TemplateResponse(template, {"request": request, "user": user})

# ... all other page routes per LLD COMP-007 section 2.2
@router.get("/catalog", response_class=HTMLResponse)
@router.get("/courses/{course_id}", response_class=HTMLResponse)
@router.get("/courses/{course_id}/lessons/{lesson_id}", response_class=HTMLResponse)
@router.get("/courses/{course_id}/modules/{module_id}/quiz", response_class=HTMLResponse)
@router.get("/admin", response_class=HTMLResponse)
@router.get("/admin/courses", response_class=HTMLResponse)
@router.get("/admin/courses/new", response_class=HTMLResponse)
@router.get("/admin/courses/{course_id}/edit", response_class=HTMLResponse)
@router.get("/admin/lessons/{lesson_id}/edit", response_class=HTMLResponse)
@router.get("/admin/ai/generate", response_class=HTMLResponse)
@router.get("/admin/ai/log", response_class=HTMLResponse)
```

## API Changes

| Endpoint                                       | Method | Auth            | Description                        |
|------------------------------------------------|--------|-----------------|------------------------------------|
| `/`                                            | GET    | None (redirect) | Redirect to /login or /dashboard   |
| `/login`                                       | GET    | None            | Login page                         |
| `/dashboard`                                   | GET    | Any auth        | Role-appropriate dashboard         |
| `/catalog`                                     | GET    | Any auth        | Course catalog                     |
| `/courses/{course_id}`                         | GET    | Any auth        | Course detail                      |
| `/courses/{course_id}/lessons/{lesson_id}`     | GET    | Enrolled        | Lesson viewer                      |
| `/admin`                                       | GET    | Admin           | Admin dashboard                    |
| `/admin/courses`                               | GET    | Admin           | Admin course list                  |
| `/admin/ai/generate`                           | GET    | Admin           | AI generation form                 |
| `/admin/ai/log`                                | GET    | Admin           | Generation audit log               |

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                          |
|-------------------|-------------------------------------------------|
| TASK-038          | Base template and static files must exist       |
| TASK-009          | `decode_access_token()` required for cookie check |

**Wave:** 6

## Acceptance Criteria

- [ ] `GET /` redirects to `/login` when unauthenticated
- [ ] `GET /` redirects to `/dashboard` when authenticated
- [ ] `GET /dashboard` serves admin template for admin users
- [ ] `GET /admin/courses` redirects non-admins to `/login` or `/dashboard`
- [ ] All 13 page routes return `200 OK` with correct templates for authenticated users

## Test Requirements

- **Unit tests:** Test redirect logic in `root()` with/without cookie
- **Integration tests:** Test that unauthenticated `/dashboard` redirects to `/login`; test role-based template selection
- **Edge cases:** Expired JWT cookie → redirect to login; Learner accessing `/admin` → redirect to `/dashboard`

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-019        |
| Epic     | EPIC-007         |
| BRD      | BRD-NFR-008      |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
