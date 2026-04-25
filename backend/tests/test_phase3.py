"""Phase 3 module: STT + OCR + anonymous contributions.

We mock httpx so tests don't reach Groq / Anthropic. The contributions
suite focuses on the no-PII contract: extra fields are forbidden by
Pydantic, plus we assert on the row shape after insert.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import Database  # noqa: E402


def _client(tmp_path: Path, *, groq_key: str = "", anthropic_key: str = ""):
    """Build a TestClient bound to a fresh DB.

    Caller can opt-in to provider keys (the default is empty so /transcribe
    and /ocr return 503). We set env BEFORE reloading main so the endpoints
    pick up the value at the per-request os.getenv check.
    """
    os.environ["DATABASE_PATH"] = str(tmp_path / "phase3.db")
    os.environ["GROQ_API_KEY"] = groq_key
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
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


# ---------------- /transcribe ----------------


def test_transcribe_503_when_groq_key_missing(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        r = client.post(
            "/transcribe",
            files={"file": ("audio.ogg", b"\x00\x01\x02", "audio/ogg")},
        )
        assert r.status_code == 503


def test_transcribe_400_on_empty_file(tmp_path):
    client, _ = _client(tmp_path, groq_key="test-key")
    with client:
        r = client.post(
            "/transcribe",
            files={"file": ("audio.ogg", b"", "audio/ogg")},
        )
        assert r.status_code == 400


def test_transcribe_returns_text_when_groq_ok(tmp_path):
    client, _ = _client(tmp_path, groq_key="test-key")

    class FakeResp:
        status_code = 200

        def json(self):
            return {"text": "yo quiero jale"}

    async def fake_post(self, url, *args, **kwargs):
        assert "groq.com" in url
        return FakeResp()

    with client, patch.object(httpx.AsyncClient, "post", new=fake_post):
        r = client.post(
            "/transcribe",
            files={"file": ("audio.ogg", b"\x00\x01\x02", "audio/ogg")},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["text"] == "yo quiero jale"
        assert body["source"] == "groq_whisper"


# ---------------- /ocr ----------------


def test_ocr_503_when_anthropic_key_missing(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        r = client.post(
            "/ocr",
            files={"file": ("img.png", b"\x89PNG\r\n", "image/png")},
        )
        assert r.status_code == 503


def test_ocr_415_for_unsupported_image(tmp_path):
    client, _ = _client(tmp_path, anthropic_key="sk-ant-real")
    with client:
        r = client.post(
            "/ocr",
            files={"file": ("doc.bmp", b"BM..", "image/bmp")},
        )
        assert r.status_code == 415


def test_ocr_returns_extracted_text(tmp_path):
    client, _ = _client(tmp_path, anthropic_key="sk-ant-real")

    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": [{"type": "text", "text": "deposita 500 spei"}]}

    async def fake_post(self, url, *args, **kwargs):
        assert "anthropic.com" in url
        return FakeResp()

    with client, patch.object(httpx.AsyncClient, "post", new=fake_post):
        r = client.post(
            "/ocr",
            files={"file": ("img.png", b"\x89PNG\r\n", "image/png")},
        )
        assert r.status_code == 200
        assert r.json()["text"] == "deposita 500 spei"
        assert r.json()["source"] == "claude_vision"


def test_ocr_no_text_returns_empty_string(tmp_path):
    client, _ = _client(tmp_path, anthropic_key="sk-ant-real")

    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": [{"type": "text", "text": "NO_TEXT"}]}

    async def fake_post(self, url, *args, **kwargs):
        return FakeResp()

    with client, patch.object(httpx.AsyncClient, "post", new=fake_post):
        r = client.post(
            "/ocr",
            files={"file": ("img.png", b"\x89PNG\r\n", "image/png")},
        )
        assert r.status_code == 200
        assert r.json()["text"] == ""


# ---------------- /contribute (no PII) ----------------


def _valid_contribution():
    return {
        "platform": "whatsapp",
        "risk_level": "PELIGRO",
        "risk_score": 1.0,
        "phase_detected": "coercion",
        "categories": ["coercion"],
        "pattern_ids": ["phase3.001", "emoji.000"],
        "source_type": "text",
        "region": "Coahuila",
        "llm_used": False,
        "override_triggered": True,
    }


def test_contribute_persists_metadata(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        r = client.post("/contribute", json=_valid_contribution())
        assert r.status_code == 201
        assert r.json()["contributed"] is True

        stats = client.get("/contributions/stats").json()
        assert stats["total_contributions"] == 1
        assert stats["by_platform"]["whatsapp"] == 1
        assert stats["by_level"]["PELIGRO"] == 1
        assert stats["by_region"]["Coahuila"] == 1


def test_contribute_rejects_extra_fields_pii(tmp_path):
    """The contract is no-PII. Pydantic must reject any unknown field."""
    client, _ = _client(tmp_path)
    with client:
        for forbidden in ("text", "contact_phone", "session_id", "original_text"):
            payload = {**_valid_contribution(), forbidden: "secret"}
            r = client.post("/contribute", json=payload)
            assert r.status_code == 422, f"{forbidden} should be rejected"


def test_contribute_rejects_invalid_risk_level(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        payload = {**_valid_contribution(), "risk_level": "ULTRA"}
        r = client.post("/contribute", json=payload)
        assert r.status_code == 422


def test_contribute_rejects_invalid_score(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        payload = {**_valid_contribution(), "risk_score": 9.0}
        r = client.post("/contribute", json=payload)
        assert r.status_code == 422


def test_contribute_rejects_long_region(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        payload = {**_valid_contribution(), "region": "x" * 200}
        r = client.post("/contribute", json=payload)
        assert r.status_code == 422


def test_contribution_db_row_has_no_pii_fields(tmp_path):
    """Direct DB inspection: row schema must not contain anything PII-shaped."""
    db = Database(path=tmp_path / "direct.db")
    db.insert_contribution(
        platform="whatsapp",
        risk_level="ATENCION",
        risk_score=0.4,
        phase_detected="captacion",
        categories=["captacion"],
        pattern_ids=["phase1.000"],
        source_type="audio",
        region="CDMX",
    )
    row = db._conn.execute(
        "SELECT * FROM contributions LIMIT 1"
    ).fetchone()
    keys = set(row.keys())
    pii_fields = {"text", "summary", "contact_phone", "session_id", "original_text_hash"}
    assert keys.isdisjoint(pii_fields), f"PII leaked: {keys & pii_fields}"


def test_top_patterns_aggregation(tmp_path):
    client, _ = _client(tmp_path)
    with client:
        # Three contributions all matching 'phase3.001'.
        for _ in range(3):
            client.post("/contribute", json=_valid_contribution())
        # One contribution matching only 'phase1.000'.
        payload = {
            **_valid_contribution(),
            "phase_detected": "captacion",
            "risk_level": "ATENCION",
            "risk_score": 0.4,
            "pattern_ids": ["phase1.000"],
            "categories": ["captacion"],
            "override_triggered": False,
        }
        client.post("/contribute", json=payload)

        stats = client.get("/contributions/stats").json()
        top = {row["pattern_id"]: row["count"] for row in stats["top_patterns"]}
        assert top["phase3.001"] == 3
        assert top["phase1.000"] == 1


def test_pattern_ids_propagate_to_alert_response(tmp_path):
    """End-to-end: /alert returns pattern_ids + source_type so the bot can
    feed /contribute with full metadata without re-classifying."""
    client, _ = _client(tmp_path)
    with client:
        r = client.post(
            "/alert",
            json={
                "text": "si intentas escapar te descuartizo",
                "source_type": "audio",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["source_type"] == "audio"
        assert isinstance(body["pattern_ids"], list)
        assert len(body["pattern_ids"]) >= 1
