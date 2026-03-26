# Learning Platform MVP

An AI-assisted internal learning platform where **Learners** enrol in and complete
GitHub-focused courses, and **Admins** create and manage content with the help of
GitHub Models (GPT-4o).

---

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.11 |
| [uv](https://docs.astral.sh/uv/) | 0.5+ |

---

## Quick Start

### 1 — Clone & install dependencies

```bash
git clone <repo-url>
cd Learning-Platform

# Install all production + dev dependencies into a managed virtual environment
uv sync
```

Alternatively, with plain pip:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 2 — Configure environment variables

```bash
cp .env.example .env
# Open .env and fill in GITHUB_MODELS_API_KEY and SECRET_KEY at minimum.
```

See `.env.example` for a description of every variable.

### 3 — Initialise the database

```bash
alembic upgrade head
```

### 4 — Start the development server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at <http://localhost:8000>.  
Interactive docs: <http://localhost:8000/docs>

---

## Running Tests

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

---

## Project Structure

```
Learning-Platform/
├── src/
│   ├── main.py                  # FastAPI app entry point
│   ├── config/                  # Settings (pydantic-settings)
│   ├── auth/                    # Authentication & RBAC
│   ├── course_management/       # Courses, modules, lessons, quizzes
│   ├── progress/                # Enrollment & progress tracking
│   ├── ai_generation/           # GitHub Models integration
│   ├── reporting/               # Admin reports & statistics
│   └── frontend/                # Jinja2 page routes
├── tests/                       # pytest test suite
├── docs/                        # SDLC artifacts
├── backlog/                     # Epics, stories, tasks
├── alembic/                     # Database migrations
├── pyproject.toml
└── .env.example
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_MODELS_API_KEY` | Yes | — | GitHub PAT for Models API |
| `GITHUB_MODELS_ENDPOINT` | No | `https://models.inference.ai.azure.com` | Models API base URL |
| `SECRET_KEY` | Yes | — | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | JWT expiry in minutes |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./learning_platform.db` | Async DB URL |
| `ENVIRONMENT` | No | `development` | Runtime environment |
| `CORS_ORIGINS` | No | `http://localhost:8000` | Allowed CORS origins |
| `AI_MAX_RETRIES` | No | `3` | GitHub Models retry limit |
| `AI_REQUEST_TIMEOUT_SECONDS` | No | `60` | GitHub Models request timeout |

---

## License

Internal use only.
