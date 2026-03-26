"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

Creates all 10 tables for the Learning Platform MVP:
  1.  users
  2.  courses
  3.  modules
  4.  lessons
  5.  quiz_questions
  6.  enrollments
  7.  progress_records
  8.  quiz_attempts
  9.  content_generation_requests
  10. content_generation_artifacts
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Revision identifiers — used by Alembic
# ---------------------------------------------------------------------------

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


# ---------------------------------------------------------------------------
# Upgrade — create all tables
# ---------------------------------------------------------------------------


def upgrade() -> None:
    """Create all 10 domain tables with indexes and constraints."""

    # ------------------------------------------------------------------
    # 1. users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("learner", "admin", name="userrole"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # 2. courses
    # ------------------------------------------------------------------
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "status",
            sa.Enum("draft", "published", name="coursestatus"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("difficulty", sa.String(50), nullable=False, server_default="beginner"),
        sa.Column("estimated_duration", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_courses_id", "courses", ["id"], unique=False)

    # ------------------------------------------------------------------
    # 3. modules
    # ------------------------------------------------------------------
    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_modules_id", "modules", ["id"], unique=False)
    op.create_index("ix_modules_course_id", "modules", ["course_id"], unique=False)

    # ------------------------------------------------------------------
    # 4. lessons
    # ------------------------------------------------------------------
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("markdown_content", sa.Text(), nullable=False, server_default=""),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lessons_id", "lessons", ["id"], unique=False)
    op.create_index("ix_lessons_module_id", "lessons", ["module_id"], unique=False)

    # ------------------------------------------------------------------
    # 5. quiz_questions
    # ------------------------------------------------------------------
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("options", sa.Text(), nullable=False),
        sa.Column("correct_answer", sa.String(255), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quiz_questions_id", "quiz_questions", ["id"], unique=False)
    op.create_index("ix_quiz_questions_module_id", "quiz_questions", ["module_id"], unique=False)

    # ------------------------------------------------------------------
    # 6. enrollments
    # ------------------------------------------------------------------
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("not_started", "in_progress", "completed", name="enrollmentstatus"),
            nullable=False,
            server_default="not_started",
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )
    op.create_index("ix_enrollments_id", "enrollments", ["id"], unique=False)
    op.create_index("ix_enrollments_user_id", "enrollments", ["user_id"], unique=False)
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"], unique=False)

    # ------------------------------------------------------------------
    # 7. progress_records
    # ------------------------------------------------------------------
    op.create_table(
        "progress_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_viewed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )
    op.create_index("ix_progress_records_id", "progress_records", ["id"], unique=False)
    op.create_index("ix_progress_records_user_id", "progress_records", ["user_id"], unique=False)
    op.create_index("ix_progress_records_lesson_id", "progress_records", ["lesson_id"], unique=False)
    op.create_index("ix_progress_records_module_id", "progress_records", ["module_id"], unique=False)

    # ------------------------------------------------------------------
    # 8. quiz_attempts
    # ------------------------------------------------------------------
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quiz_question_id", sa.Integer(), nullable=False),
        sa.Column("selected_answer", sa.String(255), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["quiz_question_id"], ["quiz_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quiz_attempts_id", "quiz_attempts", ["id"], unique=False)
    op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"], unique=False)
    op.create_index(
        "ix_quiz_attempts_quiz_question_id", "quiz_attempts", ["quiz_question_id"], unique=False
    )

    # ------------------------------------------------------------------
    # 9. content_generation_requests
    # ------------------------------------------------------------------
    op.create_table(
        "content_generation_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("model", sa.String(100), nullable=False, server_default="gpt-4o"),
        sa.Column("requester_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "processing", "completed", "failed",
                name="contentgenerationstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_content_generation_requests_id", "content_generation_requests", ["id"], unique=False
    )
    op.create_index(
        "ix_content_generation_requests_requester_id",
        "content_generation_requests",
        ["requester_id"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # 10. content_generation_artifacts
    # ------------------------------------------------------------------
    op.create_table(
        "content_generation_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("generated_content", sa.Text(), nullable=False),
        sa.Column("source_request_id", sa.Integer(), nullable=False),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("module_id", sa.Integer(), nullable=True),
        sa.Column("lesson_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["module_id"], ["modules.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["source_request_id"],
            ["content_generation_requests.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_content_generation_artifacts_id",
        "content_generation_artifacts",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_content_generation_artifacts_source_request_id",
        "content_generation_artifacts",
        ["source_request_id"],
        unique=False,
    )


# ---------------------------------------------------------------------------
# Downgrade — drop all tables in reverse dependency order
# ---------------------------------------------------------------------------


def downgrade() -> None:
    """Drop all 10 domain tables in reverse dependency order."""

    op.drop_index(
        "ix_content_generation_artifacts_source_request_id",
        table_name="content_generation_artifacts",
    )
    op.drop_index(
        "ix_content_generation_artifacts_id",
        table_name="content_generation_artifacts",
    )
    op.drop_table("content_generation_artifacts")

    op.drop_index(
        "ix_content_generation_requests_requester_id",
        table_name="content_generation_requests",
    )
    op.drop_index(
        "ix_content_generation_requests_id",
        table_name="content_generation_requests",
    )
    op.drop_table("content_generation_requests")

    op.drop_index("ix_quiz_attempts_quiz_question_id", table_name="quiz_attempts")
    op.drop_index("ix_quiz_attempts_user_id", table_name="quiz_attempts")
    op.drop_index("ix_quiz_attempts_id", table_name="quiz_attempts")
    op.drop_table("quiz_attempts")

    op.drop_index("ix_progress_records_module_id", table_name="progress_records")
    op.drop_index("ix_progress_records_lesson_id", table_name="progress_records")
    op.drop_index("ix_progress_records_user_id", table_name="progress_records")
    op.drop_index("ix_progress_records_id", table_name="progress_records")
    op.drop_table("progress_records")

    op.drop_index("ix_enrollments_course_id", table_name="enrollments")
    op.drop_index("ix_enrollments_user_id", table_name="enrollments")
    op.drop_index("ix_enrollments_id", table_name="enrollments")
    op.drop_table("enrollments")

    op.drop_index("ix_quiz_questions_module_id", table_name="quiz_questions")
    op.drop_index("ix_quiz_questions_id", table_name="quiz_questions")
    op.drop_table("quiz_questions")

    op.drop_index("ix_lessons_module_id", table_name="lessons")
    op.drop_index("ix_lessons_id", table_name="lessons")
    op.drop_table("lessons")

    op.drop_index("ix_modules_course_id", table_name="modules")
    op.drop_index("ix_modules_id", table_name="modules")
    op.drop_table("modules")

    op.drop_index("ix_courses_id", table_name="courses")
    op.drop_table("courses")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
