
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from backend.app.auth.google_oauth import create_google_oauth_flow
from backend.app.config import GOOGLE_TOKEN_FILE, APP_ENV
from backend.app.ai.email_processor import process_email


app = FastAPI(title="AI Inbox Guardian")

# Single-user MVP: temporary in-memory OAuth state.
oauth_flows = {}


class EmailAnalysisRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=256)


class SyntheticEmailRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)


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


@app.post("/dev/analyze-synthetic")
def analyze_synthetic_email(request: SyntheticEmailRequest):
    if APP_ENV != "development":
        raise HTTPException(
            status_code=404,
            detail="Not found.",
        )

    text = f"{request.subject} {request.body}".lower()

    if any(
        word in text
        for word in [
            "password",
            "verify your account",
            "urgent payment",
        ]
    ):
        category = "suspicious"
        suspicious = True
        reason = "Mock analysis detected potentially suspicious wording."

    elif any(
        word in text
        for word in [
            "please review",
            "action required",
            "deadline",
        ]
    ):
        category = "needs_action"
        suspicious = False
        reason = "Mock analysis detected a possible action request."

    elif any(
        word in text
        for word in [
            "discount",
            "sale",
            "offer",
            "promotion",
        ]
    ):
        category = "promotional"
        suspicious = False
        reason = "Mock analysis detected promotional wording."

    else:
        category = "fyi"
        suspicious = False
        reason = "Mock analysis classified this as routine information."

    return {
        "analysis_mode": "mock",
        "email": {
            "subject": request.subject,
        },
        "analysis": {
            "category": category,
            "importance_score": 50,
            "confidence": 0.50,
            "reason": reason,
            "deadline": None,
            "requires_reply": category == "needs_action",
            "suspicious": suspicious,
        },
        "action_status": "pending_user_approval",
    }
