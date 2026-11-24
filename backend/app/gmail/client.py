from googleapiclient.discovery import build

from backend.app.auth.token_storage import load_stored_credentials


def create_gmail_service():
    credentials = load_stored_credentials()

    return build(
        "gmail",
        "v1",
        credentials=credentials,
    )