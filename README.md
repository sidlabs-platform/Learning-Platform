# Learning Platform MVP

An AI-assisted internal learning platform where **Learners** enroll in and complete GitHub-focused
courses, and **Admins** create and manage course content with AI assistance via the GitHub Models API.

---

## Prerequisites

- **Python 3.11+** — verify with `python --version`
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## Quickstart

### 1. Clone the repository

```bash
git clone <repo-url>
cd Learning-Platform
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values:

| Variable                    | Description                                      | Required |
|-----------------------------|--------------------------------------------------|----------|
| `GITHUB_MODELS_API_KEY`     | GitHub personal access token for Models API      | Yes      |
| `GITHUB_MODELS_ENDPOINT`    | GitHub Models API base URL                       | Yes      |
| `SECRET_KEY`                | Random secret for JWT signing                    | Yes      |
| `DATABASE_URL`              | SQLAlchemy async DB URL (default: SQLite)        | Yes      |
| `ENVIRONMENT`               | `development` / `staging` / `production`         | No       |
| `AI_MAX_RETRIES`            | Max retry attempts for AI API calls (default: 3) | No       |
| `AI_REQUEST_TIMEOUT_SECONDS`| Timeout per AI API call in seconds (default: 60) | No       |
| `CORS_ORIGINS`              | Comma-separated list of allowed CORS origins     | No       |

Generate a strong `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Install dependencies

```bash
uv sync
```

For development dependencies (testing tools):

```bash
uv sync --extra dev
```

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

This creates `learning_platform.db` and seeds the three starter courses:
- GitHub Foundations
- GitHub Advanced Security
- GitHub Actions

### 5. Start the development server

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at **http://localhost:8000**.

---

## Project Structure

```
Learning-Platform/
├── src/                        # Application source code
│   ├── main.py                 # FastAPI app entry point, middleware, router registration
│   ├── config/                 # pydantic-settings configuration
│   │   └── settings.py
│   ├── database/               # SQLAlchemy ORM models, engine, session, migrations
│   │   ├── base.py
│   │   ├── engine.py
│   │   ├── session.py
│   │   ├── models/             # ORM model definitions (one file per entity)
│   │   └── migrations/         # Alembic migration scripts
│   ├── schemas/                # Pydantic v2 request/response schemas
│   ├── routers/                # FastAPI route handlers (thin controllers)
│   ├── services/               # Business logic services
│   │   │                       # (auth, courses, AI generation, progress, reporting)
│   ├── dependencies/           # FastAPI dependency injection helpers
│   ├── utils/                  # Shared utilities and helpers
│   ├── prompts/                # AI prompt templates
│   ├── scripts/                # Management scripts (seed, etc.)
│   ├── static/                 # Static assets (CSS, JS)
│   └── templates/              # Jinja2 HTML templates
├── tests/                      # Test suite
│   ├── conftest.py             # Shared pytest fixtures
│   └── ...
├── docs/                       # SDLC artifacts (requirements, design, testing)
├── backlog/                    # Epics, stories, tasks
├── pyproject.toml              # Project metadata and dependencies
├── .env.example                # Environment variable reference
└── README.md                   # This file
```

---

## Running Tests

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

---

## Development Workflow

### API Documentation

FastAPI auto-generates interactive API docs when `ENVIRONMENT=development`:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Creating a Database Migration

After modifying ORM models:

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```

### Default Admin Account

After running migrations and seeding, a default admin account is created:

| Field    | Value                  |
|----------|------------------------|
| Email    | `admin@example.com`    |
| Password | `changeme`             |

> **Important**: Change the default admin password immediately in any non-development environment.

---

## Environment Overview

| Service              | Technology                       |
|----------------------|----------------------------------|
| Backend Framework    | FastAPI (Python 3.11+)           |
| Database             | SQLite via SQLAlchemy async      |
| AI Integration       | GitHub Models API (GPT-4o)       |
| Auth                 | JWT (HTTP-only cookies)          |
| Frontend             | Jinja2 + Vanilla HTML/CSS/JS     |
| Testing              | pytest + httpx + respx           |

---

## Contributing

1. Read `.github/copilot-instructions.md` for coding standards.
2. All tasks are tracked in `backlog/tasks/`.
3. Every code change must trace back to a BRD requirement (`BRD-xxx`).
4. Run `pytest` and ensure all tests pass before opening a PR.
