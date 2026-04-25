"""Time-series analytics module: DB + HTTP coverage."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import Database  # noqa: E402


def _fresh_db(tmp_path: Path) -> Database:
    return Database(path=tmp_path / "ts.db")


def _insert(db: Database, level: str, override: bool = False, status: str = "pending") -> int:
    aid = db.insert_alert(
        platform="whatsapp",
        source="bot",
        risk_score={"PELIGRO": 1.0, "ATENCION": 0.4, "SEGURO": 0.0}[level],
        risk_level=level,
        phase_detected="coercion" if level == "PELIGRO" else None,
        categories=[],
        summary="x",
        text_hash="h" * 64,
        contact_phone=None,
        llm_used=False,
        override_triggered=override,
        session_id=None,
    )
    if status != "pending":
        db.update_alert_status(aid, status=status, reviewer="t")
    return aid


# ---------------- DB unit ----------------


def test_timeseries_empty_db(tmp_path):
    db = _fresh_db(tmp_path)
    assert db.timeseries(interval="hour", hours=24) == []


def test_timeseries_groups_same_bucket(tmp_path):
    db = _fresh_db(tmp_path)
    _insert(db, "PELIGRO", override=True)
    _insert(db, "ATENCION")
    _insert(db, "SEGURO")
    rows = db.timeseries(interval="hour", hours=24)
    assert len(rows) == 1
    bucket = rows[0]
    assert bucket["total"] == 3
    assert bucket["by_level"] == {"PELIGRO": 1, "ATENCION": 1, "SEGURO": 1}
    assert bucket["overrides"] == 1


def test_timeseries_counts_escalated(tmp_path):
    db = _fresh_db(tmp_path)
    _insert(db, "PELIGRO", override=True, status="escalated")
    _insert(db, "PELIGRO", override=True)
    rows = db.timeseries(interval="hour", hours=24)
    assert rows[0]["escalated"] == 1


def test_timeseries_invalid_interval_raises(tmp_path):
    db = _fresh_db(tmp_path)
    with pytest.raises(ValueError):
        db.timeseries(interval="quarter-hour", hours=24)


def test_timeseries_hours_validation(tmp_path):
    db = _fresh_db(tmp_path)
    with pytest.raises(ValueError):
        db.timeseries(interval="hour", hours=0)


def test_timeseries_day_interval(tmp_path):
    db = _fresh_db(tmp_path)
    _insert(db, "PELIGRO")
    rows = db.timeseries(interval="day", hours=24)
    assert len(rows) == 1
    # day bucket key is date-only (YYYY-MM-DD).
    assert len(rows[0]["bucket"]) == 10


# ---------------- HTTP integration ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "ts_api.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_timeseries_endpoint_returns_array(tmp_path):
    with _client(tmp_path) as c:
        c.post("/alert", json={"text": "si intentas escapar te descuartizo"})
        r = c.get("/stats/timeseries?interval=hour&hours=24")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["by_level"]["PELIGRO"] == 1
        assert body[0]["overrides"] == 1


def test_timeseries_endpoint_rejects_bad_interval(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/stats/timeseries?interval=fortnight&hours=24")
        assert r.status_code == 400


def test_timeseries_endpoint_rejects_bad_hours(tmp_path):
    with _client(tmp_path) as c:
        r1 = c.get("/stats/timeseries?interval=hour&hours=0")
        r2 = c.get("/stats/timeseries?interval=hour&hours=99999")
        assert r1.status_code == 400
        assert r2.status_code == 400
