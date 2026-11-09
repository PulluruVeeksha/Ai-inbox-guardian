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