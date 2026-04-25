"""HTTP integration tests using FastAPI TestClient — no network needed."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _client(tmp_path: Path):
    """Return a TestClient bound to a fresh DB and LLM disabled.

    Lifespan runs when the caller enters the `with` block, by which time the
    db singleton has been reset to point at the temp path.
    """
    os.environ["DATABASE_PATH"] = str(tmp_path / "test_nahual.db")
    os.environ["ANTHROPIC_API_KEY"] = ""  # LLMLayer.enabled becomes False
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_health(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_analyze_safe(tmp_path):
    with _client(tmp_path) as c:
        r = c.post("/analyze", json={"text": "vienes al cumple el sabado?", "use_llm": False})
        assert r.status_code == 200
        assert r.json()["risk_level"] == "SEGURO"


def test_analyze_override_coercion(tmp_path):
    with _client(tmp_path) as c:
        r = c.post(
            "/analyze",
            json={"text": "si intentas escapar te descuartizo", "use_llm": False},
        )
        body = r.json()
        assert r.status_code == 200
        assert body["override_triggered"] is True
        assert body["risk_level"] == "PELIGRO"


def test_alert_persists_and_lists(tmp_path):
    with _client(tmp_path) as c:
        r = c.post(
            "/alert",
            json={
                "text": "manda nudes o las fotos van a tu escuela",
                "platform": "instagram",
                "source": "extension",
            },
        )
        assert r.status_code == 201
        alert_id = r.json()["id"]

        r2 = c.get(f"/alerts/{alert_id}")
        assert r2.status_code == 200
        assert r2.json()["override_triggered"] is True

        r3 = c.get("/alerts")
        assert any(a["id"] == alert_id for a in r3.json())


def test_stats_includes_seeded_levels(tmp_path):
    with _client(tmp_path) as c:
        c.post("/alert", json={"text": "si intentas escapar te descuartizo"})
        c.post("/alert", json={"text": "vienes al cumple"})
        r = c.get("/stats")
        body = r.json()
        assert r.status_code == 200
        assert body["total_alerts"] >= 2
        assert "SEGURO" in body["by_level"]
        assert "PELIGRO" in body["by_level"]


def test_report_generates_pdf(tmp_path):
    with _client(tmp_path) as c:
        rid = c.post("/alert", json={"text": "si intentas escapar te descuartizo"}).json()["id"]
        r = c.post(f"/report/{rid}")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/pdf")
        assert r.content.startswith(b"%PDF")


def test_report_404_for_missing_alert(tmp_path):
    with _client(tmp_path) as c:
        r = c.post("/report/99999")
        assert r.status_code == 404
