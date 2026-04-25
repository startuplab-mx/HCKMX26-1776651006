"""Moderation/triage module: DB + HTTP coverage."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import ALERT_STATUSES, Database  # noqa: E402


def _fresh_db(tmp_path: Path) -> Database:
    return Database(path=tmp_path / "mod.db")


def _insert_peligro(db: Database) -> int:
    return db.insert_alert(
        platform="whatsapp",
        source="bot",
        risk_score=1.0,
        risk_level="PELIGRO",
        phase_detected="coercion",
        categories=["coercion"],
        summary="demo",
        text_hash="h" * 64,
        contact_phone=None,
        llm_used=False,
        override_triggered=True,
        session_id="demo",
    )


# ---------------- DB unit tests ----------------


def test_new_alerts_default_to_pending(tmp_path):
    db = _fresh_db(tmp_path)
    aid = _insert_peligro(db)
    alert = db.get_alert(aid)
    assert alert["status"] == "pending"
    assert alert["notes"] is None
    assert alert["reviewer"] is None


def test_update_alert_status_changes_state_and_logs_action(tmp_path):
    db = _fresh_db(tmp_path)
    aid = _insert_peligro(db)
    updated = db.update_alert_status(aid, status="reviewed", reviewer="marco")
    assert updated["status"] == "reviewed"
    assert updated["reviewer"] == "marco"
    actions = db.list_actions(aid)
    assert len(actions) == 1
    assert actions[0]["action"] == "status_change"
    assert actions[0]["from_value"] == "pending"
    assert actions[0]["to_value"] == "reviewed"
    assert actions[0]["reviewer"] == "marco"


def test_update_alert_notes_without_status_logs_note_action(tmp_path):
    db = _fresh_db(tmp_path)
    aid = _insert_peligro(db)
    db.update_alert_status(aid, notes="contacté al tutor", reviewer="marco")
    actions = db.list_actions(aid)
    assert len(actions) == 1
    assert actions[0]["action"] == "note"
    assert actions[0]["notes"] == "contacté al tutor"


def test_escalate_writes_destination_in_notes(tmp_path):
    db = _fresh_db(tmp_path)
    aid = _insert_peligro(db)
    updated = db.escalate_alert(aid, destination="088", reason="amenaza directa", reviewer="marco")
    assert updated["status"] == "escalated"
    actions = db.list_actions(aid)
    assert any(a["action"] == "escalation" for a in actions)
    esc = next(a for a in actions if a["action"] == "escalation")
    assert "destination=088" in esc["notes"]
    assert "reason=amenaza directa" in esc["notes"]


def test_invalid_status_raises(tmp_path):
    db = _fresh_db(tmp_path)
    aid = _insert_peligro(db)
    with pytest.raises(ValueError):
        db.update_alert_status(aid, status="weird")


def test_all_statuses_roundtrip(tmp_path):
    db = _fresh_db(tmp_path)
    aid = _insert_peligro(db)
    for s in ALERT_STATUSES:
        updated = db.update_alert_status(aid, status=s, reviewer="marco")
        assert updated["status"] == s


def test_list_alerts_filters_by_status(tmp_path):
    db = _fresh_db(tmp_path)
    a = _insert_peligro(db)
    b = _insert_peligro(db)
    db.update_alert_status(a, status="reviewed", reviewer="marco")
    reviewed = db.list_alerts(status="reviewed")
    pending = db.list_alerts(status="pending")
    assert [r["id"] for r in reviewed] == [a]
    assert [r["id"] for r in pending] == [b]


def test_update_nonexistent_alert_returns_none(tmp_path):
    db = _fresh_db(tmp_path)
    assert db.update_alert_status(9999, status="reviewed") is None
    assert db.escalate_alert(9999, destination="088") is None


# ---------------- HTTP integration tests ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "mod_api.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_patch_alert_updates_status(tmp_path):
    with _client(tmp_path) as c:
        aid = c.post("/alert", json={"text": "si intentas escapar te descuartizo"}).json()["id"]
        r = c.patch(f"/alerts/{aid}", json={"status": "reviewed", "reviewer": "marco"})
        assert r.status_code == 200
        assert r.json()["status"] == "reviewed"


def test_patch_rejects_invalid_status(tmp_path):
    with _client(tmp_path) as c:
        aid = c.post("/alert", json={"text": "si intentas escapar te descuartizo"}).json()["id"]
        r = c.patch(f"/alerts/{aid}", json={"status": "nonsense"})
        assert r.status_code == 422  # pydantic rejects before the endpoint runs


def test_escalate_endpoint_persists(tmp_path):
    with _client(tmp_path) as c:
        aid = c.post("/alert", json={"text": "si intentas escapar te descuartizo"}).json()["id"]
        r = c.post(
            f"/alerts/{aid}/escalate",
            json={"destination": "088", "reason": "amenaza directa", "reviewer": "marco"},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "escalated"

        hist = c.get(f"/alerts/{aid}/history").json()
        assert any(a["action"] == "escalation" for a in hist)


def test_history_404_for_missing_alert(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/alerts/99999/history")
        assert r.status_code == 404


def test_list_alerts_status_filter(tmp_path):
    with _client(tmp_path) as c:
        a = c.post("/alert", json={"text": "si intentas escapar te descuartizo"}).json()["id"]
        c.post("/alert", json={"text": "si intentas escapar te descuartizo"})
        c.patch(f"/alerts/{a}", json={"status": "reviewed", "reviewer": "marco"})
        reviewed = c.get("/alerts?status=reviewed").json()
        pending = c.get("/alerts?status=pending").json()
        assert [r["id"] for r in reviewed] == [a]
        assert len(pending) == 1
        assert pending[0]["id"] != a


def test_stats_includes_by_status(tmp_path):
    with _client(tmp_path) as c:
        a = c.post("/alert", json={"text": "si intentas escapar te descuartizo"}).json()["id"]
        c.post(f"/alerts/{a}/escalate", json={"destination": "088"})
        stats = c.get("/stats").json()
        assert "by_status" in stats
        assert stats["by_status"]["escalated"] == 1
        assert stats["by_status"]["pending"] == 0
