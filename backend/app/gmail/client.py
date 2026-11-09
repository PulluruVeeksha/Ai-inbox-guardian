from pathlib import Path

from google.oauth2.credentials import Credentials
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

    return build("gmail", "v1", credentials=credentials)