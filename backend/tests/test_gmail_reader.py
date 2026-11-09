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