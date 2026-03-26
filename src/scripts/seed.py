"""Database seed script — populates the platform with initial users and courses.

Creates:
- An **admin** user (admin@example.com / Admin1234!)
- A **learner** user (learner@example.com / Learner1234!)
- Three published starter courses with modules, lessons, and quiz questions:
    1. GitHub Foundations (beginner)
    2. GitHub Advanced Security (intermediate)
    3. GitHub Actions (intermediate)

Run directly:
    python -m src.scripts.seed

Or via:
    python src/scripts/seed.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select  # noqa: E402

from src.database import AsyncSessionLocal, Base, engine  # noqa: E402
from src.models import (  # noqa: E402
    Course,
    CourseStatus,
    Lesson,
    Module,
    QuizQuestion,
    User,
    UserRole,
)
from src.services.auth_service import hash_password  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

SEED_COURSES = [
    # ------------------------------------------------------------------
    # 1. GitHub Foundations — beginner
    # ------------------------------------------------------------------
    {
        "title": "GitHub Foundations",
        "description": (
            "A beginner-friendly introduction to GitHub. Learn the core concepts of "
            "Git and GitHub, how to collaborate on projects, manage repositories, "
            "and use essential GitHub features."
        ),
        "difficulty": "beginner",
        "estimated_duration": 120,
        "tags": ["github", "git", "version-control", "beginner"],
        "modules": [
            {
                "title": "Introduction to Git and GitHub",
                "summary": "Understand what Git and GitHub are, and why they matter for modern software development.",
                "sort_order": 1,
                "lessons": [
                    {
                        "title": "What is Version Control?",
                        "markdown_content": (
                            "# What is Version Control?\n\n"
                            "**Version control** is a system that records changes to files over time so "
                            "you can recall specific versions later.\n\n"
                            "## Why Version Control Matters\n\n"
                            "- **Collaboration** — multiple developers can work on the same project simultaneously.\n"
                            "- **History** — every change is tracked with a timestamp and author.\n"
                            "- **Revert** — mistakes can be undone by rolling back to a previous state.\n"
                            "- **Branching** — teams can experiment in isolation without affecting the main codebase.\n\n"
                            "## Git vs GitHub\n\n"
                            "| Concept | Description |\n"
                            "|---------|-------------|\n"
                            "| **Git** | A distributed version control system that runs locally on your machine. |\n"
                            "| **GitHub** | A cloud-hosted platform built on top of Git that adds collaboration features. |\n\n"
                            "## Key Terms\n\n"
                            "- **Repository (repo)** — a directory tracked by Git.\n"
                            "- **Commit** — a snapshot of changes saved to the repository history.\n"
                            "- **Branch** — a parallel line of development.\n"
                            "- **Remote** — a version of the repo hosted on a server (e.g., GitHub).\n\n"
                            "```bash\n"
                            "# Initialise a new Git repository\n"
                            "git init my-project\n"
                            "cd my-project\n"
                            "```\n"
                        ),
                        "estimated_minutes": 10,
                        "sort_order": 1,
                    },
                    {
                        "title": "Creating Your First Repository",
                        "markdown_content": (
                            "# Creating Your First Repository\n\n"
                            "A **repository** is the fundamental unit of GitHub — it stores your project's "
                            "files and their complete revision history.\n\n"
                            "## Creating a Repo on GitHub\n\n"
                            "1. Click the **+** icon in the top-right corner of GitHub.\n"
                            "2. Select **New repository**.\n"
                            "3. Choose a meaningful name (e.g., `hello-world`).\n"
                            "4. Optionally add a description and a `README.md`.\n"
                            "5. Click **Create repository**.\n\n"
                            "## Cloning to Your Machine\n\n"
                            "```bash\n"
                            "# Clone via HTTPS\n"
                            "git clone https://github.com/<username>/hello-world.git\n\n"
                            "# Clone via SSH (requires SSH key setup)\n"
                            "git clone git@github.com:<username>/hello-world.git\n"
                            "```\n\n"
                            "## The Basic Git Workflow\n\n"
                            "```bash\n"
                            "# Stage changes\n"
                            "git add README.md\n\n"
                            "# Commit with a message\n"
                            "git commit -m \"Add README\"\n\n"
                            "# Push to GitHub\n"
                            "git push origin main\n"
                            "```\n\n"
                            "> **Tip:** Write commit messages in the imperative mood — e.g., "
                            "*\"Add feature\"* not *\"Added feature\"*.\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 2,
                    },
                    {
                        "title": "Understanding Branches",
                        "markdown_content": (
                            "# Understanding Branches\n\n"
                            "Branches let you develop features, fix bugs, or safely experiment "
                            "with new ideas **in isolation** from the main codebase.\n\n"
                            "## The Default Branch\n\n"
                            "By convention, the primary branch is called **`main`** (previously `master`).\n\n"
                            "## Branch Lifecycle\n\n"
                            "```bash\n"
                            "# Create and switch to a new branch\n"
                            "git checkout -b feature/my-feature\n\n"
                            "# Make changes, then commit\n"
                            "git add .\n"
                            "git commit -m \"Implement my feature\"\n\n"
                            "# Push the branch to GitHub\n"
                            "git push origin feature/my-feature\n"
                            "```\n\n"
                            "## Merging Changes\n\n"
                            "Once work is complete, open a **Pull Request** (PR) on GitHub to merge "
                            "the feature branch back into `main`.\n\n"
                            "```bash\n"
                            "# After the PR is merged, update your local main\n"
                            "git checkout main\n"
                            "git pull origin main\n\n"
                            "# Delete the feature branch\n"
                            "git branch -d feature/my-feature\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 3,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What is the primary difference between Git and GitHub?",
                        "options": [
                            "Git is a cloud service; GitHub is a local tool.",
                            "Git is a distributed version control system; GitHub is a cloud platform built on Git.",
                            "Git is only for open-source projects; GitHub supports private repos.",
                            "There is no difference — they are the same product.",
                        ],
                        "correct_answer": "Git is a distributed version control system; GitHub is a cloud platform built on Git.",
                        "explanation": (
                            "Git is the underlying version control system that runs on your local machine. "
                            "GitHub is a cloud-hosted service that adds collaboration, code review, and "
                            "CI/CD features on top of Git."
                        ),
                    },
                    {
                        "question": "Which command creates a copy of a remote repository on your local machine?",
                        "options": [
                            "git init",
                            "git pull",
                            "git clone",
                            "git fork",
                        ],
                        "correct_answer": "git clone",
                        "explanation": (
                            "`git clone <url>` downloads the entire repository history and working "
                            "tree to your local machine."
                        ),
                    },
                    {
                        "question": "What is a Git branch?",
                        "options": [
                            "A backup copy of a file.",
                            "A parallel line of development isolated from the main codebase.",
                            "A remote version of the repository.",
                            "A label applied to a specific commit.",
                        ],
                        "correct_answer": "A parallel line of development isolated from the main codebase.",
                        "explanation": (
                            "Branches enable teams to work on features or fixes independently without "
                            "affecting the default branch until the work is reviewed and merged."
                        ),
                    },
                ],
            },
            {
                "title": "Collaborating with Pull Requests",
                "summary": "Learn how to use pull requests to propose, review, and merge code changes.",
                "sort_order": 2,
                "lessons": [
                    {
                        "title": "What is a Pull Request?",
                        "markdown_content": (
                            "# What is a Pull Request?\n\n"
                            "A **Pull Request (PR)** is GitHub's mechanism for proposing changes from "
                            "one branch to another.  It provides a forum for code review before "
                            "changes are merged.\n\n"
                            "## PR Lifecycle\n\n"
                            "1. **Create** — push a branch and open a PR on GitHub.\n"
                            "2. **Review** — team members comment on the diff and request changes.\n"
                            "3. **Iterate** — the author addresses feedback with additional commits.\n"
                            "4. **Merge** — once approved, the PR is merged into the target branch.\n\n"
                            "## Writing a Good PR Description\n\n"
                            "- Explain **what** changed and **why**.\n"
                            "- Link related issues with `Fixes #123`.\n"
                            "- Include screenshots for UI changes.\n"
                            "- Keep PRs small and focused on a single concern.\n\n"
                            "## Merge Strategies\n\n"
                            "| Strategy | Description |\n"
                            "|----------|-------------|\n"
                            "| **Merge commit** | Preserves full history with a merge commit. |\n"
                            "| **Squash and merge** | Combines all commits into one clean commit. |\n"
                            "| **Rebase and merge** | Replays commits linearly, no merge commit. |\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 1,
                    },
                    {
                        "title": "Code Review Best Practices",
                        "markdown_content": (
                            "# Code Review Best Practices\n\n"
                            "Code review is one of the most effective ways to improve code quality "
                            "and share knowledge across a team.\n\n"
                            "## For Reviewers\n\n"
                            "- **Be constructive** — focus on the code, not the author.\n"
                            "- **Ask questions** — `Why was this approach chosen?` opens a dialogue.\n"
                            "- **Approve selectively** — only approve when you're confident in the change.\n"
                            "- **Use suggestions** — GitHub's suggestion feature lets you propose exact diffs.\n\n"
                            "## For Authors\n\n"
                            "- **Respond to all comments** — even if only to say `acknowledged`.\n"
                            "- **Keep PRs small** — smaller PRs are reviewed faster and more thoroughly.\n"
                            "- **Add context** — explain non-obvious decisions in comments.\n\n"
                            "## Using CODEOWNERS\n\n"
                            "A `CODEOWNERS` file automatically assigns reviewers based on the files changed:\n\n"
                            "```\n"
                            "# .github/CODEOWNERS\n"
                            "*.py @python-team\n"
                            "docs/ @docs-team\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 2,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which merge strategy combines all PR commits into a single commit on the target branch?",
                        "options": [
                            "Merge commit",
                            "Squash and merge",
                            "Rebase and merge",
                            "Fast-forward merge",
                        ],
                        "correct_answer": "Squash and merge",
                        "explanation": (
                            "Squash and merge condenses all commits in a PR into one commit, "
                            "keeping the target branch history clean."
                        ),
                    },
                    {
                        "question": "What does a CODEOWNERS file do?",
                        "options": [
                            "Lists all contributors to a repository.",
                            "Automatically assigns reviewers based on the files changed in a PR.",
                            "Restricts who can create branches.",
                            "Defines the repository license.",
                        ],
                        "correct_answer": "Automatically assigns reviewers based on the files changed in a PR.",
                        "explanation": (
                            "CODEOWNERS maps file path patterns to GitHub users or teams who are "
                            "automatically requested as reviewers when a matching file is changed."
                        ),
                    },
                ],
            },
            {
                "title": "GitHub Issues and Project Management",
                "summary": "Use GitHub Issues, labels, and Projects to plan and track work.",
                "sort_order": 3,
                "lessons": [
                    {
                        "title": "Tracking Work with Issues",
                        "markdown_content": (
                            "# Tracking Work with Issues\n\n"
                            "**GitHub Issues** are the primary way to track bugs, feature requests, "
                            "and tasks within a repository.\n\n"
                            "## Anatomy of a Good Issue\n\n"
                            "- **Title** — a concise summary of the problem or request.\n"
                            "- **Description** — steps to reproduce, expected vs actual behaviour, screenshots.\n"
                            "- **Labels** — categorise by type (`bug`, `enhancement`) or priority (`P1`).\n"
                            "- **Assignees** — the person(s) responsible for resolution.\n"
                            "- **Milestone** — group issues by release or sprint.\n\n"
                            "## Issue Templates\n\n"
                            "Store templates in `.github/ISSUE_TEMPLATE/` to guide contributors:\n\n"
                            "```markdown\n"
                            "## Bug Report\n"
                            "**Steps to Reproduce:**\n"
                            "1. ...\n\n"
                            "**Expected:**\n\n"
                            "**Actual:**\n"
                            "```\n\n"
                            "## Closing Issues via PRs\n\n"
                            "Reference an issue in a PR description to auto-close it on merge:\n\n"
                            "```\n"
                            "Fixes #42\n"
                            "Closes #42\n"
                            "Resolves #42\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 1,
                    },
                    {
                        "title": "GitHub Projects and Roadmaps",
                        "markdown_content": (
                            "# GitHub Projects and Roadmaps\n\n"
                            "**GitHub Projects** is a flexible planning tool that integrates directly "
                            "with Issues and Pull Requests.\n\n"
                            "## Project Views\n\n"
                            "| View | Best For |\n"
                            "|------|----------|\n"
                            "| **Board** | Kanban-style task tracking (To Do / In Progress / Done). |\n"
                            "| **Table** | Spreadsheet-like view with custom fields. |\n"
                            "| **Roadmap** | Timeline view for release planning. |\n\n"
                            "## Custom Fields\n\n"
                            "Add custom fields to track story points, priority, target date, "
                            "or any other metadata relevant to your team.\n\n"
                            "## Automations\n\n"
                            "Projects support built-in automations:\n"
                            "- Move items to *In Progress* when a PR is opened.\n"
                            "- Move items to *Done* when a PR is merged.\n"
                            "- Auto-archive completed items after a set number of days.\n"
                        ),
                        "estimated_minutes": 10,
                        "sort_order": 2,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which keyword in a PR description automatically closes a linked issue when the PR is merged?",
                        "options": [
                            "References",
                            "Resolves",
                            "Relates to",
                            "Depends on",
                        ],
                        "correct_answer": "Resolves",
                        "explanation": (
                            "GitHub supports the keywords `Fixes`, `Closes`, and `Resolves` followed by "
                            "an issue number to automatically close the referenced issue when the PR is merged."
                        ),
                    },
                    {
                        "question": "Where should GitHub Issue templates be stored in a repository?",
                        "options": [
                            ".github/ISSUE_TEMPLATE/",
                            "templates/issues/",
                            "docs/issue-templates/",
                            ".github/workflows/",
                        ],
                        "correct_answer": ".github/ISSUE_TEMPLATE/",
                        "explanation": (
                            "GitHub reads issue templates from the `.github/ISSUE_TEMPLATE/` directory "
                            "and presents them as options when a user creates a new issue."
                        ),
                    },
                ],
            },
        ],
    },
    # ------------------------------------------------------------------
    # 2. GitHub Advanced Security — intermediate
    # ------------------------------------------------------------------
    {
        "title": "GitHub Advanced Security",
        "description": (
            "A comprehensive course on using GitHub Advanced Security (GHAS) features "
            "including CodeQL code scanning, secret scanning, and Dependabot to identify "
            "and remediate security vulnerabilities in your repositories."
        ),
        "difficulty": "intermediate",
        "estimated_duration": 150,
        "tags": ["security", "codeql", "dependabot", "secret-scanning", "ghas"],
        "modules": [
            {
                "title": "Introduction to GitHub Advanced Security",
                "summary": "Overview of GHAS features and how they integrate into the developer workflow.",
                "sort_order": 1,
                "lessons": [
                    {
                        "title": "What is GitHub Advanced Security?",
                        "markdown_content": (
                            "# What is GitHub Advanced Security?\n\n"
                            "**GitHub Advanced Security (GHAS)** is a suite of security tools built "
                            "directly into GitHub that help teams find and fix vulnerabilities without "
                            "leaving their workflow.\n\n"
                            "## Core Features\n\n"
                            "| Feature | Purpose |\n"
                            "|---------|--------|\n"
                            "| **Code Scanning** | Analyses source code for security vulnerabilities using CodeQL. |\n"
                            "| **Secret Scanning** | Detects leaked credentials and API keys in the codebase. |\n"
                            "| **Dependabot** | Alerts on vulnerable dependencies and opens automated fix PRs. |\n"
                            "| **Security Overview** | Centralised dashboard for org-wide security posture. |\n\n"
                            "## Availability\n\n"
                            "- Available on **GitHub Enterprise Cloud** and **GitHub Enterprise Server**.\n"
                            "- Free for **public repositories** on GitHub.com.\n"
                            "- Requires **GHAS licence** for private repositories on Enterprise plans.\n\n"
                            "## Security in the SDLC\n\n"
                            "GHAS follows a **shift-left** philosophy — catching security issues "
                            "*during development* rather than after deployment:\n\n"
                            "```\n"
                            "Code → PR → CI → Staging → Production\n"
                            "  ↑           ↑\n"
                            "  CodeQL    Secret Scan\n"
                            "  Dependabot\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 1,
                    },
                    {
                        "title": "Enabling GHAS on a Repository",
                        "markdown_content": (
                            "# Enabling GHAS on a Repository\n\n"
                            "## Repository-Level Setup\n\n"
                            "1. Navigate to **Settings → Security & analysis**.\n"
                            "2. Enable the features you want:\n"
                            "   - Dependency graph\n"
                            "   - Dependabot alerts\n"
                            "   - Dependabot security updates\n"
                            "   - Code scanning\n"
                            "   - Secret scanning\n\n"
                            "## Organisation-Level Rollout\n\n"
                            "Org admins can enable GHAS across all repositories from "
                            "**Organisation Settings → Security → Advanced Security**.\n\n"
                            "## Required Permissions\n\n"
                            "| Action | Required Permission |\n"
                            "|--------|--------------------|\n"
                            "| Enable code scanning | Repository admin |\n"
                            "| View alerts | Write access or above |\n"
                            "| Dismiss alerts | Write access or above |\n\n"
                            "## Default Setup vs Advanced Setup\n\n"
                            "- **Default setup** — GitHub auto-detects languages and configures CodeQL with zero YAML.\n"
                            "- **Advanced setup** — Full control via a `.github/workflows/codeql.yml` file.\n"
                        ),
                        "estimated_minutes": 10,
                        "sort_order": 2,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which GHAS feature automatically opens pull requests to update vulnerable dependencies?",
                        "options": [
                            "Code Scanning",
                            "Secret Scanning",
                            "Dependabot security updates",
                            "Security Overview",
                        ],
                        "correct_answer": "Dependabot security updates",
                        "explanation": (
                            "Dependabot security updates automatically open PRs to bump a vulnerable "
                            "dependency to a non-vulnerable version when an advisory is published."
                        ),
                    },
                    {
                        "question": "GHAS is available for free on which type of repository?",
                        "options": [
                            "All private repositories",
                            "Enterprise repositories only",
                            "Public repositories on GitHub.com",
                            "Any repository with more than 100 stars",
                        ],
                        "correct_answer": "Public repositories on GitHub.com",
                        "explanation": (
                            "GitHub Advanced Security features are available at no cost for public "
                            "repositories. A paid GHAS licence is required for private repositories "
                            "on Enterprise plans."
                        ),
                    },
                ],
            },
            {
                "title": "Code Scanning with CodeQL",
                "summary": "Use CodeQL to find security vulnerabilities and coding errors in your source code.",
                "sort_order": 2,
                "lessons": [
                    {
                        "title": "How CodeQL Works",
                        "markdown_content": (
                            "# How CodeQL Works\n\n"
                            "**CodeQL** is a semantic code analysis engine that treats code as data. "
                            "It builds a queryable database from your source code and runs queries "
                            "to detect vulnerabilities.\n\n"
                            "## The CodeQL Pipeline\n\n"
                            "1. **Extract** — CodeQL builds a relational database from the source code.\n"
                            "2. **Analyse** — Security queries are run against the database.\n"
                            "3. **Report** — Results appear as code scanning alerts on GitHub.\n\n"
                            "## Supported Languages\n\n"
                            "CodeQL supports: C/C++, C#, Go, Java/Kotlin, JavaScript/TypeScript, "
                            "Python, Ruby, Swift.\n\n"
                            "## Default Query Suites\n\n"
                            "| Suite | Description |\n"
                            "|-------|-------------|\n"
                            "| `default` | High-confidence, low-FP queries recommended for CI. |\n"
                            "| `security-extended` | Broader coverage including medium-confidence queries. |\n"
                            "| `security-and-quality` | All security + quality/maintainability queries. |\n\n"
                            "## Example: SQL Injection\n\n"
                            "```python\n"
                            "# Vulnerable — user input flows directly into a SQL query\n"
                            "query = f\"SELECT * FROM users WHERE id = {user_id}\"\n\n"
                            "# Safe — use parameterised queries\n"
                            "query = \"SELECT * FROM users WHERE id = ?\"\n"
                            "cursor.execute(query, (user_id,))\n"
                            "```\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 1,
                    },
                    {
                        "title": "Configuring CodeQL in CI",
                        "markdown_content": (
                            "# Configuring CodeQL in CI\n\n"
                            "## Default Setup\n\n"
                            "Enable code scanning via **Settings → Security & analysis → Code scanning** "
                            "and click **Set up → Default**. GitHub infers the languages and runs "
                            "analysis on every push and pull request.\n\n"
                            "## Advanced Setup (Workflow File)\n\n"
                            "```yaml\n"
                            "# .github/workflows/codeql.yml\n"
                            "name: CodeQL Analysis\n\n"
                            "on:\n"
                            "  push:\n"
                            "    branches: [main]\n"
                            "  pull_request:\n"
                            "    branches: [main]\n"
                            "  schedule:\n"
                            "    - cron: '0 6 * * 1'  # Weekly on Monday at 06:00 UTC\n\n"
                            "jobs:\n"
                            "  analyse:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    permissions:\n"
                            "      security-events: write\n"
                            "    steps:\n"
                            "      - uses: actions/checkout@v4\n"
                            "      - uses: github/codeql-action/init@v3\n"
                            "        with:\n"
                            "          languages: python\n"
                            "          queries: security-extended\n"
                            "      - uses: github/codeql-action/autobuild@v3\n"
                            "      - uses: github/codeql-action/analyze@v3\n"
                            "```\n\n"
                            "## Dismissing False Positives\n\n"
                            "Alerts can be dismissed with a reason (`false positive`, `won't fix`, "
                            "`used in tests`). Dismissals are audited and visible in the security log.\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 2,
                    },
                    {
                        "title": "Triaging Code Scanning Alerts",
                        "markdown_content": (
                            "# Triaging Code Scanning Alerts\n\n"
                            "## The Alert View\n\n"
                            "Navigate to **Security → Code scanning alerts** to see all open findings.\n\n"
                            "## Alert Severity Levels\n\n"
                            "| Severity | CVSS Range | Recommended Action |\n"
                            "|----------|-----------|-------------------|\n"
                            "| Critical | 9.0–10.0 | Fix immediately, block merge |\n"
                            "| High | 7.0–8.9 | Fix before next release |\n"
                            "| Medium | 4.0–6.9 | Schedule for upcoming sprint |\n"
                            "| Low | 0.1–3.9 | Track and fix in backlog |\n\n"
                            "## Best Practices\n\n"
                            "- **Block PRs** with Critical/High alerts using branch protection rules.\n"
                            "- **Review weekly** to keep the alert backlog manageable.\n"
                            "- **Write custom queries** for patterns specific to your codebase.\n"
                            "- **Use SARIF uploads** to integrate third-party scanners.\n"
                        ),
                        "estimated_minutes": 10,
                        "sort_order": 3,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What does CodeQL do during the 'Extract' phase?",
                        "options": [
                            "It downloads dependencies from package registries.",
                            "It builds a relational database from the source code.",
                            "It compiles the code into a binary.",
                            "It deploys the application to a staging environment.",
                        ],
                        "correct_answer": "It builds a relational database from the source code.",
                        "explanation": (
                            "During extraction, CodeQL creates a database that represents the "
                            "semantic structure of the code — control flow, data flow, type information — "
                            "which can then be queried using CodeQL's query language."
                        ),
                    },
                    {
                        "question": "Which CodeQL query suite has the broadest coverage including medium-confidence queries?",
                        "options": [
                            "default",
                            "security-extended",
                            "security-and-quality",
                            "full-scan",
                        ],
                        "correct_answer": "security-extended",
                        "explanation": (
                            "`security-extended` includes the default high-confidence queries plus "
                            "additional medium-confidence queries for broader security coverage."
                        ),
                    },
                    {
                        "question": "Where should you add the CodeQL analysis workflow file?",
                        "options": [
                            "codeql/workflows/",
                            ".github/workflows/",
                            "security/scans/",
                            "src/.github/",
                        ],
                        "correct_answer": ".github/workflows/",
                        "explanation": (
                            "GitHub Actions workflow files — including CodeQL analysis — must be "
                            "placed in the `.github/workflows/` directory of the repository."
                        ),
                    },
                ],
            },
            {
                "title": "Secret Scanning and Dependabot",
                "summary": "Detect leaked secrets and keep dependencies patched with Dependabot.",
                "sort_order": 3,
                "lessons": [
                    {
                        "title": "Secret Scanning",
                        "markdown_content": (
                            "# Secret Scanning\n\n"
                            "**Secret scanning** automatically searches repository content "
                            "for known credential patterns — API keys, tokens, passwords — "
                            "and alerts repository administrators when matches are found.\n\n"
                            "## How It Works\n\n"
                            "1. GitHub partners with 100+ service providers (AWS, Azure, GitHub, etc.).\n"
                            "2. When a commit is pushed, the content is scanned against known patterns.\n"
                            "3. If a match is found, an alert is raised and the provider is optified.\n"
                            "4. The provider can immediately revoke the exposed credential.\n\n"
                            "## Push Protection\n\n"
                            "**Push protection** blocks pushes that contain secrets *before* they "
                            "enter the repository:\n\n"
                            "```bash\n"
                            "# If you accidentally try to push a secret:\n"
                            "remote: Push rejected. Secret detected.\n"
                            "remote: To push anyway (not recommended), use --force.\n"
                            "```\n\n"
                            "## Custom Patterns\n\n"
                            "Define custom regex patterns for proprietary secrets your team uses:\n\n"
                            "```\n"
                            "Pattern name: Internal API Key\n"
                            "Pattern: MY_COMPANY_[A-Z0-9]{32}\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 1,
                    },
                    {
                        "title": "Managing Dependencies with Dependabot",
                        "markdown_content": (
                            "# Managing Dependencies with Dependabot\n\n"
                            "**Dependabot** keeps your dependencies up to date and alerts you to "
                            "known vulnerabilities in packages you depend on.\n\n"
                            "## Dependabot Alerts\n\n"
                            "When a CVE is published for a package in your dependency graph, "
                            "Dependabot raises an alert with:\n"
                            "- Severity level\n"
                            "- Affected version range\n"
                            "- Recommended fix version\n"
                            "- CVSS score and CWE identifiers\n\n"
                            "## Dependabot Security Updates\n\n"
                            "Automatically opens PRs to bump vulnerable dependencies:\n\n"
                            "```yaml\n"
                            "# The PR will update requirements.txt:\n"
                            "# requests==2.28.0 → requests==2.31.0\n"
                            "```\n\n"
                            "## Dependabot Version Updates\n\n"
                            "Configured via `.github/dependabot.yml`:\n\n"
                            "```yaml\n"
                            "version: 2\n"
                            "updates:\n"
                            "  - package-ecosystem: pip\n"
                            "    directory: /\n"
                            "    schedule:\n"
                            "      interval: weekly\n"
                            "    open-pull-requests-limit: 10\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 2,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What does Dependabot push protection do?",
                        "options": [
                            "Prevents pushing code that has failing tests.",
                            "Blocks commits that introduce vulnerable dependencies.",
                            "Blocks pushes that contain secrets before they enter the repository.",
                            "Prevents direct pushes to the main branch.",
                        ],
                        "correct_answer": "Blocks pushes that contain secrets before they enter the repository.",
                        "explanation": (
                            "Push protection is a secret scanning feature (not Dependabot) that "
                            "intercepts pushes containing detected secrets and blocks them before "
                            "they are committed to the repository history."
                        ),
                    },
                    {
                        "question": "Which file configures Dependabot version updates?",
                        "options": [
                            ".github/security.yml",
                            ".github/dependabot.yml",
                            "dependabot.config.json",
                            ".dependabot/config.yml",
                        ],
                        "correct_answer": ".github/dependabot.yml",
                        "explanation": (
                            "Dependabot version updates are configured via `.github/dependabot.yml`, "
                            "where you specify the package ecosystem, directory, and update schedule."
                        ),
                    },
                ],
            },
        ],
    },
    # ------------------------------------------------------------------
    # 3. GitHub Actions — intermediate
    # ------------------------------------------------------------------
    {
        "title": "GitHub Actions",
        "description": (
            "Learn to automate your software development workflows with GitHub Actions. "
            "Build, test, and deploy your code directly from GitHub using powerful "
            "CI/CD pipelines, reusable workflows, and the GitHub Actions Marketplace."
        ),
        "difficulty": "intermediate",
        "estimated_duration": 180,
        "tags": ["ci-cd", "automation", "github-actions", "devops"],
        "modules": [
            {
                "title": "GitHub Actions Fundamentals",
                "summary": "Understand the core concepts and components of GitHub Actions.",
                "sort_order": 1,
                "lessons": [
                    {
                        "title": "Core Concepts: Workflows, Jobs, and Steps",
                        "markdown_content": (
                            "# Core Concepts: Workflows, Jobs, and Steps\n\n"
                            "GitHub Actions automates your software development lifecycle using "
                            "**workflows** defined as YAML files in `.github/workflows/`.\n\n"
                            "## The Hierarchy\n\n"
                            "```\n"
                            "Workflow\n"
                            "└── Job(s)          # runs on a runner\n"
                            "    └── Step(s)     # shell commands or actions\n"
                            "```\n\n"
                            "## Workflows\n\n"
                            "A workflow is a configurable automated process. It is defined in a YAML "
                            "file and triggered by events:\n\n"
                            "```yaml\n"
                            "name: CI\n"
                            "on:\n"
                            "  push:\n"
                            "    branches: [main]\n"
                            "  pull_request:\n"
                            "    branches: [main]\n"
                            "```\n\n"
                            "## Jobs\n\n"
                            "Jobs run in parallel by default on isolated runners:\n\n"
                            "```yaml\n"
                            "jobs:\n"
                            "  build:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    steps:\n"
                            "      - uses: actions/checkout@v4\n"
                            "      - run: echo 'Hello from CI!'\n"
                            "```\n\n"
                            "## Steps\n\n"
                            "Each step is either a shell command (`run`) or a reusable action (`uses`).\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 1,
                    },
                    {
                        "title": "Triggers and Event Filters",
                        "markdown_content": (
                            "# Triggers and Event Filters\n\n"
                            "Workflows are triggered by **events** — things that happen in or to "
                            "your repository.\n\n"
                            "## Common Triggers\n\n"
                            "| Event | Description |\n"
                            "|-------|-------------|\n"
                            "| `push` | Triggered when commits are pushed. |\n"
                            "| `pull_request` | Triggered on PR actions (open, sync, close). |\n"
                            "| `schedule` | Cron-based scheduled runs. |\n"
                            "| `workflow_dispatch` | Manual trigger via UI or API. |\n"
                            "| `release` | Triggered when a release is published. |\n\n"
                            "## Filtering by Branch and Path\n\n"
                            "```yaml\n"
                            "on:\n"
                            "  push:\n"
                            "    branches:\n"
                            "      - main\n"
                            "      - 'release/**'\n"
                            "    paths:\n"
                            "      - 'src/**'\n"
                            "      - '!docs/**'  # exclude docs changes\n"
                            "```\n\n"
                            "## Manual Dispatch with Inputs\n\n"
                            "```yaml\n"
                            "on:\n"
                            "  workflow_dispatch:\n"
                            "    inputs:\n"
                            "      environment:\n"
                            "        description: 'Deploy to'\n"
                            "        required: true\n"
                            "        type: choice\n"
                            "        options: [staging, production]\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 2,
                    },
                    {
                        "title": "Runners: Hosted and Self-Hosted",
                        "markdown_content": (
                            "# Runners: Hosted and Self-Hosted\n\n"
                            "A **runner** is the server that executes the jobs in a workflow.\n\n"
                            "## GitHub-Hosted Runners\n\n"
                            "| Label | OS |\n"
                            "|-------|----|\n"
                            "| `ubuntu-latest` | Ubuntu 22.04 |\n"
                            "| `windows-latest` | Windows Server 2022 |\n"
                            "| `macos-latest` | macOS 14 (M1) |\n\n"
                            "GitHub-hosted runners come pre-installed with common tools and are "
                            "provisioned fresh for each job.\n\n"
                            "## Self-Hosted Runners\n\n"
                            "Run jobs on your own infrastructure for:\n"
                            "- Custom hardware (GPUs, ARM)\n"
                            "- Access to internal network resources\n"
                            "- Specific compliance requirements\n\n"
                            "```yaml\n"
                            "jobs:\n"
                            "  build:\n"
                            "    runs-on: self-hosted  # or a label you assigned\n"
                            "```\n\n"
                            "## Larger Runners (Enterprise)\n\n"
                            "GitHub offers **larger runners** with more CPU/RAM for compute-intensive "
                            "workloads and **GPU runners** for ML/AI tasks.\n"
                        ),
                        "estimated_minutes": 10,
                        "sort_order": 3,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Where must GitHub Actions workflow files be stored?",
                        "options": [
                            ".github/actions/",
                            ".github/workflows/",
                            "workflows/",
                            "actions/",
                        ],
                        "correct_answer": ".github/workflows/",
                        "explanation": (
                            "GitHub Actions discovers workflow YAML files stored in the "
                            "`.github/workflows/` directory of the repository."
                        ),
                    },
                    {
                        "question": "Which event trigger allows a workflow to be started manually from the GitHub UI?",
                        "options": [
                            "workflow_run",
                            "repository_dispatch",
                            "workflow_dispatch",
                            "manual_trigger",
                        ],
                        "correct_answer": "workflow_dispatch",
                        "explanation": (
                            "`workflow_dispatch` enables manual triggering of a workflow from the "
                            "Actions tab in the GitHub UI or via the REST API."
                        ),
                    },
                    {
                        "question": "By default, how do jobs within the same workflow run?",
                        "options": [
                            "Sequentially, in the order they are defined.",
                            "In parallel, on separate runners.",
                            "On the same runner, one after the other.",
                            "Randomly, depending on runner availability.",
                        ],
                        "correct_answer": "In parallel, on separate runners.",
                        "explanation": (
                            "Jobs in a workflow run in parallel by default on independent runners. "
                            "Use `needs:` to introduce sequential dependencies between jobs."
                        ),
                    },
                ],
            },
            {
                "title": "Building CI Pipelines",
                "summary": "Build effective continuous integration pipelines for testing and building your code.",
                "sort_order": 2,
                "lessons": [
                    {
                        "title": "A Complete CI Workflow",
                        "markdown_content": (
                            "# A Complete CI Workflow\n\n"
                            "A typical CI pipeline runs on every pull request to validate that "
                            "changes don't break existing functionality.\n\n"
                            "## Example: Python CI\n\n"
                            "```yaml\n"
                            "name: Python CI\n\n"
                            "on:\n"
                            "  push:\n"
                            "    branches: [main]\n"
                            "  pull_request:\n"
                            "    branches: [main]\n\n"
                            "jobs:\n"
                            "  test:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    strategy:\n"
                            "      matrix:\n"
                            "        python-version: ['3.11', '3.12']\n"
                            "    steps:\n"
                            "      - uses: actions/checkout@v4\n\n"
                            "      - name: Set up Python ${{ matrix.python-version }}\n"
                            "        uses: actions/setup-python@v5\n"
                            "        with:\n"
                            "          python-version: ${{ matrix.python-version }}\n\n"
                            "      - name: Install dependencies\n"
                            "        run: |\n"
                            "          python -m pip install --upgrade pip\n"
                            "          pip install -r requirements.txt\n\n"
                            "      - name: Run tests\n"
                            "        run: pytest --tb=short\n"
                            "```\n\n"
                            "## Matrix Builds\n\n"
                            "The `strategy.matrix` key lets you run the same job across multiple "
                            "combinations of variables (OS, language version, etc.).\n"
                        ),
                        "estimated_minutes": 18,
                        "sort_order": 1,
                    },
                    {
                        "title": "Caching and Artifacts",
                        "markdown_content": (
                            "# Caching and Artifacts\n\n"
                            "## Dependency Caching\n\n"
                            "Cache package manager downloads to speed up workflows:\n\n"
                            "```yaml\n"
                            "- uses: actions/cache@v4\n"
                            "  with:\n"
                            "    path: ~/.cache/pip\n"
                            "    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}\n"
                            "    restore-keys: |\n"
                            "      ${{ runner.os }}-pip-\n"
                            "```\n\n"
                            "## Uploading Artifacts\n\n"
                            "Save build outputs, test reports, or coverage data:\n\n"
                            "```yaml\n"
                            "- name: Upload test results\n"
                            "  uses: actions/upload-artifact@v4\n"
                            "  if: always()  # upload even if tests fail\n"
                            "  with:\n"
                            "    name: test-results\n"
                            "    path: reports/junit.xml\n"
                            "    retention-days: 30\n"
                            "```\n\n"
                            "## Downloading Artifacts\n\n"
                            "Artifacts can be downloaded in subsequent jobs:\n\n"
                            "```yaml\n"
                            "- uses: actions/download-artifact@v4\n"
                            "  with:\n"
                            "    name: test-results\n"
                            "```\n"
                        ),
                        "estimated_minutes": 12,
                        "sort_order": 2,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What does `strategy.matrix` in a GitHub Actions workflow do?",
                        "options": [
                            "Defines environment variables for all jobs.",
                            "Runs the job across multiple combinations of variables.",
                            "Sets the runner operating system.",
                            "Controls job concurrency limits.",
                        ],
                        "correct_answer": "Runs the job across multiple combinations of variables.",
                        "explanation": (
                            "`strategy.matrix` lets you define a matrix of variables (e.g., OS, "
                            "language version) and GitHub Actions automatically creates a job instance "
                            "for each combination."
                        ),
                    },
                    {
                        "question": "What is the `actions/cache` action used for?",
                        "options": [
                            "Storing workflow outputs permanently.",
                            "Caching dependency downloads to speed up workflow runs.",
                            "Encrypting sensitive workflow data.",
                            "Saving Docker layer caches to GitHub Container Registry.",
                        ],
                        "correct_answer": "Caching dependency downloads to speed up workflow runs.",
                        "explanation": (
                            "`actions/cache` caches specified directories (like package manager caches) "
                            "between workflow runs to avoid redundant downloads and speed up CI."
                        ),
                    },
                ],
            },
            {
                "title": "Advanced Workflows and Deployment",
                "summary": "Reusable workflows, environments, secrets, and CD patterns.",
                "sort_order": 3,
                "lessons": [
                    {
                        "title": "Reusable Workflows",
                        "markdown_content": (
                            "# Reusable Workflows\n\n"
                            "**Reusable workflows** allow you to define a workflow once and call it "
                            "from multiple other workflows — eliminating duplication across repositories.\n\n"
                            "## Defining a Reusable Workflow\n\n"
                            "```yaml\n"
                            "# .github/workflows/deploy.yml (in a shared repo)\n"
                            "on:\n"
                            "  workflow_call:\n"
                            "    inputs:\n"
                            "      environment:\n"
                            "        required: true\n"
                            "        type: string\n"
                            "    secrets:\n"
                            "      deploy_key:\n"
                            "        required: true\n\n"
                            "jobs:\n"
                            "  deploy:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    steps:\n"
                            "      - run: echo \"Deploying to ${{ inputs.environment }}\"\n"
                            "```\n\n"
                            "## Calling a Reusable Workflow\n\n"
                            "```yaml\n"
                            "jobs:\n"
                            "  call-deploy:\n"
                            "    uses: my-org/shared-workflows/.github/workflows/deploy.yml@main\n"
                            "    with:\n"
                            "      environment: production\n"
                            "    secrets:\n"
                            "      deploy_key: ${{ secrets.PROD_DEPLOY_KEY }}\n"
                            "```\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 1,
                    },
                    {
                        "title": "Environments, Secrets, and Approvals",
                        "markdown_content": (
                            "# Environments, Secrets, and Approvals\n\n"
                            "## Deployment Environments\n\n"
                            "Environments (`staging`, `production`) add protection rules and "
                            "scoped secrets to your deployments.\n\n"
                            "## Configuring Environment Protection\n\n"
                            "1. Go to **Settings → Environments → New environment**.\n"
                            "2. Add **Required reviewers** — deploy jobs pause until approved.\n"
                            "3. Set a **Wait timer** (minutes to delay before deploying).\n"
                            "4. Restrict to specific branches (e.g., `main` only).\n\n"
                            "## Environment Secrets\n\n"
                            "Secrets scoped to an environment are only accessible when the job "
                            "targets that environment:\n\n"
                            "```yaml\n"
                            "jobs:\n"
                            "  deploy-prod:\n"
                            "    environment: production\n"
                            "    runs-on: ubuntu-latest\n"
                            "    steps:\n"
                            "      - name: Deploy\n"
                            "        run: deploy.sh\n"
                            "        env:\n"
                            "          API_KEY: ${{ secrets.PROD_API_KEY }}\n"
                            "```\n\n"
                            "## OIDC for Keyless Authentication\n\n"
                            "Use OIDC to authenticate with cloud providers (AWS, Azure, GCP) "
                            "without storing long-lived credentials as secrets:\n\n"
                            "```yaml\n"
                            "permissions:\n"
                            "  id-token: write\n"
                            "  contents: read\n"
                            "```\n"
                        ),
                        "estimated_minutes": 15,
                        "sort_order": 2,
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What trigger makes a workflow callable from other workflows?",
                        "options": [
                            "workflow_run",
                            "workflow_call",
                            "workflow_dispatch",
                            "repository_dispatch",
                        ],
                        "correct_answer": "workflow_call",
                        "explanation": (
                            "`workflow_call` is the trigger that marks a workflow as reusable, "
                            "allowing it to be called from other workflows using `uses:` in a job definition."
                        ),
                    },
                    {
                        "question": "What GitHub Actions feature pauses a deployment until a designated reviewer approves it?",
                        "options": [
                            "Branch protection rules",
                            "Job concurrency groups",
                            "Environment required reviewers",
                            "Workflow approval gates",
                        ],
                        "correct_answer": "Environment required reviewers",
                        "explanation": (
                            "Deployment environments support 'Required reviewers' — when a job targets "
                            "an environment with reviewers configured, the job is paused until one of "
                            "the designated reviewers approves the deployment."
                        ),
                    },
                    {
                        "question": "What is the main advantage of using OIDC for cloud authentication in GitHub Actions?",
                        "options": [
                            "It speeds up workflow execution.",
                            "It eliminates the need to store long-lived cloud credentials as secrets.",
                            "It allows workflows to run on self-hosted runners.",
                            "It enables matrix builds across multiple cloud providers.",
                        ],
                        "correct_answer": "It eliminates the need to store long-lived cloud credentials as secrets.",
                        "explanation": (
                            "OIDC (OpenID Connect) allows GitHub Actions to obtain short-lived tokens "
                            "from cloud providers directly, removing the security risk of storing "
                            "long-lived API keys or service account credentials as repository secrets."
                        ),
                    },
                ],
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Seed runner
# ---------------------------------------------------------------------------


async def seed() -> None:
    """Seed the database with initial users and starter courses.

    Idempotent — if the admin user already exists, the seed is skipped.
    """
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # --- Guard: skip if already seeded ---
        existing = await db.execute(
            select(User).where(User.email == "admin@example.com")
        )
        if existing.scalar_one_or_none() is not None:
            logger.info("Database already seeded — skipping.")
            return

        # --- Users ---
        admin_user = User(
            name="Platform Admin",
            email="admin@example.com",
            hashed_password=hash_password("Admin1234!"),
            role=UserRole.admin,
            is_active=True,
        )
        learner_user = User(
            name="Test Learner",
            email="learner@example.com",
            hashed_password=hash_password("Learner1234!"),
            role=UserRole.learner,
            is_active=True,
        )
        db.add(admin_user)
        db.add(learner_user)
        await db.flush()  # get user IDs
        logger.info(
            "Users created: admin_id=%d learner_id=%d",
            admin_user.id,
            learner_user.id,
        )

        # --- Courses, Modules, Lessons, QuizQuestions ---
        for course_data in SEED_COURSES:
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                status=CourseStatus.published,
                difficulty=course_data["difficulty"],
                estimated_duration=course_data["estimated_duration"],
                tags=course_data["tags"],
                created_by=admin_user.id,
            )
            db.add(course)
            await db.flush()

            for module_data in course_data["modules"]:
                module = Module(
                    course_id=course.id,
                    title=module_data["title"],
                    summary=module_data["summary"],
                    sort_order=module_data["sort_order"],
                )
                db.add(module)
                await db.flush()

                for lesson_data in module_data["lessons"]:
                    lesson = Lesson(
                        module_id=module.id,
                        title=lesson_data["title"],
                        markdown_content=lesson_data["markdown_content"],
                        estimated_minutes=lesson_data["estimated_minutes"],
                        sort_order=lesson_data["sort_order"],
                    )
                    db.add(lesson)

                for q_data in module_data["quiz_questions"]:
                    question = QuizQuestion(
                        module_id=module.id,
                        question=q_data["question"],
                        options=q_data["options"],
                        correct_answer=q_data["correct_answer"],
                        explanation=q_data.get("explanation"),
                    )
                    db.add(question)

            logger.info("Course seeded: %r", course.title)

        await db.commit()
        logger.info("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
