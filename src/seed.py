"""
Database seed script for the Learning Platform MVP.

Creates 3 starter courses (GitHub Foundations, GitHub Advanced Security,
GitHub Actions) and 2 default users (admin + learner).

Usage::

    python -m src.seed

The script is idempotent — if the admin user already exists it exits early.
"""

import asyncio
import uuid
from datetime import datetime

from src.database import AsyncSessionLocal, init_db
from src.auth.service import hash_password
from src.models import User, Course, Module, Lesson, QuizQuestion


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

COURSES = [
    {
        "title": "GitHub Foundations",
        "description": (
            "Master the fundamentals of Git and GitHub. This course walks you through "
            "version control concepts, repository management, and team collaboration "
            "workflows used by millions of developers worldwide."
        ),
        "status": "published",
        "difficulty": "beginner",
        "estimated_duration": 120,
        "tags": ["github", "git", "foundations"],
        "modules": [
            {
                "title": "Git Basics",
                "sort_order": 1,
                "lessons": [
                    {
                        "title": "Introduction to Version Control",
                        "sort_order": 1,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## What is Version Control?\n\n"
                            "Version control is a system that records changes to a file or set of files over time "
                            "so that you can recall specific versions later. It allows multiple developers to "
                            "collaborate on a project, track changes, and revert to previous states when needed.\n\n"
                            "## Why Git?\n\n"
                            "Git is the most widely used distributed version control system in the world. "
                            "Unlike centralised systems, every developer has a full copy of the repository, "
                            "including its complete history, making operations like branching and merging fast "
                            "and efficient even without a network connection.\n\n"
                            "## Key Concepts\n\n"
                            "- **Repository**: A directory tracked by Git.\n"
                            "- **Commit**: A snapshot of your changes.\n"
                            "- **Branch**: An independent line of development.\n"
                            "- **Merge**: Combining changes from different branches.\n"
                        ),
                    },
                    {
                        "title": "Your First Git Commands",
                        "sort_order": 2,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## Setting Up Git\n\n"
                            "Before using Git, configure your identity so every commit is attributed to you:\n\n"
                            "```bash\n"
                            "git config --global user.name  \"Your Name\"\n"
                            "git config --global user.email \"you@example.com\"\n"
                            "```\n\n"
                            "## Initialising a Repository\n\n"
                            "Create a new Git repository in the current directory with `git init`. "
                            "This creates a hidden `.git` folder that stores all history and metadata.\n\n"
                            "## Staging and Committing\n\n"
                            "Use `git add <file>` to stage changes, then `git commit -m \"message\"` to record "
                            "a snapshot. Think of staging as preparing a parcel before sealing and sending it.\n\n"
                            "## Viewing History\n\n"
                            "`git log` shows the commit history. Use `git log --oneline` for a compact view.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which command initialises a new Git repository?",
                        "options": ["git start", "git init", "git create", "git new"],
                        "correct_answer": "git init",
                        "explanation": "`git init` creates a new `.git` directory in the current folder, turning it into a Git repository.",
                    },
                    {
                        "question": "What does `git add` do?",
                        "options": [
                            "Commits changes to the repository",
                            "Stages changes for the next commit",
                            "Pushes changes to a remote",
                            "Creates a new branch",
                        ],
                        "correct_answer": "Stages changes for the next commit",
                        "explanation": "`git add` moves changes into the staging area, where they wait to be included in the next commit.",
                    },
                ],
            },
            {
                "title": "GitHub Repository Management",
                "sort_order": 2,
                "lessons": [
                    {
                        "title": "Creating and Cloning Repositories",
                        "sort_order": 1,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## Creating a Repository on GitHub\n\n"
                            "Navigate to github.com, click **New repository**, choose a name, set visibility "
                            "(public or private), and optionally initialise with a README. GitHub then hosts "
                            "your repository and provides a remote URL.\n\n"
                            "## Cloning a Repository\n\n"
                            "Use `git clone <url>` to copy a remote repository to your local machine. "
                            "Git automatically sets the remote origin for you so you can push and pull changes.\n\n"
                            "## README and .gitignore\n\n"
                            "A well-written README is the front page of your project. Include a description, "
                            "installation steps, and usage examples. The `.gitignore` file lists paths that Git "
                            "should not track, such as build artifacts or secret configuration files.\n"
                        ),
                    },
                    {
                        "title": "Branches and Pull Requests",
                        "sort_order": 2,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## Working with Branches\n\n"
                            "Branches let you develop features in isolation. Create a branch with "
                            "`git checkout -b feature/my-feature` and switch between them freely without "
                            "affecting the main line of development.\n\n"
                            "## Opening a Pull Request\n\n"
                            "Once your feature branch is pushed to GitHub, open a Pull Request (PR) to propose "
                            "merging it into the target branch. PRs include a diff view, discussion thread, "
                            "and status checks from CI systems.\n\n"
                            "## Code Review\n\n"
                            "Team members review the PR, leave inline comments, and either approve or request "
                            "changes. Once approved and all checks pass, the branch is merged.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which command creates a new branch and switches to it immediately?",
                        "options": [
                            "git branch feature",
                            "git checkout -b feature",
                            "git switch feature",
                            "git new-branch feature",
                        ],
                        "correct_answer": "git checkout -b feature",
                        "explanation": "`git checkout -b <name>` is a shorthand for `git branch <name>` followed by `git checkout <name>`.",
                    },
                    {
                        "question": "What is the primary purpose of a Pull Request?",
                        "options": [
                            "Download repository changes",
                            "Propose and review changes before merging",
                            "Delete a remote branch",
                            "Revert a commit",
                        ],
                        "correct_answer": "Propose and review changes before merging",
                        "explanation": "A Pull Request notifies collaborators about changes and provides a space for discussion and review before code is merged.",
                    },
                ],
            },
            {
                "title": "Collaboration Workflows",
                "sort_order": 3,
                "lessons": [
                    {
                        "title": "Forking and Upstream Remotes",
                        "sort_order": 1,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## The Fork Workflow\n\n"
                            "Forking creates your own copy of someone else's repository under your GitHub account. "
                            "This is the standard way to contribute to open-source projects — you make changes in "
                            "your fork and then open a PR back to the original (upstream) repository.\n\n"
                            "## Adding an Upstream Remote\n\n"
                            "After cloning your fork, add the original repository as a second remote:\n\n"
                            "```bash\n"
                            "git remote add upstream https://github.com/original/repo.git\n"
                            "```\n\n"
                            "Fetch and merge upstream changes regularly to keep your fork up to date:\n\n"
                            "```bash\n"
                            "git fetch upstream\n"
                            "git merge upstream/main\n"
                            "```\n"
                        ),
                    },
                    {
                        "title": "Resolving Merge Conflicts",
                        "sort_order": 2,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## What is a Merge Conflict?\n\n"
                            "A merge conflict occurs when two branches modify the same region of a file "
                            "differently and Git cannot automatically determine which change to keep.\n\n"
                            "## Identifying Conflicts\n\n"
                            "Git marks conflict regions with `<<<<<<<`, `=======`, and `>>>>>>>` markers. "
                            "The section above `=======` is the current branch; below is the incoming change.\n\n"
                            "## Resolving and Completing the Merge\n\n"
                            "Edit the file to keep the desired changes, remove the markers, stage the file "
                            "with `git add`, and complete the merge with `git commit`.\n\n"
                            "## Prevention Tips\n\n"
                            "- Keep branches short-lived and merge frequently.\n"
                            "- Communicate with teammates about which files you are editing.\n"
                            "- Pull the latest main branch changes before starting new work.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What markers does Git use to indicate a merge conflict in a file?",
                        "options": [
                            "<<< === >>>",
                            "<<<<<<< ======= >>>>>>>",
                            "CONFLICT_START CONFLICT_END",
                            "## CONFLICT ##",
                        ],
                        "correct_answer": "<<<<<<< ======= >>>>>>>",
                        "explanation": "Git wraps conflicting sections with `<<<<<<<` (current), `=======` (separator), and `>>>>>>>` (incoming) markers.",
                    },
                    {
                        "question": "What is a fork on GitHub?",
                        "options": [
                            "A new branch in the same repository",
                            "A personal copy of another user's repository",
                            "A merge of two repositories",
                            "A read-only snapshot of a commit",
                        ],
                        "correct_answer": "A personal copy of another user's repository",
                        "explanation": "Forking copies a repository into your account so you can freely experiment without affecting the original project.",
                    },
                ],
            },
        ],
    },
    {
        "title": "GitHub Advanced Security",
        "description": (
            "Learn how to leverage GitHub Advanced Security (GHAS) features — including code scanning, "
            "secret scanning, and dependency review — to identify and remediate vulnerabilities early "
            "in the software development lifecycle."
        ),
        "status": "published",
        "difficulty": "intermediate",
        "estimated_duration": 90,
        "tags": ["github", "security", "ghas", "devsecops"],
        "modules": [
            {
                "title": "Code Scanning",
                "sort_order": 1,
                "lessons": [
                    {
                        "title": "Introduction to Code Scanning",
                        "sort_order": 1,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## What is Code Scanning?\n\n"
                            "GitHub Code Scanning is a developer-first static analysis service that helps you find "
                            "security vulnerabilities and coding errors before they reach production. "
                            "It uses CodeQL — GitHub's semantic code analysis engine — and third-party tools to "
                            "analyse every push and pull request.\n\n"
                            "## Enabling Code Scanning\n\n"
                            "Navigate to **Settings → Security → Code security and analysis** and enable "
                            "Code Scanning. GitHub will suggest the default CodeQL workflow, which you can "
                            "commit directly to your repository.\n\n"
                            "## Reading Alerts\n\n"
                            "Alerts appear under **Security → Code scanning alerts**. Each alert shows the "
                            "vulnerable code path, a severity rating (critical/high/medium/low), and remediation "
                            "guidance. Alerts can be dismissed with an explanation if they are false positives.\n"
                        ),
                    },
                    {
                        "title": "Writing Custom CodeQL Queries",
                        "sort_order": 2,
                        "estimated_minutes": 25,
                        "markdown_content": (
                            "## CodeQL as a Query Language\n\n"
                            "CodeQL treats code as data. You write queries in a SQL-like language to find patterns "
                            "that represent vulnerabilities across an entire codebase.\n\n"
                            "## Setting Up the CodeQL CLI\n\n"
                            "Download the CodeQL CLI bundle and create a database for your repository:\n\n"
                            "```bash\n"
                            "codeql database create my-db --language=python\n"
                            "codeql query run my-query.ql --database=my-db\n"
                            "```\n\n"
                            "## Example: Finding Hard-Coded Credentials\n\n"
                            "A simple CodeQL query can find string literals that look like passwords or API keys "
                            "assigned to variables with suspicious names, helping catch secrets before they are "
                            "committed.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which analysis engine powers GitHub Code Scanning by default?",
                        "options": ["SonarQube", "CodeQL", "Snyk", "Semgrep"],
                        "correct_answer": "CodeQL",
                        "explanation": "GitHub Code Scanning uses CodeQL, GitHub's own semantic code analysis engine, to find vulnerabilities.",
                    },
                ],
            },
            {
                "title": "Secret Scanning",
                "sort_order": 2,
                "lessons": [
                    {
                        "title": "How Secret Scanning Works",
                        "sort_order": 1,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## Detecting Leaked Secrets\n\n"
                            "Secret Scanning automatically scans repository contents for known secret formats "
                            "(API keys, tokens, credentials) from over 200 service providers. When a secret is "
                            "detected GitHub notifies the repository administrator and, for supported partners, "
                            "automatically revokes the secret.\n\n"
                            "## Push Protection\n\n"
                            "With push protection enabled, GitHub blocks commits that contain secrets before they "
                            "reach the repository, preventing exposure at the source rather than reactively.\n\n"
                            "## Responding to Alerts\n\n"
                            "Rotate the secret immediately, then dismiss the alert as revoked. Review your "
                            "repository history to confirm the secret has not been accessed maliciously.\n"
                        ),
                    },
                    {
                        "title": "Custom Secret Patterns",
                        "sort_order": 2,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## Beyond Built-In Patterns\n\n"
                            "If your organisation uses internal tokens or proprietary service credentials, "
                            "you can define custom secret scanning patterns using regular expressions under "
                            "**Settings → Security → Secret scanning → Custom patterns**.\n\n"
                            "## Pattern Best Practices\n\n"
                            "- Anchor patterns tightly to reduce false positives.\n"
                            "- Test patterns against real and synthetic samples before enabling.\n"
                            "- Add a descriptive name so that alerts are easy to triage.\n\n"
                            "## Organisation-Level Patterns\n\n"
                            "Enterprise and organisation owners can define patterns that apply across all "
                            "repositories, providing centralised governance of secret detection rules.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What does Secret Scanning Push Protection do?",
                        "options": [
                            "Encrypts secrets before pushing",
                            "Blocks commits containing secrets before they reach the repository",
                            "Rotates secrets automatically",
                            "Scans pull request titles for secrets",
                        ],
                        "correct_answer": "Blocks commits containing secrets before they reach the repository",
                        "explanation": "Push protection prevents secrets from ever entering the repository by rejecting the push at the point of upload.",
                    },
                ],
            },
            {
                "title": "Dependency Review",
                "sort_order": 3,
                "lessons": [
                    {
                        "title": "Understanding Dependency Review",
                        "sort_order": 1,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## What is Dependency Review?\n\n"
                            "Dependency Review surfaces the security impact of dependency changes in pull requests "
                            "by showing which packages are being added, updated, or removed and whether any "
                            "introduced versions have known vulnerabilities (CVEs).\n\n"
                            "## The Dependency Review Action\n\n"
                            "Add the `actions/dependency-review-action` workflow to your repository to block PRs "
                            "that introduce vulnerable dependencies automatically:\n\n"
                            "```yaml\n"
                            "- uses: actions/dependency-review-action@v4\n"
                            "  with:\n"
                            "    fail-on-severity: high\n"
                            "```\n\n"
                            "## Dependabot Alerts\n\n"
                            "Dependabot continuously monitors your dependency graph and opens automated pull "
                            "requests to upgrade vulnerable packages to safe versions.\n"
                        ),
                    },
                    {
                        "title": "Managing Dependabot",
                        "sort_order": 2,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## Dependabot Configuration\n\n"
                            "Create a `.github/dependabot.yml` file to configure automated dependency updates. "
                            "Specify the package ecosystem, target directory, and update schedule:\n\n"
                            "```yaml\n"
                            "version: 2\n"
                            "updates:\n"
                            "  - package-ecosystem: pip\n"
                            "    directory: /\n"
                            "    schedule:\n"
                            "      interval: weekly\n"
                            "```\n\n"
                            "## Reviewing Dependabot PRs\n\n"
                            "Dependabot PRs include a changelog summary, compatibility score, and link to the "
                            "vulnerability advisory. Review and merge them promptly — especially for security "
                            "updates — to keep your dependency graph healthy.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "What file is used to configure Dependabot automated updates?",
                        "options": [
                            ".github/dependabot.yml",
                            "dependabot.json",
                            ".dependabot/config.yml",
                            "package.json",
                        ],
                        "correct_answer": ".github/dependabot.yml",
                        "explanation": "Dependabot reads its configuration from `.github/dependabot.yml` in the root of the repository.",
                    },
                ],
            },
        ],
    },
    {
        "title": "GitHub Actions",
        "description": (
            "Automate your software development workflows with GitHub Actions. Learn how to write "
            "CI/CD pipelines, build reusable workflows, and deploy applications directly from GitHub."
        ),
        "status": "published",
        "difficulty": "intermediate",
        "estimated_duration": 105,
        "tags": ["github", "actions", "ci-cd", "automation"],
        "modules": [
            {
                "title": "Workflow Syntax",
                "sort_order": 1,
                "lessons": [
                    {
                        "title": "Anatomy of a GitHub Actions Workflow",
                        "sort_order": 1,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## What is a Workflow?\n\n"
                            "A workflow is an automated process defined in a YAML file stored under "
                            "`.github/workflows/`. It is triggered by events such as `push`, `pull_request`, "
                            "or a schedule, and it orchestrates one or more jobs.\n\n"
                            "## Key Components\n\n"
                            "- **on**: Defines the trigger event(s).\n"
                            "- **jobs**: A map of named jobs; each job runs on a runner.\n"
                            "- **steps**: Ordered list of actions or shell commands within a job.\n\n"
                            "## Minimal Example\n\n"
                            "```yaml\n"
                            "name: CI\n"
                            "on: [push]\n"
                            "jobs:\n"
                            "  build:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    steps:\n"
                            "      - uses: actions/checkout@v4\n"
                            "      - run: echo 'Hello, Actions!'\n"
                            "```\n"
                        ),
                    },
                    {
                        "title": "Triggers and Filters",
                        "sort_order": 2,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## Event Triggers\n\n"
                            "Workflows can be triggered by dozens of GitHub events. Common examples:\n\n"
                            "- `push` — runs on every push to specified branches.\n"
                            "- `pull_request` — runs when a PR is opened, synchronised, or reopened.\n"
                            "- `schedule` — runs on a cron schedule.\n"
                            "- `workflow_dispatch` — allows manual triggering from the GitHub UI.\n\n"
                            "## Branch and Path Filters\n\n"
                            "Narrow when a workflow runs using filters:\n\n"
                            "```yaml\n"
                            "on:\n"
                            "  push:\n"
                            "    branches: [main, 'release/**']\n"
                            "    paths: ['src/**', 'tests/**']\n"
                            "```\n\n"
                            "## Concurrency Control\n\n"
                            "Use `concurrency` to cancel in-progress runs when a newer commit is pushed, "
                            "saving runner minutes and avoiding race conditions in deployments.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Where must workflow YAML files be stored in a repository?",
                        "options": [
                            ".github/actions/",
                            ".github/workflows/",
                            "workflows/",
                            ".ci/",
                        ],
                        "correct_answer": ".github/workflows/",
                        "explanation": "GitHub Actions discovers workflows from YAML files placed in the `.github/workflows/` directory.",
                    },
                ],
            },
            {
                "title": "CI/CD Pipelines",
                "sort_order": 2,
                "lessons": [
                    {
                        "title": "Building a CI Pipeline",
                        "sort_order": 1,
                        "estimated_minutes": 25,
                        "markdown_content": (
                            "## Continuous Integration with Actions\n\n"
                            "A CI pipeline automatically builds and tests your code on every push, providing rapid "
                            "feedback on whether changes are safe to merge. GitHub Actions makes this straightforward "
                            "with hosted runners for Linux, macOS, and Windows.\n\n"
                            "## Example Python CI Workflow\n\n"
                            "```yaml\n"
                            "name: Python CI\n"
                            "on: [push, pull_request]\n"
                            "jobs:\n"
                            "  test:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    steps:\n"
                            "      - uses: actions/checkout@v4\n"
                            "      - uses: actions/setup-python@v5\n"
                            "        with: { python-version: '3.12' }\n"
                            "      - run: pip install -r requirements.txt\n"
                            "      - run: pytest\n"
                            "```\n\n"
                            "## Caching Dependencies\n\n"
                            "Use `actions/cache` to cache package manager directories between runs, "
                            "significantly reducing pipeline duration.\n"
                        ),
                    },
                    {
                        "title": "Deploying with GitHub Actions",
                        "sort_order": 2,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## Continuous Deployment\n\n"
                            "Once tests pass, a CD pipeline automatically deploys the application to your "
                            "target environment. GitHub Actions integrates with all major cloud providers through "
                            "official and community actions.\n\n"
                            "## Using Environments and Secrets\n\n"
                            "Define deployment environments (e.g., staging, production) in repository settings. "
                            "Each environment can have protection rules (required reviewers, wait timers) and "
                            "its own set of secrets.\n\n"
                            "## OIDC Authentication\n\n"
                            "Use OpenID Connect (OIDC) tokens to authenticate with cloud providers without "
                            "storing long-lived credentials as secrets. The `permissions: id-token: write` "
                            "setting enables this for a job.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which Actions feature lets you authenticate to cloud providers without storing long-lived credentials?",
                        "options": [
                            "Repository secrets",
                            "Environment variables",
                            "OIDC tokens",
                            "Encrypted artifacts",
                        ],
                        "correct_answer": "OIDC tokens",
                        "explanation": "OIDC (OpenID Connect) allows jobs to request short-lived tokens from cloud providers, eliminating the need for static credentials.",
                    },
                ],
            },
            {
                "title": "Reusable Workflows",
                "sort_order": 3,
                "lessons": [
                    {
                        "title": "Creating Reusable Workflows",
                        "sort_order": 1,
                        "estimated_minutes": 20,
                        "markdown_content": (
                            "## What are Reusable Workflows?\n\n"
                            "Reusable workflows allow you to define a workflow once and call it from multiple "
                            "other workflows, avoiding duplication and enforcing consistency across repositories "
                            "in your organisation.\n\n"
                            "## Defining a Reusable Workflow\n\n"
                            "Use `on: workflow_call` as the trigger. You can declare `inputs` and `secrets` "
                            "that callers must supply:\n\n"
                            "```yaml\n"
                            "on:\n"
                            "  workflow_call:\n"
                            "    inputs:\n"
                            "      environment:\n"
                            "        required: true\n"
                            "        type: string\n"
                            "```\n\n"
                            "## Calling a Reusable Workflow\n\n"
                            "Reference the reusable workflow using `uses:` at the job level with its full path "
                            "(`owner/repo/.github/workflows/file.yml@ref`).\n"
                        ),
                    },
                    {
                        "title": "Composite Actions",
                        "sort_order": 2,
                        "estimated_minutes": 15,
                        "markdown_content": (
                            "## Actions vs Reusable Workflows\n\n"
                            "Composite actions bundle multiple steps into a single reusable action, referenced "
                            "with `uses:` inside a job step. They are ideal for sharing small, focused tasks "
                            "(e.g., setting up a tool chain) rather than entire pipelines.\n\n"
                            "## Creating a Composite Action\n\n"
                            "Create a directory with an `action.yml` that declares `using: composite` and lists "
                            "the steps:\n\n"
                            "```yaml\n"
                            "runs:\n"
                            "  using: composite\n"
                            "  steps:\n"
                            "    - run: pip install -r requirements.txt\n"
                            "      shell: bash\n"
                            "```\n\n"
                            "## Publishing to the Marketplace\n\n"
                            "Tag a release and choose to publish to the GitHub Actions Marketplace to make your "
                            "action discoverable by the entire GitHub community.\n"
                        ),
                    },
                ],
                "quiz_questions": [
                    {
                        "question": "Which trigger keyword makes a workflow reusable by other workflows?",
                        "options": [
                            "workflow_dispatch",
                            "workflow_run",
                            "workflow_call",
                            "repository_dispatch",
                        ],
                        "correct_answer": "workflow_call",
                        "explanation": "`on: workflow_call` designates a workflow as reusable so other workflows can invoke it with `uses:`.",
                    },
                ],
            },
        ],
    },
]

USERS = [
    {
        "name": "Platform Admin",
        "email": "admin@platform.local",
        "password": "Admin123!",
        "role": "admin",
    },
    {
        "name": "Demo Learner",
        "email": "learner@platform.local",
        "password": "Learner123!",
        "role": "learner",
    },
]


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------


async def main() -> None:
    """
    Async entry-point for the seed script.

    Initialises the database schema, then inserts default users and starter
    courses if they do not already exist (idempotent).
    """
    await init_db()

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        # Idempotency guard — skip everything if admin already exists
        result = await db.execute(
            select(User).where(User.email == "admin@platform.local")
        )
        existing_admin = result.scalar_one_or_none()
        if existing_admin is not None:
            print("Database already seeded — skipping.")
            return

        # ----------------------------------------------------------------
        # Create users
        # ----------------------------------------------------------------
        print("Creating default users…")
        for user_data in USERS:
            user = User(
                id=str(uuid.uuid4()),
                name=user_data["name"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                created_at=datetime.utcnow(),
                is_active=True,
            )
            db.add(user)

        await db.flush()  # obtain user IDs before FK usage

        # Retrieve admin user to set as course creator
        admin_result = await db.execute(
            select(User).where(User.email == "admin@platform.local")
        )
        admin_user: User = admin_result.scalar_one()

        # ----------------------------------------------------------------
        # Create courses
        # ----------------------------------------------------------------
        print("Creating starter courses…")
        for course_data in COURSES:
            course = Course(
                id=str(uuid.uuid4()),
                title=course_data["title"],
                description=course_data["description"],
                status=course_data["status"],
                difficulty=course_data["difficulty"],
                estimated_duration=course_data["estimated_duration"],
                tags=course_data["tags"],
                created_by=admin_user.id,
                is_ai_generated=False,
            )
            db.add(course)
            await db.flush()  # get course.id

            for mod_data in course_data["modules"]:
                module = Module(
                    id=str(uuid.uuid4()),
                    course_id=course.id,
                    title=mod_data["title"],
                    sort_order=mod_data["sort_order"],
                )
                db.add(module)
                await db.flush()  # get module.id

                for lesson_data in mod_data["lessons"]:
                    lesson = Lesson(
                        id=str(uuid.uuid4()),
                        module_id=module.id,
                        title=lesson_data["title"],
                        sort_order=lesson_data["sort_order"],
                        estimated_minutes=lesson_data["estimated_minutes"],
                        markdown_content=lesson_data["markdown_content"],
                    )
                    db.add(lesson)

                for q_data in mod_data["quiz_questions"]:
                    question = QuizQuestion(
                        id=str(uuid.uuid4()),
                        module_id=module.id,
                        question=q_data["question"],
                        options=q_data["options"],
                        correct_answer=q_data["correct_answer"],
                        explanation=q_data["explanation"],
                    )
                    db.add(question)

        await db.commit()
        print("Seeding complete ✅")
        print(f"  • {len(USERS)} users created")
        print(f"  • {len(COURSES)} courses created")


if __name__ == "__main__":
    asyncio.run(main())
