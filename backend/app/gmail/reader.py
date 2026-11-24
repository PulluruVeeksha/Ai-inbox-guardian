
import base64
from html.parser import HTMLParser

from backend.app.gmail.client import create_gmail_service


class EmailHTMLParser(HTMLParser):
    """Convert HTML email content into readable plain text."""

    BLOCK_TAGS = {
        "br", "p", "div", "li",
        "h1", "h2", "h3", "h4",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text_parts = []
        self.skip_tags = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip_tags.append(tag)
        elif not self.skip_tags and tag in self.BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            index = len(self.skip_tags) - 1 - self.skip_tags[::-1].index(tag)
            self.skip_tags.pop(index)
        elif not self.skip_tags and tag in self.BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_data(self, data):
        if not self.skip_tags:
            self.text_parts.append(data)

    def get_text(self):
        lines = []

        for part in "".join(self.text_parts).splitlines():
            cleaned = " ".join(part.split())
            if cleaned:
                lines.append(cleaned)

        return "\n".join(lines)


def list_message_ids(max_results: int = 10):
    """List recent Gmail message IDs."""
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
    """Retrieve one Gmail message by its ID."""
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


def get_recent_emails(max_results: int = 10):
    """Fetch recent Gmail messages with their full contents."""
    message_ids = list_message_ids(max_results=max_results)

    return [
        get_message(item["id"])
        for item in message_ids
    ]


def get_email(email_id: str):
    """Fetch one email by its Gmail message ID."""
    return get_message(email_id)


def extract_message_metadata(message: dict):
    """Extract useful email headers and Gmail metadata."""
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
        "labels": message.get("labelIds", []),
        "list_unsubscribe": header_map.get("list-unsubscribe"),
    }


def extract_email_body(message: dict) -> str:
    """Prefer plain text; fall back to readable HTML text."""

    def decode_part(part: dict) -> str:
        body_data = part.get("body", {}).get("data")

        if not body_data:
            return ""

        decoded_bytes = base64.urlsafe_b64decode(
            body_data + "=" * (-len(body_data) % 4)
        )

        return decoded_bytes.decode("utf-8", errors="replace")

    def find_parts(payload: dict, mime_type: str) -> list:
        results = []

        if payload.get("mimeType") == mime_type:
            content = decode_part(payload)

            if content:
                results.append(content)

        for part in payload.get("parts", []):
            results.extend(find_parts(part, mime_type))

        return results

    payload = message.get("payload", {})

    # Prefer plain text whenever it is available.
    text_parts = find_parts(payload, "text/plain")

    if text_parts:
        return "\n".join(text_parts).strip()

    # Fall back to HTML if no readable plain-text part exists.
    html_parts = find_parts(payload, "text/html")

    if not html_parts:
        return ""

    parser = EmailHTMLParser()

    for html_content in html_parts:
        parser.feed(html_content)

    parser.close()

    return parser.get_text().strip()
