"""API tests for the Progress Tracking service.

Covers enrollment, lesson view/complete, course progress summary,
and quiz submission.

Traceability:
    BRD-FR-014: Admin/learner enrollment
    BRD-FR-015: Learner self-enrollment
    BRD-FR-016: Enrollment status transitions
    BRD-FR-017: Progress records
    BRD-FR-019: Course completion percentage
    BRD-FR-020: Quiz submission and scoring
    BRD-FR-004: Learner can only see own progress
    TASK-021: Progress router
"""

from httpx import AsyncClient

from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# POST /api/v1/progress/enroll
# ---------------------------------------------------------------------------


async def test_learner_enroll_in_published_course_returns_201(
    client: AsyncClient, learner_user, published_course
):
    """Learner enrolling in a published course returns 201. [BRD-FR-015]"""
    resp = await client.post(
        "/api/v1/progress/enroll",
        json={"course_id": published_course.id},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["course_id"] == published_course.id
    assert data["user_id"] == learner_user["user"].id
    assert data["status"] == "not_started"


async def test_learner_duplicate_enrollment_returns_400(
    client: AsyncClient, learner_user, enrollment
):
    """Duplicate enrollment returns 400 Bad Request. [BRD-FR-015]"""
    resp = await client.post(
        "/api/v1/progress/enroll",
        json={"course_id": enrollment.course_id},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 400


async def test_enroll_unauthenticated_returns_401(
    client: AsyncClient, published_course
):
    """Unauthenticated enrollment returns 401."""
    resp = await client.post(
        "/api/v1/progress/enroll",
        json={"course_id": published_course.id},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/progress/enrollments
# ---------------------------------------------------------------------------


async def test_list_enrollments_returns_user_enrollments(
    client: AsyncClient, learner_user, enrollment
):
    """List enrollments returns learner's own enrollments. [BRD-FR-004]"""
    resp = await client.get(
        "/api/v1/progress/enrollments",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    ids = [e["id"] for e in resp.json()]
    assert enrollment.id in ids


async def test_list_enrollments_does_not_return_others_enrollments(
    client: AsyncClient, second_learner_user, enrollment
):
    """Learner cannot see other learners' enrollments. [BRD-FR-004]"""
    resp = await client.get(
        "/api/v1/progress/enrollments",
        headers=auth_headers(second_learner_user["token"]),
    )
    assert resp.status_code == 200
    ids = [e["id"] for e in resp.json()]
    assert enrollment.id not in ids


async def test_list_enrollments_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated enrollment listing returns 401."""
    resp = await client.get("/api/v1/progress/enrollments")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/progress/enrollments/{enrollment_id}
# ---------------------------------------------------------------------------


async def test_get_enrollment_detail_returns_correct_enrollment(
    client: AsyncClient, learner_user, enrollment
):
    """Learner can get details of their own enrollment. [BRD-FR-004]"""
    resp = await client.get(
        f"/api/v1/progress/enrollments/{enrollment.id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == enrollment.id
    assert data["user_id"] == learner_user["user"].id


async def test_get_enrollment_belonging_to_another_user_returns_404(
    client: AsyncClient, second_learner_user, enrollment
):
    """Learner cannot access another user's enrollment. [BRD-FR-004]"""
    resp = await client.get(
        f"/api/v1/progress/enrollments/{enrollment.id}",
        headers=auth_headers(second_learner_user["token"]),
    )
    assert resp.status_code == 404


async def test_get_nonexistent_enrollment_returns_404(
    client: AsyncClient, learner_user
):
    """Non-existent enrollment ID returns 404."""
    resp = await client.get(
        "/api/v1/progress/enrollments/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/progress/lessons/{lesson_id}/view
# ---------------------------------------------------------------------------


async def test_record_lesson_view_returns_progress_record(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Recording a lesson view creates a progress record. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]
    resp = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/view",
        json={"module_id": module.id},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["lesson_id"] == lesson.id
    assert data["user_id"] == learner_user["user"].id
    assert data["completed"] is False
    assert "last_viewed_at" in data


async def test_record_lesson_view_twice_updates_last_viewed_at(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Viewing a lesson twice updates last_viewed_at (idempotent upsert). [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]
    body = {"module_id": module.id}
    resp1 = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/view",
        json=body,
        headers=auth_headers(learner_user["token"]),
    )
    resp2 = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/view",
        json=body,
        headers=auth_headers(learner_user["token"]),
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # Should return the same progress record (same id)
    assert resp1.json()["id"] == resp2.json()["id"]


async def test_record_lesson_view_unauthenticated_returns_401(
    client: AsyncClient, course_with_lesson
):
    """Unauthenticated lesson view recording returns 401."""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]
    resp = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/view",
        json={"module_id": module.id},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/progress/lessons/{lesson_id}/complete
# ---------------------------------------------------------------------------


async def test_complete_lesson_sets_completed_flag(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Completing a lesson marks it as completed with a timestamp. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    resp = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/complete",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["completed"] is True
    assert data["completed_at"] is not None
    assert data["lesson_id"] == lesson.id


async def test_complete_lesson_is_idempotent(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Completing a lesson twice does not change completed_at. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    resp1 = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/complete",
        headers=auth_headers(learner_user["token"]),
    )
    resp2 = await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/complete",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # completed_at should be the same on both calls
    assert resp1.json()["completed_at"] == resp2.json()["completed_at"]


# ---------------------------------------------------------------------------
# GET /api/v1/progress/lessons/{lesson_id}
# ---------------------------------------------------------------------------


async def test_get_lesson_progress_returns_record(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Getting lesson progress returns the progress record. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    module = course_with_lesson["module"]
    # Create a record first
    await client.post(
        f"/api/v1/progress/lessons/{lesson.id}/view",
        json={"module_id": module.id},
        headers=auth_headers(learner_user["token"]),
    )
    resp = await client.get(
        f"/api/v1/progress/lessons/{lesson.id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["lesson_id"] == lesson.id


async def test_get_lesson_progress_no_record_returns_404(
    client: AsyncClient, learner_user, course_with_lesson
):
    """Getting progress for a lesson never viewed returns 404. [BRD-FR-017]"""
    lesson = course_with_lesson["lesson"]
    resp = await client.get(
        f"/api/v1/progress/lessons/{lesson.id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/progress/courses/{course_id}
# ---------------------------------------------------------------------------


async def test_get_course_progress_returns_summary(
    client: AsyncClient, learner_user, enrollment
):
    """Course progress endpoint returns a summary. [BRD-FR-019]"""
    resp = await client.get(
        f"/api/v1/progress/courses/{enrollment.course_id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["course_id"] == enrollment.course_id
    assert "progress_percentage" in data
    assert "total_lessons" in data
    assert "completed_lessons" in data
    assert "enrollment_status" in data
    assert 0.0 <= data["progress_percentage"] <= 100.0


async def test_get_course_progress_not_enrolled_returns_summary(
    client: AsyncClient, learner_user, published_course
):
    """Course progress for unenrolled course returns 0% progress. [BRD-FR-019]"""
    resp = await client.get(
        f"/api/v1/progress/courses/{published_course.id}",
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["progress_percentage"] == 0.0


# ---------------------------------------------------------------------------
# POST /api/v1/progress/quiz — Quiz submission
# ---------------------------------------------------------------------------


async def test_submit_correct_quiz_answer_returns_is_correct_true(
    client: AsyncClient, learner_user, course_with_quiz
):
    """Submitting the correct answer returns is_correct=True. [BRD-FR-020]"""
    question = course_with_quiz["question"]
    resp = await client.post(
        "/api/v1/progress/quiz",
        json={"quiz_question_id": question.id, "selected_answer": "4"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_correct"] is True
    assert data["quiz_question_id"] == question.id
    assert data["selected_answer"] == "4"


async def test_submit_wrong_quiz_answer_returns_is_correct_false(
    client: AsyncClient, learner_user, course_with_quiz
):
    """Submitting a wrong answer returns is_correct=False. [BRD-FR-020]"""
    question = course_with_quiz["question"]
    resp = await client.post(
        "/api/v1/progress/quiz",
        json={"quiz_question_id": question.id, "selected_answer": "2"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 201
    assert resp.json()["is_correct"] is False


async def test_submit_quiz_nonexistent_question_returns_404(
    client: AsyncClient, learner_user
):
    """Submitting an answer for a non-existent question returns 404."""
    resp = await client.post(
        "/api/v1/progress/quiz",
        json={
            "quiz_question_id": "00000000-0000-0000-0000-000000000000",
            "selected_answer": "4",
        },
        headers=auth_headers(learner_user["token"]),
    )
    assert resp.status_code == 404


async def test_submit_quiz_unauthenticated_returns_401(
    client: AsyncClient, course_with_quiz
):
    """Unauthenticated quiz submission returns 401."""
    question = course_with_quiz["question"]
    resp = await client.post(
        "/api/v1/progress/quiz",
        json={"quiz_question_id": question.id, "selected_answer": "4"},
    )
    assert resp.status_code == 401


async def test_multiple_quiz_attempts_are_stored_independently(
    client: AsyncClient, learner_user, course_with_quiz
):
    """Multiple quiz attempts are recorded separately. [BRD-FR-020]"""
    question = course_with_quiz["question"]
    resp1 = await client.post(
        "/api/v1/progress/quiz",
        json={"quiz_question_id": question.id, "selected_answer": "1"},
        headers=auth_headers(learner_user["token"]),
    )
    resp2 = await client.post(
        "/api/v1/progress/quiz",
        json={"quiz_question_id": question.id, "selected_answer": "4"},
        headers=auth_headers(learner_user["token"]),
    )
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["id"] != resp2.json()["id"]
    assert resp1.json()["is_correct"] is False
    assert resp2.json()["is_correct"] is True
