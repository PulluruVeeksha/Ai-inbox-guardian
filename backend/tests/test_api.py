
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.app.main import app


client = TestClient(app)


@patch("backend.app.main.process_email")
def test_analyze_email_success(mock_process_email):
    mock_process_email.return_value = {
        "email": {
            "id": "test-123",
            "subject": "Project update",
        },
        "analysis": {
            "category": "needs_action",
            "importance_score": 80,
            "confidence": 0.95,
            "reason": "The email requests a review.",
            "deadline": None,
            "requires_reply": False,
            "suspicious": False,
        },
        "action_status": "pending_user_approval",
    }

    response = client.post(
        "/emails/analyze",
        json={"message_id": "test-123"},
    )

    assert response.status_code == 200
    assert response.json()["analysis"]["category"] == "needs_action"
    assert response.json()["action_status"] == "pending_user_approval"

    mock_process_email.assert_called_once_with("test-123")


def test_analyze_email_rejects_empty_message_id():
    response = client.post(
        "/emails/analyze",
        json={"message_id": ""},
    )

    assert response.status_code == 422


def test_analyze_email_requires_message_id():
    response = client.post(
        "/emails/analyze",
        json={},
    )

    assert response.status_code == 422


@patch("backend.app.main.process_email")
def test_analyze_email_handles_unavailable_service(mock_process_email):
    mock_process_email.side_effect = RuntimeError("Service unavailable")

    response = client.post(
        "/emails/analyze",
        json={"message_id": "test-123"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Email analysis is temporarily unavailable."
    )
