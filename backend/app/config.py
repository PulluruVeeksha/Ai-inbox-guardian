
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_CREDENTIALS_FILE = (
    PROJECT_ROOT / "credentials" / "client_secret.json"
)

GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"

GOOGLE_GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.modify"

GOOGLE_TOKEN_FILE = PROJECT_ROOT / "token.json"

APP_ENV = os.getenv("APP_ENV", "development")

# PostgreSQL configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "ai_inbox_guardian")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
