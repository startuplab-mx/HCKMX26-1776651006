"""Tests for the /admin observability endpoints (added in polish-2).

These are public read-only endpoints. They MUST never leak PII (alert IDs,
session IDs, message text, hashes) and MUST return the same shape regardless
of auth state.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "admin.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    os.environ["NAHUAL_API_KEY"] = ""
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


# ---------------- /admin/version ----------------


def test_admin_version_shape(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/admin/version")
        assert r.status_code == 200
        body = r.json()
        # Required keys; allow None for git fields when not in a checkout.
        for k in ("service", "commit", "branch", "committed_at", "environment", "python"):
            assert k in body
        assert body["service"] == "nahual-backend"
        # No PII shapes — body must not include 'alerts', 'session', 'phone'.
        assert all(
            k not in body for k in ("alerts", "session_id", "phone", "text")
        )


def test_admin_version_is_public_even_with_auth(tmp_path):
    """Auth-on must not 403 the version endpoint."""
    os.environ["DATABASE_PATH"] = str(tmp_path / "admin2.db")
    os.environ["NAHUAL_API_KEY"] = "topsecret"
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient
    with TestClient(main_module.app) as c:
        assert c.get("/admin/version").status_code == 200


# ---------------- /admin/dataset-info ----------------


def test_admin_dataset_info_returns_phase_counts(tmp_path):
    with _client(tmp_path) as c:
        body = c.get("/admin/dataset-info").json()
        assert body["total_patterns"] > 500  # we shipped 643 in polish-2
        assert body["high_confidence_patterns"] > 0
        assert body["override_threshold"] == 0.80
        # Phase 3 must be the densest in high_0.8_1.0 (override grade).
        p3 = body["phases"]["phase3"]
        assert p3["name"] == "Coerción"
        assert p3["weight_histogram"]["high_0.8_1.0"] >= 50
        # Sum of phase counts must equal total.
        total_from_phases = sum(p["patterns"] for p in body["phases"].values())
        assert total_from_phases == body["total_patterns"]


def test_admin_dataset_info_emoji_count(tmp_path):
    with _client(tmp_path) as c:
        body = c.get("/admin/dataset-info").json()
        assert body["emoji_count"] >= 5  # narco emoji set


# ---------------- /admin/metrics ----------------


def test_admin_metrics_counters_increment(tmp_path):
    with _client(tmp_path) as c:
        # Baseline.
        before = c.get("/admin/metrics").json()
        assert before["analyze_total"] == 0
        # Fire one analyze.
        c.post("/analyze", json={"text": "te voy a matar"})
        after = c.get("/admin/metrics").json()
        assert after["analyze_total"] == 1
        # Fire one alert.
        c.post("/alert", json={"text": "te voy a matar"})
        after2 = c.get("/admin/metrics").json()
        assert after2["alert_total"] == 1
        assert after2["analyze_total"] == 1  # didn't double-count
        # Uptime grows monotonically.
        assert after2["uptime_seconds"] >= 0
        # No boot_time leaked (private field).
        assert "boot_time" not in after2


def test_admin_metrics_no_pii(tmp_path):
    with _client(tmp_path) as c:
        body = c.get("/admin/metrics").json()
        # Must not include any field that could doxx an alert/session.
        assert all(
            k not in body for k in ("session_id", "phone", "text_hash", "ip", "user_id")
        )
