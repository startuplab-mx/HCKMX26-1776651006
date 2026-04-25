"""API key auth (security correction #1).

The auth dependency is opt-in: when NAHUAL_API_KEY is empty/unset, every
endpoint behaves as before (this keeps the prior 126-test suite green).
When the env var is set, sensitive endpoints reject requests without a
matching X-API-Key header with HTTP 403.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _client(tmp_path: Path, *, api_key: str = ""):
    """Reload main with an explicit NAHUAL_API_KEY value."""
    os.environ["DATABASE_PATH"] = str(tmp_path / "auth.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    os.environ["NAHUAL_API_KEY"] = api_key
    os.environ["PRECISION_TUNING_INTERVAL"] = "999"
    import importlib

    import database.db as db_module
    import main as main_module
    import webhooks as wh_module

    importlib.reload(wh_module)
    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


# ---------------- Public endpoints stay open even with auth on ----------------


def test_public_endpoints_skip_auth_when_key_set(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        # /health, /analyze, /alert, /contributions/stats, /transcribe→503,
        # /stats, /report/{id}, /profile/{id}, /feedback are all PUBLIC and
        # respond *without* the X-API-Key header.
        assert c.get("/health").status_code == 200
        assert c.post("/analyze", json={"text": "hola"}).status_code == 200
        aid = c.post("/alert", json={"text": "te voy a matar"}).json()["id"]
        assert c.get("/contributions/stats").status_code == 200
        # /transcribe is public-input — without GROQ_API_KEY it 503s, not 403.
        r = c.post("/transcribe", files={"file": ("a.ogg", b"\x00", "audio/ogg")})
        assert r.status_code in (400, 503)
        # /stats is also public.
        assert c.get("/stats").status_code == 200
        # /report, /profile, /feedback are public per hackathon demo policy.
        assert c.post(f"/report/{aid}").status_code == 200
        assert c.get("/profile/u-public").status_code == 200
        fb = {"feedback_type": "confirm", "pattern_ids": ["phase3.001"]}
        assert c.post("/feedback", json=fb).status_code == 201


def test_health_no_longer_exposes_db_path(tmp_path):
    """Security correction #6: db_path removed from /health response."""
    with _client(tmp_path) as c:
        body = c.get("/health").json()
        assert "db_path" not in body
        assert body["status"] == "ok"
        assert "auth_enforced" in body


# ---------------- Sensitive endpoints with auth disabled (default) ----------------


def test_sensitive_endpoints_open_when_no_key_configured(tmp_path):
    """When NAHUAL_API_KEY is unset, sensitive endpoints are open."""
    with _client(tmp_path, api_key="") as c:
        # /alerts list — should NOT 403 just because no key was sent.
        assert c.get("/alerts").status_code == 200
        # /sessions/{id} get unknown returns 404, not 403.
        assert c.get("/sessions/u-test").status_code == 404


# ---------------- Sensitive endpoints with auth enabled ----------------


def test_get_alerts_403_without_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        r = c.get("/alerts")
        assert r.status_code == 403


def test_get_alerts_200_with_correct_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        r = c.get("/alerts", headers={"X-API-Key": "topsecret"})
        assert r.status_code == 200


def test_get_alerts_403_with_wrong_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        r = c.get("/alerts", headers={"X-API-Key": "wrong"})
        assert r.status_code == 403


def test_patch_alert_requires_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        # Create an alert through the *public* /alert endpoint first.
        aid = c.post(
            "/alert", json={"text": "te voy a matar"}
        ).json()["id"]
        # PATCH without key → 403.
        r1 = c.patch(f"/alerts/{aid}", json={"status": "reviewed"})
        assert r1.status_code == 403
        # PATCH with key → 200.
        r2 = c.patch(
            f"/alerts/{aid}",
            json={"status": "reviewed"},
            headers={"X-API-Key": "topsecret"},
        )
        assert r2.status_code == 200


def test_escalate_requires_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        aid = c.post(
            "/alert", json={"text": "te voy a matar"}
        ).json()["id"]
        r1 = c.post(f"/alerts/{aid}/escalate", json={"destination": "088"})
        assert r1.status_code == 403
        r2 = c.post(
            f"/alerts/{aid}/escalate",
            json={"destination": "088"},
            headers={"X-API-Key": "topsecret"},
        )
        assert r2.status_code == 200


def test_sessions_endpoints_require_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        assert c.get("/sessions/u").status_code == 403
        assert (
            c.put("/sessions/u", json={"current_step": "result"}).status_code == 403
        )
        assert c.delete("/sessions/u").status_code == 403
        # With key.
        h = {"X-API-Key": "topsecret"}
        assert c.put("/sessions/u", json={"current_step": "result"}, headers=h).status_code == 200
        assert c.get("/sessions/u", headers=h).status_code == 200
        assert c.delete("/sessions/u", headers=h).status_code == 204


def test_precision_endpoints_require_key(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        assert c.get("/precision/diagnostics").status_code == 403
        assert c.get("/precision/stats").status_code == 403
        assert c.post("/precision/tune").status_code == 403
        assert c.get("/precision/state").status_code == 403
        h = {"X-API-Key": "topsecret"}
        assert c.get("/precision/diagnostics", headers=h).status_code == 200
        assert c.get("/precision/stats", headers=h).status_code == 200


def test_risk_history_requires_key_but_profile_is_public(tmp_path):
    with _client(tmp_path, api_key="topsecret") as c:
        # /profile/{id} is PUBLIC — pitch demo + extension overlay use it
        # without a key. Returns 200 with status=no_data when never seen.
        assert c.get("/profile/u").status_code == 200
        # /risk-history/* remains protected (write/delete operator surface).
        assert c.get("/risk-history/u").status_code == 403
        assert c.delete("/risk-history/u").status_code == 403
        h = {"X-API-Key": "topsecret"}
        assert c.get("/risk-history/u", headers=h).status_code == 200


def test_report_is_public(tmp_path):
    """PDF report is PUBLIC for demo: any alert ID can be exported.

    Rationale: the alert IDs themselves are protected (/alerts requires key),
    so to download a report you still need to know the integer id, and the
    PDF body itself contains no PII (only hashes + categories).
    """
    with _client(tmp_path, api_key="topsecret") as c:
        aid = c.post("/alert", json={"text": "te voy a matar"}).json()["id"]
        r = c.post(f"/report/{aid}")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/pdf")


def test_feedback_is_public(tmp_path):
    """User feedback (/feedback) is PUBLIC: bot + panel + extension submit
    confirm/deny without a key. The auto-tuner treats every signal as a
    weak prior and never trusts a single source."""
    with _client(tmp_path, api_key="topsecret") as c:
        payload = {"feedback_type": "confirm", "pattern_ids": ["phase3.001"]}
        r = c.post("/feedback", json=payload)
        assert r.status_code == 201


# ---------------- Other security corrections ----------------


def test_transcribe_rejects_unsupported_mime(tmp_path):
    """Security correction #3: ALLOWED_AUDIO_MIME enforced."""
    with _client(tmp_path) as c:
        os.environ["GROQ_API_KEY"] = "fake-key-just-for-test"
        # Reload so the endpoint sees the env var.
        import importlib
        import main as main_module
        importlib.reload(main_module)

        from fastapi.testclient import TestClient
        with TestClient(main_module.app) as c2:
            r = c2.post(
                "/transcribe",
                files={"file": ("evil.exe", b"MZ\x90\x00", "application/octet-stream")},
            )
            assert r.status_code == 415


def test_health_includes_auth_enforced_flag(tmp_path):
    with _client(tmp_path, api_key="x") as c:
        body = c.get("/health").json()
        assert body["auth_enforced"] is True
    with _client(tmp_path, api_key="") as c:
        body = c.get("/health").json()
        assert body["auth_enforced"] is False
