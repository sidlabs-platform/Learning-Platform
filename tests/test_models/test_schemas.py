"""Unit tests for Pydantic v2 schema validation.

Covers field validation, enum constraints, and domain invariants.

Traceability:
    BRD-FR-002: Role enum validation
    BRD-FR-010: Course required fields
    BRD-FR-011: Lesson fields
    BRD-FR-012: Quiz question options/answer constraints
    TASK-008: Pydantic schema definitions
"""

import pytest
from pydantic import ValidationError

from src.auth.schemas import UserCreate, UserLogin, UserRole
from src.course_management.schemas import (
    CourseCreate,
    CourseUpdate,
    DifficultyLevel,
    LessonCreate,
    ModuleCreate,
    QuizQuestionCreate,
)
from src.progress.schemas import (
    EnrollmentCreate,
    EnrollmentStatus,
    QuizSubmission,
)
from src.reporting.schemas import CSVExportRequest, ReportType
from src.ai_generation.schemas import GenerationRequest, GenerationStatus


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------


class TestUserCreate:
    def test_valid_user_create(self):
        """Valid UserCreate schema parses correctly. [BRD-FR-002]"""
        user = UserCreate(
            name="Alice",
            email="alice@example.com",
            password="SecurePass1!",
            role=UserRole.learner,
        )
        assert user.name == "Alice"
        assert user.role == UserRole.learner

    def test_default_role_is_learner(self):
        """Default role is learner. [BRD-FR-002]"""
        user = UserCreate(
            name="Bob",
            email="bob@example.com",
            password="SecurePass1!",
        )
        assert user.role == UserRole.learner

    def test_invalid_email_raises_validation_error(self):
        """Invalid email raises ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(name="Carol", email="not-an-email", password="pass")

    def test_invalid_role_raises_validation_error(self):
        """Unknown role raises ValidationError. [BRD-FR-002]"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="Dan",
                email="dan@example.com",
                password="pass",
                role="superuser",
            )

    def test_missing_required_fields_raises_validation_error(self):
        """Missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(name="Eve")


class TestUserRole:
    def test_learner_role_value(self):
        """Learner role has correct string value. [BRD-FR-002]"""
        assert UserRole.learner.value == "learner"

    def test_admin_role_value(self):
        """Admin role has correct string value. [BRD-FR-002]"""
        assert UserRole.admin.value == "admin"

    def test_only_two_roles_exist(self):
        """Only learner and admin roles exist. [BRD-FR-002]"""
        role_values = {r.value for r in UserRole}
        assert role_values == {"learner", "admin"}


# ---------------------------------------------------------------------------
# Course schemas
# ---------------------------------------------------------------------------


class TestCourseCreate:
    def test_valid_course_create(self):
        """Valid CourseCreate schema parses correctly. [BRD-FR-010]"""
        course = CourseCreate(
            title="GitHub Actions",
            description="Learn to automate workflows.",
            difficulty=DifficultyLevel.beginner,
            estimated_duration=120,
            tags=["github", "ci-cd"],
        )
        assert course.title == "GitHub Actions"
        assert course.difficulty == DifficultyLevel.beginner
        assert len(course.tags) == 2

    def test_tags_default_to_empty_list(self):
        """Tags default to empty list. [BRD-FR-010]"""
        course = CourseCreate(
            title="No Tags",
            description="A course.",
            difficulty=DifficultyLevel.advanced,
            estimated_duration=60,
        )
        assert course.tags == []

    def test_missing_required_field_raises_error(self):
        """Missing required course fields raise ValidationError. [BRD-FR-010]"""
        with pytest.raises(ValidationError):
            CourseCreate(title="Only Title")

    def test_invalid_difficulty_raises_error(self):
        """Invalid difficulty raises ValidationError."""
        with pytest.raises(ValidationError):
            CourseCreate(
                title="Bad Difficulty",
                description="Test.",
                difficulty="expert",
                estimated_duration=60,
            )


class TestDifficultyLevel:
    def test_all_three_levels_exist(self):
        """All three difficulty levels exist. [BRD-FR-010]"""
        values = {d.value for d in DifficultyLevel}
        assert "beginner" in values
        assert "intermediate" in values
        assert "advanced" in values


class TestCourseUpdate:
    def test_all_optional_fields(self):
        """CourseUpdate allows partial updates (all fields optional)."""
        update = CourseUpdate()
        assert update.title is None
        assert update.description is None
        assert update.difficulty is None

    def test_single_field_update(self):
        """Only title is changed in a partial update."""
        update = CourseUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.description is None


# ---------------------------------------------------------------------------
# Module schemas
# ---------------------------------------------------------------------------


class TestModuleCreate:
    def test_valid_module_create(self):
        """Valid ModuleCreate schema parses correctly. [BRD-FR-009]"""
        module = ModuleCreate(title="Module 1", summary="Intro module.", sort_order=0)
        assert module.title == "Module 1"
        assert module.sort_order == 0

    def test_missing_fields_raises_error(self):
        """Missing required module fields raise ValidationError."""
        with pytest.raises(ValidationError):
            ModuleCreate(title="No Summary")


# ---------------------------------------------------------------------------
# Lesson schemas
# ---------------------------------------------------------------------------


class TestLessonCreate:
    def test_valid_lesson_create(self):
        """Valid LessonCreate schema parses correctly. [BRD-FR-011]"""
        lesson = LessonCreate(
            title="Intro to Git",
            markdown_content="# Git\nGit is a VCS.",
            estimated_minutes=15,
            sort_order=0,
        )
        assert lesson.title == "Intro to Git"
        assert lesson.estimated_minutes == 15


# ---------------------------------------------------------------------------
# Quiz schemas
# ---------------------------------------------------------------------------


class TestQuizQuestionCreate:
    def test_valid_quiz_question(self):
        """Valid QuizQuestionCreate parses correctly. [BRD-FR-012]"""
        q = QuizQuestionCreate(
            question="What is Git?",
            options=["A VCS", "A language", "An IDE", "A cloud"],
            correct_answer="A VCS",
            explanation="Git is a distributed VCS.",
        )
        assert q.correct_answer == "A VCS"
        assert len(q.options) == 4

    def test_correct_answer_not_in_options_raises_error(self):
        """correct_answer not in options raises ValidationError. [BRD-FR-012]"""
        with pytest.raises(ValidationError):
            QuizQuestionCreate(
                question="What is Git?",
                options=["A VCS", "A language"],
                correct_answer="A framework",
                explanation="It's a VCS.",
            )

    def test_correct_answer_in_options_passes(self):
        """correct_answer matching an option passes validation."""
        q = QuizQuestionCreate(
            question="Which is correct?",
            options=["A", "B", "C"],
            correct_answer="B",
            explanation="B is correct.",
        )
        assert q.correct_answer == "B"


# ---------------------------------------------------------------------------
# Progress schemas
# ---------------------------------------------------------------------------


class TestEnrollmentStatus:
    def test_all_three_statuses_exist(self):
        """All three enrollment statuses exist. [BRD-FR-016]"""
        values = {s.value for s in EnrollmentStatus}
        assert "not_started" in values
        assert "in_progress" in values
        assert "completed" in values


class TestQuizSubmission:
    def test_valid_quiz_submission(self):
        """Valid QuizSubmission parses correctly."""
        sub = QuizSubmission(
            quiz_question_id="some-uuid",
            selected_answer="Option A",
        )
        assert sub.quiz_question_id == "some-uuid"
        assert sub.selected_answer == "Option A"


# ---------------------------------------------------------------------------
# Reporting schemas
# ---------------------------------------------------------------------------


class TestReportType:
    def test_all_report_types_exist(self):
        """All report types exist. [BRD-FR-025]"""
        values = {r.value for r in ReportType}
        assert "enrollments" in values
        assert "learner_progress" in values
        assert "quiz_results" in values


class TestCSVExportRequest:
    def test_default_report_type_is_enrollments(self):
        """Default report type is enrollments. [BRD-FR-026]"""
        req = CSVExportRequest()
        assert req.report_type == ReportType.enrollments


# ---------------------------------------------------------------------------
# AI generation schemas
# ---------------------------------------------------------------------------


class TestGenerationRequest:
    def test_valid_generation_request(self):
        """Valid GenerationRequest parses correctly. [BRD-FR-029]"""
        req = GenerationRequest(
            topic="GitHub Actions",
            target_audience="Developers",
            learning_objectives=["Understand CI/CD"],
            difficulty=DifficultyLevel.beginner,
        )
        assert req.topic == "GitHub Actions"
        assert req.desired_module_count == 3
        assert req.preferred_tone == "professional"

    def test_missing_required_fields_raises_error(self):
        """Missing required generation fields raise ValidationError."""
        with pytest.raises(ValidationError):
            GenerationRequest(topic="GitHub Actions")


class TestGenerationStatus:
    def test_all_statuses_exist(self):
        """All generation statuses exist."""
        values = {s.value for s in GenerationStatus}
        assert "pending" in values
        assert "in_progress" in values
        assert "completed" in values
        assert "failed" in values
