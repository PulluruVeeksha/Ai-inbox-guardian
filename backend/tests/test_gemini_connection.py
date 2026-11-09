import os

import pytest
from dotenv import load_dotenv
from google import genai


load_dotenv()

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEMINI_TESTS") != "1",
    reason="Live Gemini tests are disabled by default.",
)


def test_gemini_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    assert api_key, "GEMINI_API_KEY is missing."

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Reply with exactly: AI Inbox Guardian connection successful.",
    )

    assert response.text.strip() == (
        "AI Inbox Guardian connection successful."
    )