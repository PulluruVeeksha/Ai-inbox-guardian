
from unittest.mock import patch

from fastapi.testclient import TestClient

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


def test_synthetic_email_analysis():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "Project review required",
            "body": "Please review the report before the deadline.",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["analysis_mode"] == "mock"
    assert result["analysis"]["category"] == "needs_action"
    assert result["analysis"]["suspicious"] is False
    assert result["action_status"] == "pending_user_approval"


def test_synthetic_email_detects_suspicious_content():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "Urgent: Verify your account",
            "body": "Your password must be verified immediately.",
        },
    )

    assert response.status_code == 200
    assert response.json()["analysis"]["category"] == "suspicious"
    assert response.json()["analysis"]["suspicious"] is True


@patch("backend.app.main.APP_ENV", "production")
def test_synthetic_endpoint_disabled_outside_development():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "Test",
            "body": "Sample email.",
        },
    )

    assert response.status_code == 404


def test_synthetic_email_rejects_empty_subject():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "",
            "body": "This is a sample email.",
        },
    )

    assert response.status_code == 422


def test_synthetic_email_rejects_empty_body():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "Sample email",
            "body": "",
        },
    )

    assert response.status_code == 422


def test_synthetic_email_rejects_oversized_subject():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "A" * 201,
            "body": "Sample email.",
        },
    )

    assert response.status_code == 422


def test_synthetic_email_rejects_oversized_body():
    response = client.post(
        "/dev/analyze-synthetic",
        json={
            "subject": "Sample email",
            "body": "A" * 5001,
        },
    )

    assert response.status_code == 422
