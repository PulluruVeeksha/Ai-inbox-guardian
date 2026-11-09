
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from backend.app.ai.email_processor import process_email


@patch("backend.app.ai.email_processor.analyze_email")
@patch("backend.app.ai.email_processor.extract_email_body")
@patch("backend.app.ai.email_processor.extract_message_metadata")
@patch("backend.app.ai.email_processor.get_message")
def test_process_email_success(
    mock_get_message,
    mock_metadata,
    mock_body,
    mock_analyze,
):
    mock_get_message.return_value = {"id": "test-123"}

    mock_metadata.return_value = {
        "id": "test-123",
        "thread_id": "thread-123",
        "sender": "sender@example.com",
        "recipient": "user@example.com",
        "subject": "Project update",
        "date": "2026-11-09",
        "snippet": "Please review the update.",
    }

    mock_body.return_value = "Please review the project update."

    mock_analyze.return_value = SimpleNamespace(
        model_dump=lambda mode: {
            "category": "needs_action",
            "importance_score": 80,
            "confidence": 0.95,
            "reason": "The email requests a review.",
            "deadline": None,
            "requires_reply": False,
            "suspicious": False,
        }
    )

    result = process_email("test-123")

    assert result["email"]["id"] == "test-123"
    assert result["analysis"]["category"] == "needs_action"
    assert result["analysis"]["importance_score"] == 80
    assert result["action_status"] == "pending_user_approval"

    mock_get_message.assert_called_once_with("test-123")
    mock_analyze.assert_called_once()


@patch("backend.app.ai.email_processor.get_message")
def test_process_email_rejects_empty_message_id(mock_get_message):
    with pytest.raises(ValueError, match="Message ID cannot be empty"):
        process_email("")

    mock_get_message.assert_not_called()


@patch("backend.app.ai.email_processor.analyze_email")
@patch("backend.app.ai.email_processor.extract_email_body")
@patch("backend.app.ai.email_processor.extract_message_metadata")
@patch("backend.app.ai.email_processor.get_message")
def test_process_email_rejects_empty_body(
    mock_get_message,
    mock_metadata,
    mock_body,
    mock_analyze,
):
    mock_get_message.return_value = {"id": "test-123"}
    mock_metadata.return_value = {"id": "test-123"}
    mock_body.return_value = ""

    with pytest.raises(ValueError, match="no readable plain-text body"):
        process_email("test-123")

    mock_analyze.assert_not_called()
