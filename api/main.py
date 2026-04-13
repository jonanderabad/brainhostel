"""BRAINHOSTEL API — FastAPI service backed by Claude Managed Agents."""

import os
import logging

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from session_handler import ask_question

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = "".join(os.environ.get("ANTHROPIC_API_KEY", "").split())
AGENT_ID = os.environ.get("AGENT_ID", "agent_011Ca1ZKPsvBCA2yGDzQkXnw")
ENV_ID = os.environ.get("ENV_ID", "env_01YAaWs9eHTPJ5NMYDxNcPb4")

if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY is not set")
if not AGENT_ID:
    raise RuntimeError("AGENT_ID is not set — run setup_agent.py first")
if not ENV_ID:
    raise RuntimeError("ENV_ID is not set — run setup_agent.py first")

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
)

# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="BRAINHOSTEL API",
    description="Consulta el Convenio de Hostelería de Bizkaia 2025",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Models ───────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class AskResponse(BaseModel):
    question: str
    answer: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "agent_id": AGENT_ID}


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    logger.info(f"Question received: {body.question[:80]}")
    try:
        answer = ask_question(client, AGENT_ID, ENV_ID, body.question)
        return AskResponse(question=body.question, answer=answer)
    except RuntimeError as e:
        logger.error(f"Session error: {e}")
        raise HTTPException(status_code=500, detail="Error al consultar el agente. Inténtalo de nuevo.")
    except ValueError as e:
        logger.error(f"Empty response: {e}")
        raise HTTPException(status_code=500, detail="El agente no generó respuesta.")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
