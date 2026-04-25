"""
Outbound webhook dispatcher.

Fires HTTP POSTs to configured URLs when significant events happen
(escalation, automatic override on PELIGRO). Fail-soft by design — a
webhook failure must NEVER bubble up into the request that triggered it,
because the alert pipeline is more important than any external integration.

Configuration: comma-separated URLs in NAHUAL_WEBHOOK_URLS env var.
Optional NAHUAL_WEBHOOK_SECRET is sent as `X-Nahual-Signature` for naive
auth at the receiving end (not HMAC — placeholder for hackathon scope).

Payload schema (stable):
    {
      "event": "alert.escalated" | "alert.override",
      "alert_id": int,
      "platform": str,
      "risk_level": "PELIGRO" | "ATENCION" | "SEGURO",
      "risk_score": float,
      "phase_detected": str | null,
      "override_triggered": bool,
      "destination": str | null,    # only for escalations
      "reason": str | null,         # only for escalations
      "reviewer": str | null,
      "summary": str,
      "fired_at": ISO-8601 UTC
    }
"""
from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT_S = 2.0


def _configured_urls() -> list[str]:
    raw = os.getenv("NAHUAL_WEBHOOK_URLS", "")
    return [u.strip() for u in raw.split(",") if u.strip()]


def _headers() -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Nahual-Webhook/1.0",
    }
    secret = os.getenv("NAHUAL_WEBHOOK_SECRET")
    if secret:
        headers["X-Nahual-Signature"] = secret
    return headers


def build_payload(
    *,
    event: str,
    alert: dict[str, Any],
    destination: str | None = None,
    reason: str | None = None,
    reviewer: str | None = None,
) -> dict[str, Any]:
    return {
        "event": event,
        "alert_id": alert["id"],
        "platform": alert["platform"],
        "risk_level": alert["risk_level"],
        "risk_score": alert["risk_score"],
        "phase_detected": alert.get("phase_detected"),
        "override_triggered": bool(alert.get("override_triggered")),
        "destination": destination,
        "reason": reason,
        "reviewer": reviewer or alert.get("reviewer"),
        "summary": alert.get("summary"),
        "fired_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _post_one(url: str, payload: dict[str, Any], *, max_retries: int = 3) -> None:
    """POST with bounded exponential backoff retry. Each retry budget is
    aligned with WEBHOOK_TIMEOUT_S so the total wall time stays small even
    in the worst case (≈ 2 + 1 + 2 + 1 + 4 + 1 = 11s max, but typical happy
    path is one 200 OK in <1s).

    Caller still gets fire-and-forget semantics because dispatch() runs us
    in a daemon thread.
    """
    backoff = (1.0, 2.0, 4.0)  # seconds between retries
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=WEBHOOK_TIMEOUT_S) as client:
                r = client.post(url, json=payload, headers=_headers())
            if r.status_code < 400:
                return  # success
            # 4xx is a permanent error — retrying won't help.
            if 400 <= r.status_code < 500:
                logger.warning("webhook %s returned %s (no retry on 4xx)", url, r.status_code)
                return
            logger.warning("webhook %s returned %s (will retry)", url, r.status_code)
        except Exception as e:
            logger.warning("webhook %s failed (attempt %d/%d): %s", url, attempt + 1, max_retries, e)
        if attempt < len(backoff):
            import time as _t
            _t.sleep(backoff[attempt])
    logger.error("webhook %s exhausted %d retries", url, max_retries)


def dispatch(payload: dict[str, Any], *, urls: list[str] | None = None) -> int:
    """Fire payload to all configured URLs in background threads.

    Returns the number of webhooks actually fired (0 if none configured).
    The threads are daemon=True so they don't block app shutdown.
    """
    targets = urls if urls is not None else _configured_urls()
    if not targets:
        return 0
    for url in targets:
        threading.Thread(
            target=_post_one,
            args=(url, payload),
            daemon=True,
            name=f"webhook-{payload.get('event','?')}",
        ).start()
    return len(targets)
