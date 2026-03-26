"""Initial schema — create all 10 tables.

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

Creates all 10 domain tables for the Learning Platform MVP:
  1. users
  2. courses
  3. modules
  4. lessons
  5. quiz_questions
  6. enrollments
  7. progress_records
  8. quiz_attempts
  9. content_generation_requests
 10. content_generation_artifacts

Includes explicit indexes on frequently queried FK columns and the unique
index on ``users.email``.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all 10 tables with constraints and indexes."""

    # ------------------------------------------------------------------
    # 1. users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("learner", "admin", name="user_role"),
            nullable=False,
            server_default="learner",
        ),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
    )
    op.create_index("idx_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # 2. courses
    # ------------------------------------------------------------------
    op.create_table(
        "courses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "published", name="course_status"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "difficulty",
            sa.Enum("beginner", "intermediate", "advanced", name="difficulty_level"),
            nullable=False,
        ),
        sa.Column("estimated_duration", sa.Integer, nullable=False),
        sa.Column("tags", sa.Text, nullable=False, server_default="[]"),
        sa.Column(
            "created_by",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # ------------------------------------------------------------------
    # 3. modules
    # ------------------------------------------------------------------
    op.create_table(
        "modules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "course_id",
            sa.String(36),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("idx_modules_course_id", "modules", ["course_id"])

    # ------------------------------------------------------------------
    # 4. lessons
    # ------------------------------------------------------------------
    op.create_table(
        "lessons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "module_id",
            sa.String(36),
            sa.ForeignKey("modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("markdown_content", sa.Text, nullable=False, server_default=""),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("idx_lessons_module_id", "lessons", ["module_id"])

    # ------------------------------------------------------------------
    # 5. quiz_questions
    # ------------------------------------------------------------------
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "module_id",
            sa.String(36),
            sa.ForeignKey("modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("options", sa.Text, nullable=False, server_default="[]"),
        sa.Column("correct_answer", sa.String(500), nullable=False),
        sa.Column("explanation", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("idx_quiz_questions_module_id", "quiz_questions", ["module_id"])

    # ------------------------------------------------------------------
    # 6. enrollments
    # ------------------------------------------------------------------
    op.create_table(
        "enrollments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.String(36),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("enrolled_at", sa.DateTime, nullable=False),
        sa.Column(
            "status",
            sa.Enum("not_started", "in_progress", "completed", name="enrollment_status"),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )
    op.create_index("idx_enrollments_user_id", "enrollments", ["user_id"])
    op.create_index("idx_enrollments_course_id", "enrollments", ["course_id"])

    # ------------------------------------------------------------------
    # 7. progress_records
    # ------------------------------------------------------------------
    op.create_table(
        "progress_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "lesson_id",
            sa.String(36),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "module_id",
            sa.String(36),
            sa.ForeignKey("modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("completed", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("last_viewed_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )
    op.create_index("idx_progress_records_user_id", "progress_records", ["user_id"])
    op.create_index("idx_progress_records_lesson_id", "progress_records", ["lesson_id"])
    op.create_index("idx_progress_records_module_id", "progress_records", ["module_id"])

    # ------------------------------------------------------------------
    # 8. quiz_attempts
    # ------------------------------------------------------------------
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "quiz_question_id",
            sa.String(36),
            sa.ForeignKey("quiz_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("selected_answer", sa.String(500), nullable=False),
        sa.Column("is_correct", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("attempted_at", sa.DateTime, nullable=False),
    )
    op.create_index("idx_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("idx_quiz_attempts_question_id", "quiz_attempts", ["quiz_question_id"])

    # ------------------------------------------------------------------
    # 9. content_generation_requests
    # ------------------------------------------------------------------
    op.create_table(
        "content_generation_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("prompt", sa.Text, nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column(
            "requester_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", "failed", name="generation_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index(
        "idx_gen_requests_requester_id", "content_generation_requests", ["requester_id"]
    )

    # ------------------------------------------------------------------
    # 10. content_generation_artifacts
    # ------------------------------------------------------------------
    op.create_table(
        "content_generation_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("generated_content", sa.Text, nullable=False),
        sa.Column(
            "source_request_id",
            sa.String(36),
            sa.ForeignKey("content_generation_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "approved_by",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column(
            "course_id",
            sa.String(36),
            sa.ForeignKey("courses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "module_id",
            sa.String(36),
            sa.ForeignKey("modules.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "lesson_id",
            sa.String(36),
            sa.ForeignKey("lessons.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index(
        "idx_gen_artifacts_source_request_id",
        "content_generation_artifacts",
        ["source_request_id"],
    )


def downgrade() -> None:
    """Drop all 10 tables in reverse dependency order."""
    op.drop_table("content_generation_artifacts")
    op.drop_table("content_generation_requests")
    op.drop_table("quiz_attempts")
    op.drop_table("progress_records")
    op.drop_table("enrollments")
    op.drop_table("quiz_questions")
    op.drop_table("lessons")
    op.drop_table("modules")
    op.drop_table("courses")
    op.drop_table("users")
