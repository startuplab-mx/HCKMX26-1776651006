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

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from classifier import Pipeline
from database import get_db
import webhooks
from database.models import (
    AlertAction,
    AlertCreate,
    AlertUpdate,
    AnalyzeRequest,
    AnalyzeResponse,
    EscalationRequest,
    PhaseScores,
    SessionState,
    SessionUpsert,
    StatsResponse,
    TimeseriesBucket,
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
    app.state.pipeline = Pipeline()
    app.state.db = get_db()
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


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_enabled": app.state.pipeline.llm.enabled,
        "db_path": str(app.state.db.path),
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    result = app.state.pipeline.classify(req.text, use_llm=req.use_llm)
    return AnalyzeResponse(
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        phase_detected=result["phase_detected"],
        phase_scores=PhaseScores(**result["phase_scores"]),
        categories=result["categories"],
        override_triggered=result["override_triggered"],
        llm_used=result["llm_used"],
        llm_rationale=result["llm_rationale"],
        text_hash=result["text_hash"],
        summary=result["summary"],
    )


@app.post("/alert", status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate):
    """Webhook from bot/extension. Analyzes and persists in one call.

    Returns the full classification so callers (e.g. the bot) don't need a
    second /analyze trip. The text is never persisted — only its SHA-256 hash
    plus an anonymized summary.
    """
    result = app.state.pipeline.classify(payload.text, use_llm=True)
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
    )
    response = {
        "id": alert_id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "phase_detected": result["phase_detected"],
        "phase_scores": result["phase_scores"],
        "categories": result["categories"],
        "override_triggered": result["override_triggered"],
        "llm_used": result["llm_used"],
        "summary": result["summary"],
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
