
from backend.app.gmail.reader import (
    get_message,
    extract_message_metadata,
    extract_email_body,
)
from backend.app.ai.analyzer import analyze_email


def process_email(message_id: str) -> dict:
    """
    Retrieve an email from Gmail and analyze it with Gemini.

    This function only reads and analyzes emails.
    It does not modify Gmail messages.
    """

    if not message_id or not message_id.strip():
        raise ValueError("Message ID cannot be empty.")

    # Retrieve email from Gmail.
    message = get_message(message_id)

    # Extract metadata and plain-text body.
    metadata = extract_message_metadata(message)
    email_body = extract_email_body(message)

    if not email_body.strip():
        raise ValueError(
            "Email has no readable plain-text body. "
            "Human review is required."
        )

    # Include metadata as context for classification.
    email_content = f"""
From: {metadata.get('sender') or 'Unknown'}
To: {metadata.get('recipient') or 'Unknown'}
Subject: {metadata.get('subject') or 'No subject'}
Date: {metadata.get('date') or 'Unknown'}

Email body:
{email_body}
"""

    # Analyze email using Gemini.
    analysis = analyze_email(email_content)

    return {
        "email": metadata,
        "analysis": analysis.model_dump(mode="json"),
        "action_status": "pending_user_approval",
    }
