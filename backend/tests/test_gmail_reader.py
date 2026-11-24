from backend.app.gmail.reader import extract_message_metadata


def test_extract_message_metadata():
    message = {
        "id": "test-message-id",
        "threadId": "test-thread-id",
        "snippet": "Test email snippet",
        "payload": {
            "headers": [
                {"name": "From", "value": "sender@example.com"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Subject", "value": "Test Subject"},
                {"name": "Date", "value": "Thu, 29 Oct 2026 10:00:00 +0000"},
            ]
        },
    }

    result = extract_message_metadata(message)

    assert result["id"] == "test-message-id"
    assert result["thread_id"] == "test-thread-id"
    assert result["sender"] == "sender@example.com"
    assert result["recipient"] == "recipient@example.com"
    assert result["subject"] == "Test Subject"
    assert result["date"] == "Thu, 29 Oct 2026 10:00:00 +0000"
    assert result["snippet"] == "Test email snippet"
def test_extract_message_metadata_with_missing_headers():
    message = {
        "id": "test-id",
        "threadId": "test-thread",
        "snippet": "Test snippet",
        "payload": {
            "headers": [
                {"name": "From", "value": "sender@example.com"}
            ]
        },
    }

    result = extract_message_metadata(message)

    assert result["sender"] == "sender@example.com"
    assert result["subject"] is None
    assert result["recipient"] is None
    assert result["date"] is None
    
import base64

from backend.app.gmail.reader import extract_email_body


def test_extract_email_body():
    email_text = "Hello! Please review the project update."

    encoded_body = base64.urlsafe_b64encode(
        email_text.encode("utf-8")
    ).decode("utf-8").rstrip("=")

    message = {
        "payload": {
            "mimeType": "text/plain",
            "body": {
                "data": encoded_body
            }
        }
    }

    result = extract_email_body(message)

    assert result == email_text

def test_extract_email_body_from_multipart():
    plain_text = "This is the plain-text email body."

    encoded_body = base64.urlsafe_b64encode(
        plain_text.encode("utf-8")
    ).decode("utf-8").rstrip("=")

    message = {
        "payload": {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": "PGI+SGVsbG88L2I+"}
                },
                {
                    "mimeType": "text/plain",
                    "body": {"data": encoded_body}
                }
            ]
        }
    }

    result = extract_email_body(message)

    assert result == plain_text
def test_extract_email_body_when_empty():
    message = {
        "payload": {
            "mimeType": "text/plain",
            "body": {}
        }
    }

    result = extract_email_body(message)

    assert result == ""

import base64


def encode_email_content(content: str) -> str:
    return base64.urlsafe_b64encode(
        content.encode("utf-8")
    ).decode("utf-8").rstrip("=")


def test_extract_email_body_from_html_only():
    from backend.app.gmail.reader import extract_email_body

    html_content = """
    <html>
        <body>
            <h1>Hello</h1>
            <p>This is an HTML-only email.</p>
            <script>alert('ignore this')</script>
        </body>
    </html>
    """

    message = {
        "payload": {
            "mimeType": "text/html",
            "body": {
                "data": encode_email_content(html_content)
            },
        }
    }

    result = extract_email_body(message)

    assert "Hello" in result
    assert "This is an HTML-only email." in result
    assert "alert" not in result


def test_extract_message_metadata_with_labels_and_unsubscribe():
    from backend.app.gmail.reader import extract_message_metadata

    message = {
        "id": "message-123",
        "threadId": "thread-456",
        "labelIds": ["INBOX", "UNREAD"],
        "payload": {
            "headers": [
                {"name": "From", "value": "sender@example.com"},
                {"name": "Subject", "value": "Test email"},
                {
                    "name": "List-Unsubscribe",
                    "value": "<mailto:unsubscribe@example.com>",
                },
            ]
        },
    }

    result = extract_message_metadata(message)

    assert result["labels"] == ["INBOX", "UNREAD"]
    assert result["list_unsubscribe"] == (
        "<mailto:unsubscribe@example.com>"
    )
