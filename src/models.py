"""
ORM models for the Learning Platform MVP.

All 10 domain entities are defined here as SQLAlchemy ORM models that inherit
from :class:`src.database.Base`.  JSON list columns (``tags``, ``options``)
use the :class:`src.database.JSONList` TypeDecorator so values are stored as
JSON strings in SQLite and returned as Python lists.

Import side-effect: importing this module registers every model with
``Base.metadata``, making them visible to ``init_db()`` / ``create_all()``.
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.database.base import Base, JSONList

# ---------------------------------------------------------------------------
# Enum definitions (string-backed so SQLite stores readable values)
# ---------------------------------------------------------------------------

_user_role_enum = sa.Enum("learner", "admin", name="user_role")
_course_status_enum = sa.Enum("draft", "published", name="course_status")
_difficulty_enum = sa.Enum("beginner", "intermediate", "advanced", name="difficulty_level")
_enrollment_status_enum = sa.Enum(
    "not_started", "in_progress", "completed", name="enrollment_status"
)
_generation_status_enum = sa.Enum(
    "pending", "in_progress", "completed", "failed", name="generation_status"
)


# ---------------------------------------------------------------------------
# 1. User
# ---------------------------------------------------------------------------


class User(Base):
    """
    Platform user — either a learner consuming courses or an admin managing them.

    Attributes:
        id: UUID primary key (string form).
        name: Display name.
        email: Unique e-mail address used for login.
        hashed_password: Bcrypt-hashed password; never stored in plaintext.
        role: ``"learner"`` or ``"admin"``.
        created_at: UTC timestamp of account creation.
        is_active: Soft-delete / suspension flag; defaults to ``True``.
    """

    __tablename__ = "users"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: str = sa.Column(sa.String(255), nullable=False)
    email: str = sa.Column(sa.String(255), nullable=False, unique=True, index=True)
    hashed_password: str = sa.Column(sa.String(255), nullable=False)
    role: str = sa.Column(_user_role_enum, nullable=False, default="learner")
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )
    is_active: bool = sa.Column(sa.Boolean, nullable=False, default=True)

    # Relationships
    courses_created = relationship("Course", back_populates="creator", foreign_keys="Course.created_by")
    enrollments = relationship("Enrollment", back_populates="user", foreign_keys="Enrollment.user_id")
    progress_records = relationship("ProgressRecord", back_populates="user", foreign_keys="ProgressRecord.user_id")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", foreign_keys="QuizAttempt.user_id")
    generation_requests = relationship(
        "ContentGenerationRequest", back_populates="requester", foreign_keys="ContentGenerationRequest.requester_id"
    )
    approved_artifacts = relationship(
        "ContentGenerationArtifact", back_populates="approver", foreign_keys="ContentGenerationArtifact.approved_by"
    )


# ---------------------------------------------------------------------------
# 2. Course
# ---------------------------------------------------------------------------


class Course(Base):
    """
    A learning course composed of ordered modules.

    Attributes:
        id: UUID primary key.
        title: Short human-readable title.
        description: Rich description shown in the catalogue.
        status: ``"draft"`` until published by an admin.
        difficulty: Audience skill level.
        estimated_duration: Total estimated time in minutes.
        tags: JSON list of keyword tags.
        created_by: FK to :class:`User` who created the course.
        created_at: UTC creation timestamp.
        updated_at: UTC last-modified timestamp.
    """

    __tablename__ = "courses"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: str = sa.Column(sa.String(500), nullable=False)
    description: str = sa.Column(sa.Text, nullable=False)
    status: str = sa.Column(_course_status_enum, nullable=False, default="draft")
    difficulty: str = sa.Column(_difficulty_enum, nullable=False)
    estimated_duration: int = sa.Column(sa.Integer, nullable=False)
    tags: list = sa.Column(JSONList, nullable=False, default=list)
    created_by: str = sa.Column(
        sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    creator = relationship("User", back_populates="courses_created", foreign_keys=[created_by])
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")
    artifacts = relationship(
        "ContentGenerationArtifact", back_populates="course", foreign_keys="ContentGenerationArtifact.course_id"
    )


# ---------------------------------------------------------------------------
# 3. Module
# ---------------------------------------------------------------------------


class Module(Base):
    """
    A logical section of a :class:`Course`, containing lessons and quiz questions.

    Attributes:
        id: UUID primary key.
        course_id: FK to the parent :class:`Course`.
        title: Module heading.
        summary: Short overview paragraph.
        sort_order: Integer position within the course (0-based).
        created_at: UTC creation timestamp.
    """

    __tablename__ = "modules"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    course_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: str = sa.Column(sa.String(500), nullable=False)
    summary: str = sa.Column(sa.Text, nullable=False)
    sort_order: int = sa.Column(sa.Integer, nullable=False, default=0)
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="module", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="module")
    artifacts = relationship(
        "ContentGenerationArtifact", back_populates="module", foreign_keys="ContentGenerationArtifact.module_id"
    )


# ---------------------------------------------------------------------------
# 4. Lesson
# ---------------------------------------------------------------------------


class Lesson(Base):
    """
    A single lesson within a :class:`Module`, containing Markdown content.

    Attributes:
        id: UUID primary key.
        module_id: FK to the parent :class:`Module`.
        title: Lesson heading.
        markdown_content: Full lesson body in Markdown format.
        estimated_minutes: Approximate reading/study time.
        sort_order: Integer position within the module.
        created_at: UTC creation timestamp.
        updated_at: UTC last-modified timestamp.
    """

    __tablename__ = "lessons"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    module_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: str = sa.Column(sa.String(500), nullable=False)
    markdown_content: str = sa.Column(sa.Text, nullable=False, default="")
    estimated_minutes: int = sa.Column(sa.Integer, nullable=False, default=0)
    sort_order: int = sa.Column(sa.Integer, nullable=False, default=0)
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    module = relationship("Module", back_populates="lessons")
    progress_records = relationship("ProgressRecord", back_populates="lesson")
    artifacts = relationship(
        "ContentGenerationArtifact", back_populates="lesson", foreign_keys="ContentGenerationArtifact.lesson_id"
    )


# ---------------------------------------------------------------------------
# 5. QuizQuestion
# ---------------------------------------------------------------------------


class QuizQuestion(Base):
    """
    A multiple-choice question attached to a :class:`Module`.

    Attributes:
        id: UUID primary key.
        module_id: FK to the parent :class:`Module`.
        question: The question text.
        options: JSON list of exactly four answer options.
        correct_answer: The correct option string (must be one of ``options``).
        explanation: Explanation shown after the learner answers.
        created_at: UTC creation timestamp.
    """

    __tablename__ = "quiz_questions"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    module_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question: str = sa.Column(sa.Text, nullable=False)
    options: list = sa.Column(JSONList, nullable=False, default=list)
    correct_answer: str = sa.Column(sa.String(500), nullable=False)
    explanation: str = sa.Column(sa.Text, nullable=False, default="")
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    module = relationship("Module", back_populates="quiz_questions")
    attempts = relationship("QuizAttempt", back_populates="quiz_question")


# ---------------------------------------------------------------------------
# 6. Enrollment
# ---------------------------------------------------------------------------


class Enrollment(Base):
    """
    Records a learner's enrolment in a course and tracks overall completion.

    Attributes:
        id: UUID primary key.
        user_id: FK to the enrolled :class:`User`.
        course_id: FK to the enrolled :class:`Course`.
        enrolled_at: UTC timestamp of enrolment.
        status: ``not_started`` → ``in_progress`` → ``completed``.
        completed_at: UTC completion timestamp; ``None`` until status is ``completed``.
    """

    __tablename__ = "enrollments"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enrolled_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )
    status: str = sa.Column(_enrollment_status_enum, nullable=False, default="not_started")
    completed_at: datetime | None = sa.Column(sa.DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="enrollments", foreign_keys=[user_id])
    course = relationship("Course", back_populates="enrollments", foreign_keys=[course_id])


# ---------------------------------------------------------------------------
# 7. ProgressRecord
# ---------------------------------------------------------------------------


class ProgressRecord(Base):
    """
    Tracks whether a learner has completed a specific lesson.

    Attributes:
        id: UUID primary key.
        user_id: FK to the :class:`User`.
        lesson_id: FK to the :class:`Lesson`.
        module_id: Denormalised FK to the parent :class:`Module` for efficient queries.
        completed: ``True`` once the learner marks the lesson done.
        completed_at: UTC timestamp set when ``completed`` becomes ``True``.
        last_viewed_at: UTC timestamp of the most recent lesson view.
    """

    __tablename__ = "progress_records"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    module_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    completed: bool = sa.Column(sa.Boolean, nullable=False, default=False)
    completed_at: datetime | None = sa.Column(sa.DateTime, nullable=True)
    last_viewed_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="progress_records", foreign_keys=[user_id])
    lesson = relationship("Lesson", back_populates="progress_records", foreign_keys=[lesson_id])
    module = relationship("Module", back_populates="progress_records", foreign_keys=[module_id])


# ---------------------------------------------------------------------------
# 8. QuizAttempt
# ---------------------------------------------------------------------------


class QuizAttempt(Base):
    """
    Records a single learner attempt at a :class:`QuizQuestion`.

    Multiple attempts per question are allowed; each is stored independently.

    Attributes:
        id: UUID primary key.
        user_id: FK to the attempting :class:`User`.
        quiz_question_id: FK to the :class:`QuizQuestion`.
        selected_answer: The answer option chosen by the learner.
        is_correct: ``True`` if ``selected_answer`` matches ``correct_answer``.
        attempted_at: UTC timestamp of the attempt.
    """

    __tablename__ = "quiz_attempts"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quiz_question_id: str = sa.Column(
        sa.String(36),
        sa.ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_answer: str = sa.Column(sa.String(500), nullable=False)
    is_correct: bool = sa.Column(sa.Boolean, nullable=False, default=False)
    attempted_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="quiz_attempts", foreign_keys=[user_id])
    quiz_question = relationship("QuizQuestion", back_populates="attempts", foreign_keys=[quiz_question_id])


# ---------------------------------------------------------------------------
# 9. ContentGenerationRequest
# ---------------------------------------------------------------------------


class ContentGenerationRequest(Base):
    """
    Audit record for a single AI content generation request.

    Tracks the full lifecycle from ``pending`` through to ``completed`` or
    ``failed`` so admins can inspect generation history.

    Attributes:
        id: UUID primary key.
        prompt: The raw prompt string sent to the AI model.
        model: Identifier of the model used (e.g. ``"gpt-4o"``).
        requester_id: FK to the admin :class:`User` who triggered generation.
        status: ``pending`` → ``in_progress`` → ``completed`` | ``failed``.
        created_at: UTC creation timestamp.
        updated_at: UTC last-modified timestamp.
    """

    __tablename__ = "content_generation_requests"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    prompt: str = sa.Column(sa.Text, nullable=False)
    model: str = sa.Column(sa.String(100), nullable=False)
    requester_id: str = sa.Column(
        sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: str = sa.Column(_generation_status_enum, nullable=False, default="pending")
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    requester = relationship(
        "User", back_populates="generation_requests", foreign_keys=[requester_id]
    )
    artifacts = relationship(
        "ContentGenerationArtifact", back_populates="source_request"
    )


# ---------------------------------------------------------------------------
# 10. ContentGenerationArtifact
# ---------------------------------------------------------------------------


class ContentGenerationArtifact(Base):
    """
    A single piece of AI-generated content awaiting admin review.

    An artifact can optionally be associated with an existing :class:`Course`,
    :class:`Module`, or :class:`Lesson` — for example when regenerating a
    specific section.  All three foreign keys are nullable.

    Attributes:
        id: UUID primary key.
        generated_content: The raw AI-generated text (Markdown).
        source_request_id: FK to the originating :class:`ContentGenerationRequest`.
        approved_by: FK to the admin :class:`User` who approved; ``None`` if pending.
        approved_at: UTC timestamp of approval; ``None`` if not yet approved.
        course_id: Optional FK to an associated :class:`Course`.
        module_id: Optional FK to an associated :class:`Module`.
        lesson_id: Optional FK to an associated :class:`Lesson`.
        created_at: UTC creation timestamp.
    """

    __tablename__ = "content_generation_artifacts"

    id: str = sa.Column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    generated_content: str = sa.Column(sa.Text, nullable=False)
    source_request_id: str = sa.Column(
        sa.String(36),
        sa.ForeignKey("content_generation_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approved_by: str | None = sa.Column(
        sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: datetime | None = sa.Column(sa.DateTime, nullable=True)
    course_id: str | None = sa.Column(
        sa.String(36), sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True
    )
    module_id: str | None = sa.Column(
        sa.String(36), sa.ForeignKey("modules.id", ondelete="SET NULL"), nullable=True
    )
    lesson_id: str | None = sa.Column(
        sa.String(36), sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
    created_at: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    source_request = relationship("ContentGenerationRequest", back_populates="artifacts")
    approver = relationship(
        "User", back_populates="approved_artifacts", foreign_keys=[approved_by]
    )
    course = relationship(
        "Course", back_populates="artifacts", foreign_keys=[course_id]
    )
    module = relationship(
        "Module", back_populates="artifacts", foreign_keys=[module_id]
    )
    lesson = relationship(
        "Lesson", back_populates="artifacts", foreign_keys=[lesson_id]
    )


__all__ = [
    "User",
    "Course",
    "Module",
    "Lesson",
    "QuizQuestion",
    "Enrollment",
    "ProgressRecord",
    "QuizAttempt",
    "ContentGenerationRequest",
    "ContentGenerationArtifact",
]
