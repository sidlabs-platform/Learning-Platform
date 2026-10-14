"""Structural checks for the starter course seed data."""

import os

import pytest

# Importing src.seed loads app settings, which require these env vars.
os.environ.setdefault("GITHUB_MODELS_API_KEY", "test-key")
os.environ.setdefault("GITHUB_MODELS_ENDPOINT", "https://models.example.test")
os.environ.setdefault("SECRET_KEY", "x" * 32)

from src.seed import COURSES  # noqa: E402


@pytest.mark.parametrize("course", COURSES, ids=lambda c: c["title"])
def test_course_structure(course: dict) -> None:
    """Each course has 3–5 modules, 1–3 lessons per module and valid quiz answers."""
    assert 3 <= len(course["modules"]) <= 5
    assert any(m["quiz_questions"] for m in course["modules"])
    for module in course["modules"]:
        assert 1 <= len(module["lessons"]) <= 3
        for lesson in module["lessons"]:
            assert lesson["markdown_content"].strip()
        for q in module["quiz_questions"]:
            assert q["correct_answer"] in q["options"]


def test_copilot_course_covers_auto_mode_and_hydrafusion() -> None:
    """The GitHub Copilot course teaches Auto mode routing and HydraFusion."""
    course = next(c for c in COURSES if c["title"] == "GitHub Copilot")
    content = " ".join(
        lesson["markdown_content"]
        for module in course["modules"]
        for lesson in module["lessons"]
    )
    for term in ("Auto", "Efficiency", "Balance", "Intelligence", "HydraFusion", "Cascade", "Critique"):
        assert term in content


def test_hydrafusion_safety_and_client_eligibility() -> None:
    """Keep preview safety guarantees and plan eligibility scoped accurately."""
    course = next(c for c in COURSES if c["title"] == "GitHub Copilot")
    overview = course["modules"][1]["lessons"][0]["markdown_content"]
    setup = course["modules"][2]["lessons"][0]["markdown_content"]

    assert "no patch is applied if a workflow is cancelled or fails validation" in overview
    assert "all Copilot plans through Copilot CLI, including Free" in setup
    assert (
        "In VS Code and the GitHub Copilot app, it is available to Copilot Pro, Pro+, "
        "Business, and Enterprise users"
    ) in setup
    assert "an administrator must allow preview features" in setup
