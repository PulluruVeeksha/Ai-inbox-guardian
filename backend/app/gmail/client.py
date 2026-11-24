
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from backend.app.config import GOOGLE_GMAIL_SCOPE, GOOGLE_TOKEN_FILE


def create_gmail_service():
    if not GOOGLE_TOKEN_FILE.exists():
        raise FileNotFoundError(
            "Gmail OAuth token not found. Complete OAuth authorization first."
        )

    credentials = Credentials.from_authorized_user_file(
        str(GOOGLE_TOKEN_FILE),
        scopes=[GOOGLE_GMAIL_SCOPE],
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        GOOGLE_TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    if not credentials.valid:
        raise RuntimeError(
            "Gmail credentials are invalid. Please authorize Google again."
        )

    return build("gmail", "v1", credentials=credentials)
