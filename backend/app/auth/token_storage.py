
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.app.auth.token_encryption import encrypt_token, decrypt_token
from backend.app.config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_GMAIL_SCOPE,
)
from backend.app.database import SessionLocal
from backend.app.models import User, OAuthToken


def save_oauth_credentials(credentials) -> str:
    """Save an encrypted refresh token for the authorized Gmail account."""

    gmail = build("gmail", "v1", credentials=credentials)
    profile = gmail.users().getProfile(userId="me").execute()
    account_email = profile["emailAddress"]

    if not credentials.refresh_token:
        raise ValueError(
            "Google did not return a refresh token. Reauthorize with consent."
        )

    session = SessionLocal()

    try:
        user = (
            session.query(User)
            .filter_by(google_account_email=account_email)
            .first()
        )

        if user is None:
            user = User(google_account_email=account_email)
            session.add(user)
            session.flush()

        token_record = (
            session.query(OAuthToken)
            .filter_by(user_id=user.id)
            .first()
        )

        encrypted_refresh_token = encrypt_token(
            credentials.refresh_token
        )

        if token_record is None:
            token_record = OAuthToken(
                user_id=user.id,
                encrypted_refresh_token=encrypted_refresh_token,
                scopes=list(credentials.scopes or [GOOGLE_GMAIL_SCOPE]),
            )
            session.add(token_record)
        else:
            token_record.encrypted_refresh_token = encrypted_refresh_token
            token_record.scopes = list(
                credentials.scopes or [GOOGLE_GMAIL_SCOPE]
            )
            token_record.revoked_at = None

        session.commit()
        return account_email

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def load_stored_credentials() -> Credentials:
    """Load the single-user MVP refresh token from PostgreSQL."""

    session = SessionLocal()

    try:
        token_record = (
            session.query(OAuthToken)
            .filter(OAuthToken.revoked_at.is_(None))
            .first()
        )

        if token_record is None:
            raise FileNotFoundError(
                "No active Gmail authorization was found. Please authorize Google."
            )

        refresh_token = decrypt_token(
            token_record.encrypted_refresh_token
        )
        scopes = token_record.scopes or [GOOGLE_GMAIL_SCOPE]

    finally:
        session.close()

    with GOOGLE_CREDENTIALS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        client_config = json.load(file)

    oauth_config = (
        client_config.get("web")
        or client_config.get("installed")
    )

    if not oauth_config:
        raise RuntimeError("Google OAuth client configuration is invalid.")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=oauth_config["token_uri"],
        client_id=oauth_config["client_id"],
        client_secret=oauth_config["client_secret"],
        scopes=scopes,
    )

    credentials.refresh(Request())
    return credentials
