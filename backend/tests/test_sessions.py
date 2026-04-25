"""Sessions persistence module: DB + HTTP coverage."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import Database  # noqa: E402


def _fresh_db(tmp_path: Path) -> Database:
    return Database(path=tmp_path / "sess.db")


# ---------------- DB unit ----------------


def test_get_missing_session_returns_none(tmp_path):
    db = _fresh_db(tmp_path)
    assert db.get_session("nope") is None


def test_upsert_creates_then_updates(tmp_path):
    db = _fresh_db(tmp_path)
    db.upsert_session("u1", "recibir_msg", {"foo": 1})
    s = db.get_session("u1")
    assert s["current_step"] == "recibir_msg"
    assert s["data"] == {"foo": 1}

    db.upsert_session("u1", "notify", {"foo": 2, "bar": "x"})
    s2 = db.get_session("u1")
    assert s2["current_step"] == "notify"
    assert s2["data"] == {"foo": 2, "bar": "x"}


def test_delete_session_removes_row(tmp_path):
    db = _fresh_db(tmp_path)
    db.upsert_session("u1", "recibir_msg")
    db.delete_session("u1")
    assert db.get_session("u1") is None


# ---------------- HTTP integration ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "sess_api.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_get_unknown_session_returns_404(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/sessions/nope")
        assert r.status_code == 404


def test_put_creates_then_get_returns_state(tmp_path):
    with _client(tmp_path) as c:
        r = c.put(
            "/sessions/abc",
            json={"current_step": "result", "data": {"lastAlertId": 7}},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["current_step"] == "result"
        assert body["data"] == {"lastAlertId": 7}

        r2 = c.get("/sessions/abc")
        assert r2.status_code == 200
        assert r2.json()["data"]["lastAlertId"] == 7


def test_put_updates_existing_session(tmp_path):
    with _client(tmp_path) as c:
        c.put("/sessions/abc", json={"current_step": "recibir_msg"})
        r = c.put("/sessions/abc", json={"current_step": "notify", "data": {"phone": "+5255"}})
        assert r.status_code == 200
        assert r.json()["current_step"] == "notify"
        assert r.json()["data"] == {"phone": "+5255"}


def test_delete_session(tmp_path):
    with _client(tmp_path) as c:
        c.put("/sessions/abc", json={"current_step": "result"})
        r = c.delete("/sessions/abc")
        assert r.status_code == 204
        assert c.get("/sessions/abc").status_code == 404


def test_put_validates_required_field(tmp_path):
    with _client(tmp_path) as c:
        r = c.put("/sessions/abc", json={})
        assert r.status_code == 422
