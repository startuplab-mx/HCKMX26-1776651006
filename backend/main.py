"""
Nahual FastAPI app.

Run:
    uvicorn main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import base64

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from classifier import Pipeline
from classifier.escalation import EscalationDetector
from classifier.pipeline import build_why_from_ids
from classifier.precision import PrecisionProcessor
from database import get_db
from legal import get_legal_context, get_privacy_disclaimer, serialize_context
import webhooks
from database.models import (
    AlertAction,
    AlertCreate,
    AlertUpdate,
    AnalyzeRequest,
    AnalyzeResponse,
    ContributionCreate,
    ContributionStats,
    EscalationRequest,
    FeedbackCreate,
    PhaseScores,
    SessionState,
    SessionUpsert,
    StatsResponse,
    TimeseriesBucket,
    TranscriptionResponse,
)
from reports import generate_report

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nahual")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = get_db()
    app.state.precision = PrecisionProcessor(app.state.db)
    app.state.pipeline = Pipeline(
        escalation=EscalationDetector(app.state.db),
        precision=app.state.precision,
    )
    logger.info("Nahual backend up · LLM enabled=%s", app.state.pipeline.llm.enabled)
    yield
    app.state.db.close()


app = FastAPI(
    title="Nahual API",
    description=(
        "Sistema de detección de reclutamiento criminal digital de menores. "
        "Hackathon 404: Threat Not Found."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins_env = os.getenv("CORS_ORIGINS", "*")
allow_origins = (
    ["*"] if cors_origins_env.strip() == "*" else [o.strip() for o in cors_origins_env.split(",")]
)

# CORS spec: a wildcard origin cannot coexist with credentials. Disable
# credentials when origins are wildcarded so browsers don't reject preflight.
allow_credentials = "*" not in allow_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Endpoints ----------------


@app.get("/", include_in_schema=False)
def root():
    return {
        "name": "Nahual API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/sessions/{session_id}", response_model=SessionState)
def get_session(session_id: str):
    """Fetch a bot session. 404 if it doesn't exist (caller may PUT to create)."""
    sess = app.state.db.get_session(session_id)
    if sess is None:
        raise HTTPException(404, f"Session {session_id} not found")
    return sess


@app.put("/sessions/{session_id}", response_model=SessionState)
def upsert_session(session_id: str, payload: SessionUpsert):
    """Upsert bot session state. Used by the bot to survive restarts."""
    app.state.db.upsert_session(
        session_id=session_id,
        current_step=payload.current_step,
        data=payload.data or {},
    )
    sess = app.state.db.get_session(session_id)
    assert sess is not None  # we just wrote it
    return sess


@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str):
    """Reset a bot session (e.g. after a completed flow)."""
    app.state.db.delete_session(session_id)
    return None


@app.get("/profile/{session_id}")
def risk_profile(session_id: str):
    """Cumulative risk profile for a session — used by panel and pitch demo.

    Computes: trend, average score, max, dominant phase, phase distribution,
    score timeline (last 10), and the count of alerts written for the
    session. Returns `status=no_data` when the session has never been seen.
    """
    history = app.state.db.get_risk_history(session_id)
    alerts = app.state.db.get_alerts_by_session(session_id)
    if not history:
        return {"session_id": session_id, "status": "no_data"}

    scores = [h["risk_score"] for h in history]
    phases = [
        h["phase_detected"]
        for h in history
        if h["phase_detected"] and h["phase_detected"] != "ninguna"
    ]
    phase_counts: dict[str, int] = {}
    for p in phases:
        phase_counts[p] = phase_counts.get(p, 0) + 1
    dominant = max(phase_counts, key=phase_counts.get) if phase_counts else None

    if len(scores) >= 2:
        diffs = [scores[i + 1] - scores[i] for i in range(len(scores) - 1)]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 0.05:
            trend = "incremental"
        elif avg_diff < -0.05:
            trend = "decreciente"
        else:
            trend = "estable"
    else:
        trend = "insufficient_data"

    return {
        "session_id": session_id,
        "status": "ok",
        "total_analyses": len(history),
        "risk_profile": {
            "current_level": history[-1]["risk_level"],
            "current_score": history[-1]["risk_score"],
            "average_score": round(sum(scores) / len(scores), 3),
            "max_score": max(scores),
            "trend": trend,
            "dominant_phase": dominant,
            "phase_distribution": phase_counts,
            "score_timeline": [round(s, 3) for s in scores[-10:]],
        },
        "total_alerts": len(alerts),
        "first_analysis": history[0]["timestamp"],
        "last_analysis": history[-1]["timestamp"],
    }


@app.get("/risk-history/{session_id}")
def risk_history(session_id: str, limit: int = 50):
    """Raw risk_history rows for the session (newest entries truncated to `limit`)."""
    if limit < 1 or limit > 500:
        raise HTTPException(400, "limit must be in [1, 500]")
    return app.state.db.get_risk_history(session_id, limit=limit)


@app.delete("/risk-history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def reset_risk_history(session_id: str):
    """Clear the session's risk history. Used by demo_live.py to start clean."""
    app.state.db.clear_risk_history(session_id)
    return None


@app.post("/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(payload: FeedbackCreate):
    """Record a feedback signal for the auto-tuner.

    Sources:
      • bot: 'confirm' when the user provides the guardian phone after
        PELIGRO; 'deny' when the user explicitly contradicts the alert
      • panel: 'operator_fp' / 'operator_fn' (twice the magnitude)
      • pipeline: 'llm_discrepancy' (auto-recorded when |LLM−heuristic|≥0.3)
    """
    fid = app.state.db.save_feedback(
        feedback_type=payload.feedback_type,
        alert_id=payload.alert_id,
        heuristic_score=payload.heuristic_score,
        llm_score=payload.llm_score,
        final_score=payload.final_score,
        pattern_ids=payload.pattern_ids,
        session_id=payload.session_id,
    )
    return {"received": True, "id": fid}


@app.get("/precision/diagnostics")
def precision_diagnostics():
    """Snapshot of the auto-tuner: active adjustments + problematic patterns."""
    return app.state.precision.get_diagnostics()


@app.get("/precision/stats")
def precision_stats():
    """Counts of feedback rows in the queue by type + pending."""
    return app.state.db.feedback_stats()


@app.post("/precision/tune")
def precision_tune():
    """Force a tuning cycle (drains the feedback_log queue once)."""
    return app.state.precision.process_pending_feedback()


@app.get("/precision/state")
def precision_state():
    """Export full processor state (adjustments + per-pattern stats).

    Useful for persistence between restarts and for the post-hackathon
    dashboard to visualize what the tuner has learned.
    """
    return app.state.precision.export_state()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_enabled": app.state.pipeline.llm.enabled,
        "db_path": str(app.state.db.path),
        "groq_enabled": bool(os.getenv("GROQ_API_KEY")),
    }


# ---------------- STT / OCR (Phase 3) ----------------

GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"

OCR_SYSTEM_PROMPT = (
    "Extrae TODO el texto visible en esta imagen de una conversación de chat. "
    "Incluye cada mensaje exactamente como aparece, incluyendo emojis. "
    "Retorna SOLO el texto extraído, sin explicaciones ni formato adicional. "
    "Si no hay texto legible, responde 'NO_TEXT'."
)

ALLOWED_AUDIO_MIME = {"audio/ogg", "audio/mpeg", "audio/mp4", "audio/wav", "audio/webm", "audio/x-m4a"}
ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_AUDIO_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_IMAGE_BYTES = 8 * 1024 * 1024    # 8 MB


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Receive an audio file, transcribe with Groq Whisper.

    Privacy: the audio bytes are forwarded to Groq for transcription and
    NOT persisted on the Nahual side. The returned text is fed back into
    /alert by the bot (after user confirmation), where only its SHA-256
    hash + summary are stored.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise HTTPException(503, "STT service unavailable (GROQ_API_KEY not configured)")

    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(400, "empty audio file")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(413, f"audio exceeds {MAX_AUDIO_BYTES // (1024 * 1024)} MB")

    mime = file.content_type or "audio/ogg"
    timeout = float(os.getenv("STT_TIMEOUT_SECONDS", "15"))

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                GROQ_TRANSCRIBE_URL,
                headers={"Authorization": f"Bearer {groq_key}"},
                files={"file": (file.filename or "audio.ogg", audio_bytes, mime)},
                data={"model": "whisper-large-v3", "language": "es"},
            )
    except httpx.TimeoutException:
        raise HTTPException(504, "STT upstream timed out")
    except httpx.HTTPError as e:
        raise HTTPException(502, f"STT upstream error: {e}")

    if resp.status_code != 200:
        raise HTTPException(502, f"STT upstream returned {resp.status_code}: {resp.text[:200]}")
    text = (resp.json().get("text") or "").strip()
    return TranscriptionResponse(text=text, source="groq_whisper")


@app.post("/ocr", response_model=TranscriptionResponse)
async def ocr_image(file: UploadFile = File(...)):
    """Receive an image, extract text with Claude Vision.

    Privacy: the image bytes are forwarded to Anthropic and not persisted
    here. Same pipeline as /transcribe — extracted text is shown to the
    user for confirmation before being analyzed.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-xxxxx"):
        raise HTTPException(503, "OCR service unavailable (ANTHROPIC_API_KEY not configured)")

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(400, "empty image file")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, f"image exceeds {MAX_IMAGE_BYTES // (1024 * 1024)} MB")

    media_type = file.content_type or "image/png"
    if media_type not in ALLOWED_IMAGE_MIME:
        raise HTTPException(415, f"unsupported image type {media_type!r}")

    b64 = base64.b64encode(image_bytes).decode("ascii")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    timeout = float(os.getenv("OCR_TIMEOUT_SECONDS", "15"))

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                ANTHROPIC_MESSAGES_URL,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": b64,
                                    },
                                },
                                {"type": "text", "text": OCR_SYSTEM_PROMPT},
                            ],
                        }
                    ],
                },
            )
    except httpx.TimeoutException:
        raise HTTPException(504, "OCR upstream timed out")
    except httpx.HTTPError as e:
        raise HTTPException(502, f"OCR upstream error: {e}")

    if resp.status_code != 200:
        raise HTTPException(502, f"OCR upstream returned {resp.status_code}: {resp.text[:200]}")
    body = resp.json()
    text = (body.get("content", [{}])[0].get("text") or "").strip()
    if text == "NO_TEXT":
        text = ""
    return TranscriptionResponse(text=text, source="claude_vision")


# ---------------- Anonymous research contributions (Phase 3) ----------------

@app.post("/contribute", status_code=status.HTTP_201_CREATED)
def contribute(payload: ContributionCreate):
    """Persist anonymized analysis metadata.

    The Pydantic model has ``extra='forbid'`` so unknown fields (which
    might smuggle PII) are rejected with 422. We never accept text, phone,
    session id, or hash here — by construction, this dataset is the
    anonymous research output of Nahual.
    """
    cid = app.state.db.insert_contribution(
        platform=payload.platform,
        risk_level=payload.risk_level,
        risk_score=payload.risk_score,
        phase_detected=payload.phase_detected,
        categories=payload.categories,
        pattern_ids=payload.pattern_ids,
        source_type=payload.source_type,
        region=payload.region,
        llm_used=payload.llm_used,
        override_triggered=payload.override_triggered,
    )
    return {"contributed": True, "id": cid}


@app.get("/contributions/stats", response_model=ContributionStats)
def contributions_stats():
    """Public aggregate from the contributed-research dataset."""
    return app.state.db.contribution_stats()


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """Analyze text + return classification + legal context + escalation.

    When `session_id` is provided, the call participates in escalation
    tracking: each analysis is appended to risk_history and the trend
    is reported in `escalation`. A trajectory of climbing ATENCION
    messages can also auto-promote risk_level to PELIGRO via
    `escalation_override`.
    """
    result = app.state.pipeline.classify(
        req.text,
        use_llm=req.use_llm,
        session_id=req.session_id,
        source_type=req.source_type,
    )
    legal = get_legal_context(
        phase=result["phase_detected"],
        categories=result["categories"],
        risk_level=result["risk_level"],
    )
    body = AnalyzeResponse(
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        phase_detected=result["phase_detected"],
        phase_scores=PhaseScores(**result["phase_scores"]),
        categories=result["categories"],
        pattern_ids=result.get("pattern_ids", []),
        override_triggered=result["override_triggered"],
        llm_used=result["llm_used"],
        llm_rationale=result["llm_rationale"],
        text_hash=result["text_hash"],
        summary=result["summary"],
    ).model_dump()
    body["why"] = result.get("why", [])
    body["escalation"] = result.get("escalation")
    body["escalation_override"] = result.get("escalation_override", False)
    body["legal"] = serialize_context(legal)
    body["privacy_disclaimer"] = get_privacy_disclaimer()
    return body


@app.post("/alert", status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate):
    """Webhook from bot/extension. Analyzes and persists in one call.

    Returns the full classification so callers (e.g. the bot) don't need a
    second /analyze trip. The text is never persisted — only its SHA-256 hash
    plus an anonymized summary.
    """
    result = app.state.pipeline.classify(
        payload.text,
        use_llm=True,
        session_id=payload.session_id,
        source_type=payload.source_type,
    )
    alert_id = app.state.db.insert_alert(
        platform=payload.platform,
        source=payload.source,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        phase_detected=result["phase_detected"],
        categories=result["categories"],
        summary=result["summary"],
        text_hash=result["text_hash"],
        contact_phone=payload.contact_phone,
        llm_used=result["llm_used"],
        override_triggered=result["override_triggered"],
        session_id=payload.session_id,
        pattern_ids=result.get("pattern_ids", []),
        source_type=payload.source_type,
    )
    legal = get_legal_context(
        phase=result["phase_detected"],
        categories=result["categories"],
        risk_level=result["risk_level"],
    )
    response = {
        "id": alert_id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "phase_detected": result["phase_detected"],
        "phase_scores": result["phase_scores"],
        "categories": result["categories"],
        "pattern_ids": result.get("pattern_ids", []),
        "override_triggered": result["override_triggered"],
        "escalation_override": result.get("escalation_override", False),
        "escalation": result.get("escalation"),
        "why": result.get("why", []),
        "llm_used": result["llm_used"],
        "summary": result["summary"],
        "source_type": payload.source_type,
        "legal": serialize_context(legal),
    }
    # Auto-fire webhook on override (death threats, sextortion). External
    # consumers — e.g. SIPINNA bridge, Fiscalía intake — can listen here.
    if result["override_triggered"]:
        stored = app.state.db.get_alert(alert_id)
        if stored is not None:
            webhooks.dispatch(
                webhooks.build_payload(event="alert.override", alert=stored)
            )
    return response


@app.get("/alerts")
def list_alerts(
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    risk_level: str | None = None,
):
    if limit < 1 or limit > 500:
        raise HTTPException(400, "limit must be in [1, 500]")
    return app.state.db.list_alerts(
        limit=limit,
        offset=offset,
        status=status,
        risk_level=risk_level,
    )


@app.get("/alerts/{alert_id}")
def get_alert(alert_id: int):
    alert = app.state.db.get_alert(alert_id)
    if not alert:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return alert


@app.patch("/alerts/{alert_id}")
def patch_alert(alert_id: int, payload: AlertUpdate):
    """Update triage state (status / notes / reviewer). Writes audit trail."""
    try:
        updated = app.state.db.update_alert_status(
            alert_id,
            status=payload.status,
            notes=payload.notes,
            reviewer=payload.reviewer,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    if updated is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return updated


@app.post("/alerts/{alert_id}/escalate", status_code=status.HTTP_200_OK)
def escalate_alert(alert_id: int, payload: EscalationRequest):
    """Escalate an alert to an external authority (088, SIPINNA, Fiscalía).

    Also fires outbound webhooks (NAHUAL_WEBHOOK_URLS) so external systems
    can receive the escalation. Webhook failures are logged but never bubble
    up — the escalation has already been recorded in the DB.
    """
    updated = app.state.db.escalate_alert(
        alert_id,
        destination=payload.destination,
        reason=payload.reason,
        reviewer=payload.reviewer,
    )
    if updated is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    webhooks.dispatch(
        webhooks.build_payload(
            event="alert.escalated",
            alert=updated,
            destination=payload.destination,
            reason=payload.reason,
            reviewer=payload.reviewer,
        )
    )
    return updated


@app.get("/alerts/{alert_id}/history", response_model=list[AlertAction])
def alert_history(alert_id: int):
    """Audit trail for an alert — every status change, note and escalation."""
    if app.state.db.get_alert(alert_id) is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return app.state.db.list_actions(alert_id)


@app.get("/alerts/{alert_id}/why")
def alert_why(alert_id: int):
    """Reconstruct the human-readable "¿Por qué?" view for a stored alert.

    Re-derives explanations from the alert's persisted pattern_ids using
    the live heuristic, so the panel can show why the alert fired even
    weeks later without retaining the original text.
    """
    alert = app.state.db.get_alert(alert_id)
    if alert is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    pattern_ids = alert.get("pattern_ids") or []
    why = build_why_from_ids(app.state.pipeline.heuristic, pattern_ids, limit=12)
    return {
        "alert_id": alert_id,
        "phase_detected": alert.get("phase_detected"),
        "risk_level": alert.get("risk_level"),
        "pattern_ids": pattern_ids,
        "why": why,
    }


@app.get("/alerts/{alert_id}/legal")
def alert_legal(alert_id: int):
    """Recompute the legal context for a stored alert.

    Built deterministically from the persisted phase + categories +
    risk_level, so the panel can render the same articles, authorities
    and recommended actions that the bot saw at analysis time.
    """
    alert = app.state.db.get_alert(alert_id)
    if alert is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    legal = get_legal_context(
        phase=alert.get("phase_detected"),
        categories=alert.get("categories") or [],
        risk_level=alert.get("risk_level", "SEGURO"),
    )
    return serialize_context(legal)


@app.get("/stats", response_model=StatsResponse)
def stats():
    return StatsResponse(**app.state.db.stats())


@app.get("/stats/timeseries", response_model=list[TimeseriesBucket])
def stats_timeseries(interval: str = "hour", hours: int = 24):
    """Time-bucketed alert counts for the panel activity chart.

    Returns one row per non-empty bucket, oldest first. The client is
    responsible for filling zero-buckets to keep the time axis continuous.
    """
    if interval not in ("hour", "day"):
        raise HTTPException(400, "interval must be 'hour' or 'day'")
    if hours < 1 or hours > 30 * 24:
        raise HTTPException(400, "hours must be in [1, 720]")
    try:
        return app.state.db.timeseries(interval=interval, hours=hours)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/report/{alert_id}")
def report(alert_id: int):
    alert = app.state.db.get_alert(alert_id)
    if not alert:
        raise HTTPException(404, f"Alert {alert_id} not found")
    path = generate_report(alert)
    app.state.db.mark_report_generated(alert_id, str(path))
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )


@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
