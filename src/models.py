"""SQLAlchemy ORM models for the Learning Platform.

All models inherit from ``Base`` (defined in ``src.database``) so that
``Base.metadata`` aggregates every table for schema creation and migrations.

Domain hierarchy:
    User
    Course → Module[] → Lesson[] + QuizQuestion[]
    Enrollment (User ↔ Course)
    ProgressRecord (User ↔ Lesson)
    QuizAttempt (User ↔ QuizQuestion)
    ContentGenerationRequest → ContentGenerationArtifact
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base, JSONList


# ---------------------------------------------------------------------------
# Enum types
# ---------------------------------------------------------------------------


class UserRole(str, enum.Enum):
    """Roles available to platform users."""

    learner = "learner"
    admin = "admin"


class CourseStatus(str, enum.Enum):
    """Publication status of a course."""

    draft = "draft"
    published = "published"


class EnrollmentStatus(str, enum.Enum):
    """Progress status of a learner's enrollment in a course."""

    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class ContentGenerationStatus(str, enum.Enum):
    """Lifecycle status of an AI content-generation request."""

    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


# ---------------------------------------------------------------------------
# 1. User
# ---------------------------------------------------------------------------


class User(Base):
    """Platform user — either a learner or an administrator."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole"), nullable=False, default=UserRole.learner
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    courses: Mapped[list["Course"]] = relationship(
        "Course", back_populates="creator", foreign_keys="Course.created_by"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="user"
    )
    progress_records: Mapped[list["ProgressRecord"]] = relationship(
        "ProgressRecord", back_populates="user"
    )
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="user"
    )
    generation_requests: Mapped[list["ContentGenerationRequest"]] = relationship(
        "ContentGenerationRequest", back_populates="requester"
    )
    approved_artifacts: Mapped[list["ContentGenerationArtifact"]] = relationship(
        "ContentGenerationArtifact",
        back_populates="approver",
        foreign_keys="ContentGenerationArtifact.approved_by",
    )


# ---------------------------------------------------------------------------
# 2. Course
# ---------------------------------------------------------------------------


class Course(Base):
    """A course composed of ordered modules."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[CourseStatus] = mapped_column(
        SAEnum(CourseStatus, name="coursestatus"),
        nullable=False,
        default=CourseStatus.draft,
    )
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False, default="beginner")
    estimated_duration: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Total estimated duration in minutes"
    )
    # None is intentional: courses may be created without tags.
    # JSONList preserves None as SQL NULL; an empty list serialises as "[]".
    tags: Mapped[list[str] | None] = mapped_column(JSONList, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", back_populates="courses", foreign_keys=[created_by]
    )
    modules: Mapped[list["Module"]] = relationship(
        "Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.sort_order"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="course"
    )
    artifacts: Mapped[list["ContentGenerationArtifact"]] = relationship(
        "ContentGenerationArtifact", back_populates="course", foreign_keys="ContentGenerationArtifact.course_id"
    )


# ---------------------------------------------------------------------------
# 3. Module
# ---------------------------------------------------------------------------


class Module(Base):
    """An ordered module within a course, containing lessons and quiz questions."""

    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.sort_order"
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion", back_populates="module", cascade="all, delete-orphan"
    )
    progress_records: Mapped[list["ProgressRecord"]] = relationship(
        "ProgressRecord", back_populates="module"
    )
    artifacts: Mapped[list["ContentGenerationArtifact"]] = relationship(
        "ContentGenerationArtifact", back_populates="module", foreign_keys="ContentGenerationArtifact.module_id"
    )


# ---------------------------------------------------------------------------
# 4. Lesson
# ---------------------------------------------------------------------------


class Lesson(Base):
    """An individual lesson within a module; content is stored as Markdown."""

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="lessons")
    progress_records: Mapped[list["ProgressRecord"]] = relationship(
        "ProgressRecord", back_populates="lesson"
    )
    artifacts: Mapped[list["ContentGenerationArtifact"]] = relationship(
        "ContentGenerationArtifact", back_populates="lesson", foreign_keys="ContentGenerationArtifact.lesson_id"
    )


# ---------------------------------------------------------------------------
# 5. QuizQuestion
# ---------------------------------------------------------------------------


class QuizQuestion(Base):
    """A multiple-choice quiz question associated with a module."""

    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSONList, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="quiz_questions")
    attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="quiz_question"
    )


# ---------------------------------------------------------------------------
# 6. Enrollment
# ---------------------------------------------------------------------------


class Enrollment(Base):
    """Records a learner's enrollment in a course."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(EnrollmentStatus, name="enrollmentstatus"),
        nullable=False,
        default=EnrollmentStatus.not_started,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")


# ---------------------------------------------------------------------------
# 7. ProgressRecord
# ---------------------------------------------------------------------------


class ProgressRecord(Base):
    """Tracks a learner's completion of an individual lesson."""

    __tablename__ = "progress_records"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="progress_records")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress_records")
    module: Mapped["Module"] = relationship("Module", back_populates="progress_records")


# ---------------------------------------------------------------------------
# 8. QuizAttempt
# ---------------------------------------------------------------------------


class QuizAttempt(Base):
    """Records a learner's single attempt at a quiz question."""

    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quiz_question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    selected_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    quiz_question: Mapped["QuizQuestion"] = relationship(
        "QuizQuestion", back_populates="attempts"
    )


# ---------------------------------------------------------------------------
# 9. ContentGenerationRequest
# ---------------------------------------------------------------------------


class ContentGenerationRequest(Base):
    """Represents an AI content-generation job submitted by an admin."""

    __tablename__ = "content_generation_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="gpt-4o")
    requester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[ContentGenerationStatus] = mapped_column(
        SAEnum(ContentGenerationStatus, name="contentgenerationstatus"),
        nullable=False,
        default=ContentGenerationStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    requester: Mapped["User"] = relationship("User", back_populates="generation_requests")
    artifacts: Mapped[list["ContentGenerationArtifact"]] = relationship(
        "ContentGenerationArtifact", back_populates="source_request"
    )


# ---------------------------------------------------------------------------
# 10. ContentGenerationArtifact
# ---------------------------------------------------------------------------


class ContentGenerationArtifact(Base):
    """Stores the raw output of a completed AI generation request.

    An artifact may optionally be linked to an existing course, module,
    or lesson once an admin reviews and approves the generated content.
    """

    __tablename__ = "content_generation_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    generated_content: Mapped[str] = mapped_column(Text, nullable=False)
    source_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("content_generation_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approved_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    course_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True
    )
    module_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True
    )
    lesson_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    source_request: Mapped["ContentGenerationRequest"] = relationship(
        "ContentGenerationRequest", back_populates="artifacts"
    )
    approver: Mapped["User | None"] = relationship(
        "User", back_populates="approved_artifacts", foreign_keys=[approved_by]
    )
    course: Mapped["Course | None"] = relationship(
        "Course", back_populates="artifacts", foreign_keys=[course_id]
    )
    module: Mapped["Module | None"] = relationship(
        "Module", back_populates="artifacts", foreign_keys=[module_id]
    )
    lesson: Mapped["Lesson | None"] = relationship(
        "Lesson", back_populates="artifacts", foreign_keys=[lesson_id]
    )
