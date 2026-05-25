import os
import uuid
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from chatbot.engine import ServiceBot

load_dotenv()

app = FastAPI(title="NexSupport Web API", version="1.0.0")

# ── In-memory session store ────────────────────────────────────────────────────
_sessions: dict[str, dict] = {}


def _get_api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key or key == "your-api-key-here":
        raise HTTPException(status_code=503, detail="OPENROUTER_API_KEY is not configured on the server.")
    return key


def _get_model() -> str:
    return os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")


def _make_session(session_id: str) -> dict:
    status_messages: list[str] = []

    def status_callback(msg: str):
        status_messages.append(msg)

    bot = ServiceBot(
        api_key=_get_api_key(),
        model=_get_model(),
        status_callback=status_callback,
    )
    _sessions[session_id] = {"bot": bot, "status": status_messages}
    return _sessions[session_id]


# ── Request / Response Models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    model: str
    status_messages: list[str]


class SessionResponse(BaseModel):
    session_id: str
    greeting: str
    model: str


class ResetRequest(BaseModel):
    session_id: str


class ResetResponse(BaseModel):
    session_id: str
    greeting: str
    model: str


# ── API Endpoints ──────────────────────────────────────────────────────────────

@app.get("/api/session", response_model=SessionResponse)
def create_session():
    """Create a new chat session and return the greeting."""
    session_id = str(uuid.uuid4())
    session = _make_session(session_id)
    bot: ServiceBot = session["bot"]
    status: list[str] = session["status"]

    status.clear()
    greeting = bot.get_greeting()

    return SessionResponse(
        session_id=session_id,
        greeting=greeting,
        model=bot.model,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a user message and get the bot's reply."""
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please refresh the page.")

    session = _sessions[req.session_id]
    bot: ServiceBot = session["bot"]
    status: list[str] = session["status"]

    status.clear()
    reply = bot.chat(req.message)
    captured_status = list(status)

    return ChatResponse(
        reply=reply,
        model=bot.model,
        status_messages=captured_status,
    )


@app.post("/api/reset", response_model=ResetResponse)
def reset_session(req: ResetRequest):
    """Reset the current session and start fresh."""
    # Remove old session if exists
    if req.session_id in _sessions:
        del _sessions[req.session_id]

    session_id = req.session_id  # reuse same ID so client doesn't need to update localStorage
    session = _make_session(session_id)
    bot: ServiceBot = session["bot"]
    status: list[str] = session["status"]

    status.clear()
    greeting = bot.get_greeting()

    return ResetResponse(
        session_id=session_id,
        greeting=greeting,
        model=bot.model,
    )


@app.get("/api/status")
def server_status():
    """Returns server info and configuration."""
    return {
        "status": "online",
        "model": _get_model(),
        "active_sessions": len(_sessions),
    }


# ── Static Files & Catch-all for SPA ──────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
