
import base64

from backend.app.gmail.client import create_gmail_service


def list_message_ids(max_results: int = 10):
    service = create_gmail_service()

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
        )
        .execute()
    )

    return response.get("messages", [])


def get_message(message_id: str):
    service = create_gmail_service()

    return (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full",
        )
        .execute()
    )


def extract_message_metadata(message: dict):
    headers = message.get("payload", {}).get("headers", [])

    header_map = {
        header["name"].lower(): header["value"]
        for header in headers
    }

    return {
        "id": message.get("id"),
        "thread_id": message.get("threadId"),
        "sender": header_map.get("from"),
        "recipient": header_map.get("to"),
        "subject": header_map.get("subject"),
        "date": header_map.get("date"),
        "snippet": message.get("snippet"),
    }


def extract_email_body(message: dict) -> str:
    """Extract plain-text email content from Gmail message payload."""

    def decode_part(part: dict) -> str:
        body_data = part.get("body", {}).get("data")

        if not body_data:
            return ""

        decoded_bytes = base64.urlsafe_b64decode(
            body_data + "=" * (-len(body_data) % 4)
        )

        return decoded_bytes.decode("utf-8", errors="replace")

    def find_plain_text(payload: dict) -> list:
        mime_type = payload.get("mimeType", "")

        if mime_type == "text/plain":
            content = decode_part(payload)
            return [content] if content else []

        results = []

        for part in payload.get("parts", []):
            results.extend(find_plain_text(part))

        return results

    payload = message.get("payload", {})
    text_parts = find_plain_text(payload)

    return "\n".join(text_parts).strip()
