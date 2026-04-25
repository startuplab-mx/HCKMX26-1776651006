"""Outbound webhooks module: payload + dispatch + integration."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import webhooks  # noqa: E402


SAMPLE_ALERT = {
    "id": 42,
    "platform": "whatsapp",
    "risk_level": "PELIGRO",
    "risk_score": 1.0,
    "phase_detected": "coercion",
    "override_triggered": True,
    "summary": "demo",
    "reviewer": None,
}


# ---------------- payload schema ----------------


def test_build_payload_for_escalation():
    p = webhooks.build_payload(
        event="alert.escalated",
        alert=SAMPLE_ALERT,
        destination="088",
        reason="amenaza directa",
        reviewer="marco",
    )
    assert p["event"] == "alert.escalated"
    assert p["alert_id"] == 42
    assert p["risk_level"] == "PELIGRO"
    assert p["destination"] == "088"
    assert p["reason"] == "amenaza directa"
    assert p["reviewer"] == "marco"
    assert p["override_triggered"] is True
    assert "fired_at" in p


def test_build_payload_for_override_has_no_destination():
    p = webhooks.build_payload(event="alert.override", alert=SAMPLE_ALERT)
    assert p["event"] == "alert.override"
    assert p["destination"] is None
    assert p["reason"] is None


# ---------------- dispatch ----------------


def test_dispatch_zero_when_no_urls_configured(monkeypatch):
    monkeypatch.setenv("NAHUAL_WEBHOOK_URLS", "")
    n = webhooks.dispatch({"event": "x", "alert_id": 1})
    assert n == 0


def test_dispatch_uses_explicit_urls_arg(monkeypatch):
    """`urls` arg overrides env so tests don't depend on global state."""
    captured: list[tuple[str, dict]] = []

    def fake_post(url, payload):
        captured.append((url, payload))

    with patch.object(webhooks, "_post_one", side_effect=fake_post):
        n = webhooks.dispatch(
            {"event": "alert.escalated", "alert_id": 1},
            urls=["http://example.com/hook1", "http://example.com/hook2"],
        )
    # Threads are daemon — give them a moment to land.
    deadline = time.time() + 1.0
    while len(captured) < 2 and time.time() < deadline:
        time.sleep(0.01)
    assert n == 2
    assert {u for u, _ in captured} == {
        "http://example.com/hook1",
        "http://example.com/hook2",
    }


def test_post_one_swallows_network_errors():
    # Use a guaranteed-unreachable URL — the function must NOT raise.
    webhooks._post_one("http://127.0.0.1:1/never-listens", {"event": "x"})


def test_signature_header_set_when_secret_present(monkeypatch):
    monkeypatch.setenv("NAHUAL_WEBHOOK_SECRET", "topsecret")
    h = webhooks._headers()
    assert h["X-Nahual-Signature"] == "topsecret"


# ---------------- integration with API ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "wh_api.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    # Ensure no leftover env from earlier tests.
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    import importlib

    import database.db as db_module
    import main as main_module
    import webhooks as wh_module

    importlib.reload(wh_module)
    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app), main_module


def test_escalate_endpoint_fires_webhook(tmp_path):
    client, main_module = _client(tmp_path)
    fired: list[dict] = []
    with client:
        aid = client.post(
            "/alert", json={"text": "te voy a matar"}
        ).json()["id"]
        # patch the dispatch on the imported module reference inside main
        with patch.object(main_module.webhooks, "dispatch") as mock:
            mock.side_effect = lambda payload, **kw: fired.append(payload) or 1
            client.post(
                f"/alerts/{aid}/escalate",
                json={"destination": "088", "reason": "amenaza", "reviewer": "marco"},
            )
    assert len(fired) == 1
    assert fired[0]["event"] == "alert.escalated"
    assert fired[0]["destination"] == "088"


def test_alert_override_fires_webhook(tmp_path):
    client, main_module = _client(tmp_path)
    fired: list[dict] = []
    with client:
        with patch.object(main_module.webhooks, "dispatch") as mock:
            mock.side_effect = lambda payload, **kw: fired.append(payload) or 1
            client.post("/alert", json={"text": "te voy a matar"})
    # Death threat → override → webhook fires automatically.
    assert any(p["event"] == "alert.override" for p in fired)


def test_alert_safe_does_not_fire_webhook(tmp_path):
    client, main_module = _client(tmp_path)
    fired: list[dict] = []
    with client:
        with patch.object(main_module.webhooks, "dispatch") as mock:
            mock.side_effect = lambda payload, **kw: fired.append(payload) or 1
            client.post("/alert", json={"text": "vienes al cumple el sabado"})
    assert fired == []
