import pytest
from pydantic import ValidationError

from backend.app.ai.analyzer import EmailAnalysis


def test_valid_email_analysis():
    result = EmailAnalysis(
        category="needs_action",
        importance_score=90,
        confidence=0.95,
        reason="The email asks the recipient to complete a task.",
        deadline="2026-11-05",
        requires_reply=True,
        suspicious=False,
    )

    assert result.category == "needs_action"
    assert result.importance_score == 90
    assert result.confidence == 0.95
    assert result.requires_reply is True
    assert result.suspicious is False


def test_importance_score_must_be_between_0_and_100():
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category="important",
            importance_score=101,
            confidence=0.9,
            reason="Test",
            requires_reply=False,
            suspicious=False,
        )


def test_confidence_must_be_between_0_and_1():
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category="fyi",
            importance_score=50,
            confidence=1.5,
            reason="Test",
            requires_reply=False,
            suspicious=False,
        )