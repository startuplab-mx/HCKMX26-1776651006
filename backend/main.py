"""
Nahual FastAPI app.

Run:
    uvicorn main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
"""
from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import base64

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Security, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import APIKeyHeader

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


_ENV = os.getenv("ENVIRONMENT", "development").strip().lower()
_PROD = _ENV == "production"

app = FastAPI(
    title="Nahual API",
    description=(
        "Sistema de detección de reclutamiento criminal digital de menores. "
        "Hackathon 404: Threat Not Found."
    ),
    version="1.0.0",
    lifespan=lifespan,
    # Disable interactive docs in production. /openapi.json is also
    # implicitly disabled when both docs urls are None.
    docs_url=None if _PROD else "/docs",
    redoc_url=None if _PROD else "/redoc",
    openapi_url=None if _PROD else "/openapi.json",
)

# ---------------- API key auth (opt-in via NAHUAL_API_KEY) ----------------

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(provided: str | None = Security(API_KEY_HEADER)) -> None:
    """Gate sensitive endpoints behind the X-API-Key header.

    When `NAHUAL_API_KEY` is unset or empty, auth is disabled — keeps
    dev/test environments and the 126-test suite working without
    changes. Once the env var is set, every protected endpoint demands
    a matching header or returns 403.
    """
    expected = os.getenv("NAHUAL_API_KEY", "").strip()
    if not expected:
        return  # dev mode: no enforcement
    if not provided or provided != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-API-Key",
        )


# Reusable dependency list for protected routes.
PROTECTED = [Depends(require_api_key)]


cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
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


@app.get("/sessions/{session_id}", response_model=SessionState, dependencies=PROTECTED)
def get_session(session_id: str):
    """Fetch a bot session. 404 if it doesn't exist (caller may PUT to create)."""
    sess = app.state.db.get_session(session_id)
    if sess is None:
        raise HTTPException(404, f"Session {session_id} not found")
    return sess


@app.put("/sessions/{session_id}", response_model=SessionState, dependencies=PROTECTED)
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


@app.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=PROTECTED,
)
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


@app.get("/risk-history/{session_id}", dependencies=PROTECTED)
def risk_history(session_id: str, limit: int = 50):
    """Raw risk_history rows for the session (newest entries truncated to `limit`)."""
    if limit < 1 or limit > 500:
        raise HTTPException(400, "limit must be in [1, 500]")
    return app.state.db.get_risk_history(session_id, limit=limit)


@app.delete(
    "/risk-history/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=PROTECTED,
)
def reset_risk_history(session_id: str):
    """Clear the session's risk history. Used by demo_live.py to start clean."""
    app.state.db.clear_risk_history(session_id)
    return None


@app.post(
    "/feedback",
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(payload: FeedbackCreate):
    """Record a feedback signal for the auto-tuner.

    Sources:
      • bot: 'confirm' when the user provides the guardian phone after
        PELIGRO; 'deny' when the user explicitly contradicts the alert
      • panel: 'operator_fp' / 'operator_fn' (twice the magnitude)
      • pipeline: 'llm_discrepancy' (auto-recorded when |LLM−heuristic|≥0.3)

    Side effect: feeds the Bayesian classifier when the alert is known.
    `confirm` → train with the alert's dominant phase.
    `deny` / `operator_fp` → train as "seguro" (the alert was wrong).
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

    # Feed the Bayesian classifier so the model learns from real feedback.
    # Best-effort: failures here MUST NOT prevent the feedback row from
    # being saved (which is what the auto-tuner consumes).
    try:
        bayes = getattr(app.state.pipeline, "bayesian", None)
        if bayes is not None and payload.alert_id:
            alert = app.state.db.get_alert(payload.alert_id)
            if alert:
                # We don't have the original text (privacy by design) — use
                # the anonymized summary as a coarse feature source. It
                # contains the categories that fired, which is the most
                # generalisable signal we can persist.
                surrogate_text = alert.get("summary") or ""
                # Pattern_ids reconstruct via the heuristic to recover the
                # actual pattern surface forms (better feature signal).
                from classifier.pipeline import build_why_from_ids
                why_lines = build_why_from_ids(
                    app.state.pipeline.heuristic,
                    alert.get("pattern_ids") or [],
                    limit=5,
                )
                surrogate_text = " ".join([surrogate_text] + (why_lines or []))
                if not surrogate_text.strip():
                    surrogate_text = " ".join(alert.get("categories") or [])
                if surrogate_text:
                    if payload.feedback_type == "confirm":
                        phase = (alert.get("phase_detected") or "").strip()
                        # Map phase_detected to bayesian class names.
                        phase_to_class = {
                            "captacion": "captacion",
                            "enganche": "enganche",
                            "coercion": "coercion",
                            "explotacion": "explotacion",
                        }
                        cls = phase_to_class.get(phase)
                        if cls:
                            bayes.train_one(surrogate_text, cls)
                    elif payload.feedback_type in ("deny", "operator_fp"):
                        bayes.train_one(surrogate_text, "seguro")
    except Exception as e:
        logger.warning("bayesian feed from /feedback failed: %s", e)

    return {"received": True, "id": fid}


# ---------------- Bayesian (Capa 1.5) ----------------


@app.get("/bayesian/stats")
def bayesian_stats():
    """Diagnostic snapshot of the Bayesian classifier.

    Public read-only — exposes counts and top features per class but NEVER
    PII or original text (only n-gram tokens that came from the dataset
    or anonymized summaries). Useful in the panel + pitch demo.
    """
    bayes = getattr(app.state.pipeline, "bayesian", None)
    if bayes is None:
        return {"available": False}
    s = bayes.get_stats()
    s["available"] = True
    return s


@app.post("/bayesian/predict")
def bayesian_predict(payload: AnalyzeRequest):
    """Pure Bayesian prediction (debug/comparison endpoint).

    Bypasses the heuristic + LLM merge so callers can see what the
    Bayesian thinks alone. Matches /analyze's input shape so the same
    request body works.
    """
    bayes = getattr(app.state.pipeline, "bayesian", None)
    if bayes is None:
        raise HTTPException(503, "bayesian classifier not initialised")
    return bayes.predict(payload.text)


@app.get("/precision/diagnostics", dependencies=PROTECTED)
def precision_diagnostics():
    """Snapshot of the auto-tuner: active adjustments + problematic patterns."""
    return app.state.precision.get_diagnostics()


@app.get("/precision/stats", dependencies=PROTECTED)
def precision_stats():
    """Counts of feedback rows in the queue by type + pending."""
    return app.state.db.feedback_stats()


@app.post("/precision/tune", dependencies=PROTECTED)
def precision_tune():
    """Force a tuning cycle (drains the feedback_log queue once)."""
    return app.state.precision.process_pending_feedback()


@app.get("/precision/state", dependencies=PROTECTED)
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
        "groq_enabled": bool(os.getenv("GROQ_API_KEY")),
        "auth_enforced": bool(os.getenv("NAHUAL_API_KEY", "").strip()),
    }


# ---------------- /admin observability (public — read-only) ----------------
# These endpoints surface system metadata that judges and ops want at a
# glance: dataset version, pattern counts, classifier weights snapshot, and
# basic runtime metrics. PII-free, no DB rows leaked.

_BUILD_INFO_CACHE: dict | None = None


def _read_build_info() -> dict:
    """Read git SHA + branch + last-commit timestamp without shelling out.

    Walks the .git directory directly so it works in containers without
    the git binary. Cached after first read because git refs do not
    change at runtime.
    """
    global _BUILD_INFO_CACHE
    if _BUILD_INFO_CACHE is not None:
        return _BUILD_INFO_CACHE

    info = {"commit": None, "branch": None, "committed_at": None}
    try:
        git_dir = ROOT / ".git"
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref: "):
            ref = head[5:]
            info["branch"] = ref.split("/")[-1]
            ref_path = git_dir / ref
            if ref_path.exists():
                info["commit"] = ref_path.read_text(encoding="utf-8").strip()
        else:
            info["commit"] = head  # detached HEAD
        # Best-effort committed_at via packed-refs or commit object header.
        if info["commit"]:
            obj_path = git_dir / "objects" / info["commit"][:2] / info["commit"][2:]
            if obj_path.exists():
                import zlib

                raw = zlib.decompress(obj_path.read_bytes())
                # Format: b"commit <size>\\0tree ...\\nauthor ... <ts> +0000\\n..."
                idx = raw.find(b"committer ")
                if idx >= 0:
                    line_end = raw.find(b"\n", idx)
                    chunk = raw[idx:line_end].decode("utf-8", errors="ignore")
                    parts = chunk.rsplit(" ", 2)
                    if len(parts) == 3:
                        try:
                            info["committed_at"] = int(parts[1])
                        except ValueError:
                            pass
    except Exception:
        # Best-effort only; admin endpoint never crashes on missing git data.
        pass

    _BUILD_INFO_CACHE = info
    return info


@app.get("/admin/version")
def admin_version():
    """Build/version metadata for the demo (commit SHA, branch, time)."""
    info = _read_build_info()
    return {
        "service": "nahual-backend",
        "commit": info.get("commit"),
        "branch": info.get("branch"),
        "committed_at": info.get("committed_at"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python": sys.version.split()[0] if hasattr(sys, "version") else None,
    }


@app.get("/admin/dataset-info")
def admin_dataset_info():
    """Live snapshot of the heuristic classifier's loaded patterns.

    Returns per-phase counts and weight histogram so the panel/judges
    can see at a glance how dense the dataset is and where the high-
    confidence patterns concentrate. Read directly from the in-memory
    classifier (the source of truth at runtime); does not re-read JSON
    so it reflects any tuner overlay applied since boot.
    """
    h = app.state.pipeline.heuristic
    phases = {}
    total = 0
    high_conf = 0  # weight >= 0.8
    for phase_id, name in [
        ("phase1", "Captación"),
        ("phase2", "Enganche"),
        ("phase3", "Coerción"),
        ("phase4", "Explotación"),
    ]:
        # Internal storage is a list of tuples:
        # (compiled_regex, weight, source, pattern_id, explanation)
        pats = h._compiled_patterns.get(phase_id, []) or []
        weights = [t[1] for t in pats]
        # Histogram buckets aligned with semaphore (low/mid/high signal).
        buckets = {
            "low_0.0_0.5": sum(1 for w in weights if w < 0.5),
            "mid_0.5_0.8": sum(1 for w in weights if 0.5 <= w < 0.8),
            "high_0.8_1.0": sum(1 for w in weights if w >= 0.8),
        }
        phases[phase_id] = {
            "name": name,
            "patterns": len(pats),
            "weight_histogram": buckets,
            "max_weight": max(weights) if weights else 0,
            "avg_weight": round(sum(weights) / len(weights), 3) if weights else 0,
        }
        total += len(pats)
        high_conf += buckets["high_0.8_1.0"]

    # Auto-tuner active overlay count (may not exist in fresh boot).
    tuner_overlay_size = 0
    try:
        ov = app.state.precision.export_state()
        if isinstance(ov, dict):
            tuner_overlay_size = len(ov.get("adjustments", {}) or {})
    except Exception:
        pass

    return {
        "total_patterns": total,
        "high_confidence_patterns": high_conf,
        "override_threshold": float(os.getenv("OVERRIDE_THRESHOLD", "0.80")),
        "phases": phases,
        "tuner_active_adjustments": tuner_overlay_size,
        "emoji_count": len(getattr(h, "_emojis", []) or []),
    }


_REQUEST_METRICS = {
    "boot_time": time.time(),
    "requests_total": 0,
    "analyze_total": 0,
    "alert_total": 0,
    "transcribe_total": 0,
    "ocr_total": 0,
    "llm_calls": 0,
}


@app.middleware("http")
async def _bump_metrics(request, call_next):
    """Bump the in-memory counters; cheap O(1), no I/O.

    Path → counter mapping:
      POST /analyze    → analyze_total
      POST /alert      → alert_total
      POST /transcribe → transcribe_total
      POST /ocr        → ocr_total
    Every request bumps requests_total. Errors are still counted (we
    measure load, not success rate).
    """
    _REQUEST_METRICS["requests_total"] += 1
    p = request.url.path
    if p == "/analyze" and request.method == "POST":
        _REQUEST_METRICS["analyze_total"] += 1
    elif p == "/alert" and request.method == "POST":
        _REQUEST_METRICS["alert_total"] += 1
    elif p == "/transcribe" and request.method == "POST":
        _REQUEST_METRICS["transcribe_total"] += 1
    elif p == "/ocr" and request.method == "POST":
        _REQUEST_METRICS["ocr_total"] += 1
    return await call_next(request)


@app.get("/admin/healthcheck-deep")
async def admin_healthcheck_deep():
    """Full health probe — includes LLM and STT round-trips. Slow (≤6s).

    Use sparingly (the panel only calls it once on demand). Each external
    check is bounded by its own timeout so a dead Groq doesn't make the
    whole probe hang.
    """
    out = {
        "service": "nahual-backend",
        "started_at": datetime.fromtimestamp(_REQUEST_METRICS["boot_time"]).isoformat(),
        "checks": {},
    }
    # SQLite: run a trivial query through the locked connection.
    try:
        app.state.db.list_alerts(limit=1)
        out["checks"]["db"] = {"ok": True}
    except Exception as e:
        out["checks"]["db"] = {"ok": False, "error": str(e)[:120]}

    # Anthropic — small ping so we know the model id and key are valid.
    if app.state.pipeline.llm.enabled:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                r = await client.post(
                    ANTHROPIC_MESSAGES_URL,
                    headers={
                        "x-api-key": os.getenv("ANTHROPIC_API_KEY", ""),
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
                        "max_tokens": 5,
                        "messages": [{"role": "user", "content": "ping"}],
                    },
                )
            out["checks"]["anthropic"] = {
                "ok": r.status_code == 200,
                "status": r.status_code,
                "model": os.getenv("ANTHROPIC_MODEL"),
            }
        except Exception as e:
            out["checks"]["anthropic"] = {"ok": False, "error": str(e)[:120]}
    else:
        out["checks"]["anthropic"] = {"ok": False, "reason": "disabled"}

    # Groq — only validates the key shape; actual transcribe needs a real audio file.
    if os.getenv("GROQ_API_KEY"):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
                )
            out["checks"]["groq"] = {"ok": r.status_code == 200, "status": r.status_code}
        except Exception as e:
            out["checks"]["groq"] = {"ok": False, "error": str(e)[:120]}
    else:
        out["checks"]["groq"] = {"ok": False, "reason": "GROQ_API_KEY unset"}

    out["all_ok"] = all(c.get("ok") for c in out["checks"].values())
    return out


@app.get("/admin/metrics")
def admin_metrics():
    """Lightweight request counters since boot. Updated by middleware above."""
    # Best-effort alerts count without locking on a missing helper.
    db_alerts = None
    try:
        if hasattr(app.state.db, "count_alerts"):
            db_alerts = app.state.db.count_alerts()
        elif hasattr(app.state.db, "stats"):
            stats = app.state.db.stats()
            db_alerts = (stats or {}).get("total_alerts")
    except Exception:
        pass

    return {
        **{k: v for k, v in _REQUEST_METRICS.items() if k != "boot_time"},
        "uptime_seconds": int(time.time() - _REQUEST_METRICS["boot_time"]),
        "alerts_in_db": db_alerts,
    }


@app.get("/admin/runtime-info")
def admin_runtime_info():
    """Aggregated ops view — combines version, dataset, metrics, and the
    last 5 alert ids/levels/dates without exposing PII. Single round-trip
    for the panel header strip + operator dashboards.
    """
    info_pieces: dict = {}

    # Version
    bi = _read_build_info()
    info_pieces["version"] = {
        "commit": (bi.get("commit") or "")[:10],
        "branch": bi.get("branch"),
        "committed_at": bi.get("committed_at"),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }

    # Dataset
    try:
        h = app.state.pipeline.heuristic
        total = sum(len(h._compiled_patterns.get(p, []))
                    for p in ("phase1", "phase2", "phase3", "phase4"))
        info_pieces["dataset"] = {
            "total_patterns": total,
            "phases": {
                p: len(h._compiled_patterns.get(p, []))
                for p in ("phase1", "phase2", "phase3", "phase4")
            },
        }
    except Exception:
        info_pieces["dataset"] = None

    # Bayesian
    try:
        if app.state.pipeline.bayesian is not None:
            s = app.state.pipeline.bayesian.get_stats()
            info_pieces["bayesian"] = {
                "total_docs": s.get("total_training_examples"),
                "vocab": s.get("vocabulary_size"),
                "classes": s.get("class_distribution"),
            }
    except Exception:
        info_pieces["bayesian"] = None

    # Metrics
    info_pieces["metrics"] = {
        k: v for k, v in _REQUEST_METRICS.items() if k != "boot_time"
    }
    info_pieces["metrics"]["uptime_seconds"] = int(
        time.time() - _REQUEST_METRICS["boot_time"]
    )

    # Recent alerts (id + level + platform + date — NO content/hash/PII).
    try:
        rows = app.state.db.list_alerts(limit=5, offset=0)
        info_pieces["recent_alerts"] = [
            {
                "id": r.get("id"),
                "created_at": r.get("created_at"),
                "platform": r.get("platform"),
                "risk_level": r.get("risk_level"),
                "phase_detected": r.get("phase_detected"),
                "override": bool(r.get("override_triggered")),
            }
            for r in rows
        ]
    except Exception:
        info_pieces["recent_alerts"] = []

    return info_pieces


# ---------------- STT / OCR (Phase 3) ----------------

GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"

OCR_SYSTEM_PROMPT = (
    "Extrae TODO el texto visible en esta imagen de una conversación de chat. "
    "Incluye cada mensaje exactamente como aparece, incluyendo emojis. "
    "Retorna SOLO el texto extraído, sin explicaciones ni formato adicional. "
    "Si no hay texto legible, responde 'NO_TEXT'."
)

ALLOWED_AUDIO_MIME = {"audio/ogg", "audio/mpeg", "audio/mp4", "audio/wav", "audio/webm", "audio/x-m4a", "audio/aac", "audio/flac", "audio/x-wav"}
ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif", "image/heic", "image/heif"}


def _normalize_mime(raw: str | None, default: str) -> str:
    """WhatsApp/Baileys sends MIME types like 'audio/ogg; codecs=opus' or
    'image/jpeg;charset=binary'. The strict set check rejected these as 415.
    Normalize to the bare type/subtype so the lookup matches.
    """
    m = (raw or default).split(";")[0].strip().lower()
    return m or default
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

    mime = _normalize_mime(file.content_type, "audio/ogg")
    if mime not in ALLOWED_AUDIO_MIME:
        raise HTTPException(415, f"unsupported audio type {mime!r}")
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

    media_type = _normalize_mime(file.content_type, "image/png")
    if media_type not in ALLOWED_IMAGE_MIME:
        raise HTTPException(415, f"unsupported image type {media_type!r}")

    b64 = base64.b64encode(image_bytes).decode("ascii")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
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
    body["bayesian"] = result.get("bayesian")
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
        "bayesian": result.get("bayesian"),
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


@app.get("/alerts", dependencies=PROTECTED)
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


@app.get("/alerts.csv", dependencies=PROTECTED)
def list_alerts_csv(
    limit: int = 500,
    status: str | None = None,
    risk_level: str | None = None,
):
    """CSV export for triage / handoff to authorities. PII-free by design:
    text_hash is the only "sensitive" field, and it's irreversible.
    """
    import csv
    import io

    if limit < 1 or limit > 5000:
        raise HTTPException(400, "limit must be in [1, 5000]")
    rows = app.state.db.list_alerts(
        limit=limit,
        offset=0,
        status=status,
        risk_level=risk_level,
    )
    columns = [
        "id", "created_at", "platform", "source", "risk_score", "risk_level",
        "phase_detected", "categories", "override_triggered", "status",
        "report_generated", "llm_used", "session_id", "text_hash",
    ]
    buf = io.StringIO()
    writer = csv.writer(buf, dialect="excel")
    writer.writerow(columns)
    for r in rows:
        cats = r.get("categories")
        if isinstance(cats, list):
            cats = ",".join(cats)
        writer.writerow([
            r.get(c) if c != "categories" else (cats or "") for c in columns
        ])
    csv_bytes = buf.getvalue().encode("utf-8-sig")  # BOM for Excel
    from fastapi.responses import Response

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="nahual-alerts.csv"',
        },
    )


@app.get("/alerts/{alert_id}", dependencies=PROTECTED)
def get_alert(alert_id: int):
    alert = app.state.db.get_alert(alert_id)
    if not alert:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return alert


@app.patch("/alerts/{alert_id}", dependencies=PROTECTED)
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


@app.post(
    "/alerts/{alert_id}/escalate",
    status_code=status.HTTP_200_OK,
    dependencies=PROTECTED,
)
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


@app.get(
    "/alerts/{alert_id}/history",
    response_model=list[AlertAction],
    dependencies=PROTECTED,
)
def alert_history(alert_id: int):
    """Audit trail for an alert — every status change, note and escalation."""
    if app.state.db.get_alert(alert_id) is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return app.state.db.list_actions(alert_id)


@app.get("/alerts/{alert_id}/why", dependencies=PROTECTED)
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


@app.get("/alerts/{alert_id}/legal", dependencies=PROTECTED)
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
