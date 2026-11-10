
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from backend.app.auth.google_oauth import create_google_oauth_flow
from backend.app.config import GOOGLE_TOKEN_FILE
from backend.app.ai.email_processor import process_email


app = FastAPI(title="AI Inbox Guardian")

# Single-user MVP: temporary in-memory OAuth state.
oauth_flows = {}


class EmailAnalysisRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=256)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/auth/login")
def auth_login():
    flow = create_google_oauth_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    oauth_flows[state] = flow

    return RedirectResponse(url=authorization_url)


@app.get("/auth/callback")
def auth_callback(code: str, state: str):
    flow = oauth_flows.pop(state, None)

    if flow is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state.",
        )

    flow.fetch_token(code=code)

    GOOGLE_TOKEN_FILE.write_text(
        flow.credentials.to_json(),
        encoding="utf-8",
    )

    return {
        "status": "oauth authorization successful",
        "message": "Google authorization successful and credentials saved.",
    }


@app.post("/emails/analyze")
def analyze_email_endpoint(request: EmailAnalysisRequest):
    try:
        return process_email(request.message_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=401,
            detail="Gmail authorization is required.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Email analysis is temporarily unavailable.",
        ) from exc
