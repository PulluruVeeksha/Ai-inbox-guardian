from google_auth_oauthlib.flow import Flow

from backend.app.config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_GMAIL_SCOPE,
    GOOGLE_REDIRECT_URI,
)


def create_google_oauth_flow() -> Flow:
    flow = Flow.from_client_secrets_file(
        str(GOOGLE_CREDENTIALS_FILE),
        scopes=[GOOGLE_GMAIL_SCOPE],
        redirect_uri=GOOGLE_REDIRECT_URI,
    )

    return flow