# Task: Implement Database Seed Script for 3 Starter Courses

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-007             |
| **Story**    | STORY-003            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5h                   |

## Description

Implement the idempotent seed script `002_seed_starter_courses.py` as an Alembic data migration and standalone `seed.py` module that inserts the three mandatory starter courses — GitHub Foundations, GitHub Advanced Security, and GitHub Actions — each with 5 modules, at least 1 lesson per module, and at least 1 quiz question per course, all with `status=published`.

## Implementation Details

**Files to create/modify:**
- `src/database/migrations/versions/002_seed_starter_courses.py` — Alembic data migration that calls `seed_starter_courses()`
- `src/course_management/seed.py` — `seed_starter_courses(db: AsyncSession)` function with all seed data defined as Python dicts

**Approach:**
Define seed data as Python constants (dicts) at the top of `seed.py`. The function checks if each course already exists by title before inserting (idempotency). Use SQLAlchemy ORM `session.add()` for each entity.

Seed data structure for each course:
```python
GITHUB_FOUNDATIONS = {
    "title": "GitHub Foundations",
    "description": "...",
    "status": "published",
    "difficulty": "beginner",
    "estimated_duration": 120,
    "target_audience": "Developers new to GitHub",
    "learning_objectives": [...],
    "tags": ["github", "git", "foundations"],
    "modules": [
        {
            "title": "Introduction to Git and GitHub",
            "sort_order": 1,
            "lessons": [{"title": "...", "markdown_content": "...", "estimated_minutes": 10}],
            "quiz_questions": [{"question": "...", "options": [...], "correct_answer": "...", "explanation": "..."}]
        },
        # ... 4 more modules
    ]
}
```

Three courses required:
1. **GitHub Foundations** — 5 modules: Introduction to Git and GitHub; Repositories, Branches, and Commits; Pull Requests and Code Reviews; Issues and Project Basics; Collaboration Best Practices
2. **GitHub Advanced Security** — 5 modules: Overview of GHAS; Code Scanning Basics; Secret Scanning; Dependency Review and Dependabot; Security Workflows and Remediation
3. **GitHub Actions** — 5 modules: Introduction to Workflows; Workflow Syntax and Triggers; Jobs, Steps, and Runners; Reusable Workflows and Actions; CI/CD Use Cases and Troubleshooting

## API Changes

N/A — seed data only.

## Data Model Changes

- Inserts seed data into `courses`, `modules`, `lessons`, `quiz_questions` tables

## Dependencies

| Prerequisite Task | Reason                                             |
|-------------------|----------------------------------------------------|
| TASK-006          | Alembic and initial schema migration must exist    |
| TASK-013          | Course management Pydantic models (for type hints in seed validation) |

**Wave:** 4

## Acceptance Criteria

- [ ] `uv run alembic upgrade head` inserts all 3 courses with correct module structures
- [ ] Each of the 3 courses has exactly 5 modules in the correct `sortOrder`
- [ ] Each module has ≥ 1 lesson with non-empty `markdownContent`
- [ ] Each course has ≥ 1 `QuizQuestion`
- [ ] All seeded courses have `status=published` and `isAiGenerated=False`
- [ ] Running the migration twice does not duplicate any records (idempotent)

## Test Requirements

- **Unit tests:** Test `seed_starter_courses()` function with an in-memory SQLite test DB
- **Integration tests:** Verify `GET /api/v1/courses` returns 3 courses after seed
- **Edge cases:** Run seed on DB that already has one of the courses; verify only missing courses are added

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-003        |
| Epic     | EPIC-001         |
| BRD      | BRD-FR-041, BRD-FR-042, BRD-FR-043, BRD-FR-044 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
