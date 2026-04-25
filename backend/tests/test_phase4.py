"""Phase 4 — escalation + explainability + risk profile + ATENCION→PELIGRO bump."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classifier.escalation import EscalationDetector  # noqa: E402
from classifier.heuristic import HeuristicClassifier  # noqa: E402
from classifier.llm_layer import LLMLayer  # noqa: E402
from classifier.pipeline import Pipeline, build_why  # noqa: E402
from database.db import Database  # noqa: E402


# ---------------- escalation unit ----------------


def _detector(tmp_path: Path) -> tuple[EscalationDetector, Database]:
    db = Database(path=tmp_path / "esc.db")
    return EscalationDetector(db), db


def test_escalation_insufficient_data_on_first_call(tmp_path):
    det, _ = _detector(tmp_path)
    out = det.analyze_escalation("s1", 0.20, "ATENCION", "captacion")
    assert out["trend"] == "insufficient_data"
    assert out["alert_escalation"] is False
    assert out["history_length"] == 1


def test_escalation_increasing_trend(tmp_path):
    det, _ = _detector(tmp_path)
    det.analyze_escalation("s1", 0.10, "SEGURO", "captacion")
    det.analyze_escalation("s1", 0.40, "ATENCION", "captacion")
    out = det.analyze_escalation("s1", 0.65, "ATENCION", "enganche")
    assert out["trend"] == "increasing"
    assert out["velocity"] > 0.15
    assert out["alert_escalation"] is True


def test_escalation_phase_progression_triggers_alert(tmp_path):
    det, _ = _detector(tmp_path)
    det.analyze_escalation("s1", 0.20, "SEGURO", "captacion")
    det.analyze_escalation("s1", 0.30, "ATENCION", "enganche")
    out = det.analyze_escalation("s1", 0.40, "ATENCION", "coercion")
    assert out["phase_progression"] is True
    assert out["alert_escalation"] is True


def test_escalation_decreasing_does_not_alert(tmp_path):
    det, _ = _detector(tmp_path)
    det.analyze_escalation("s1", 0.80, "PELIGRO", "coercion")
    det.analyze_escalation("s1", 0.40, "ATENCION", "enganche")
    out = det.analyze_escalation("s1", 0.10, "SEGURO", None)
    assert out["trend"] == "decreasing"
    assert out["alert_escalation"] is False


def test_escalation_rapid_jump_flagged(tmp_path):
    det, _ = _detector(tmp_path)
    det.analyze_escalation("s1", 0.10, "SEGURO", "captacion")
    out = det.analyze_escalation("s1", 0.55, "ATENCION", "enganche")
    assert out["rapid"] is True
    assert out["alert_escalation"] is True


def test_escalation_isolated_per_session(tmp_path):
    det, _ = _detector(tmp_path)
    det.analyze_escalation("a", 0.10, "SEGURO", "captacion")
    det.analyze_escalation("a", 0.40, "ATENCION", "enganche")
    other = det.analyze_escalation("b", 0.10, "SEGURO", "captacion")
    assert other["history_length"] == 1
    assert other["trend"] == "insufficient_data"


# ---------------- heuristic explanations + why ----------------


def test_build_why_dedupes_and_sorts_by_severity():
    explanations = [
        {"type": "Captación", "what": "oferta económica", "severity": "media"},
        {"type": "Coerción", "what": "amenaza directa", "severity": "alta"},
        {"type": "Captación", "what": "oferta económica", "severity": "media"},  # dup
    ]
    why = build_why(explanations)
    assert why[0].startswith("Se detectó amenaza directa")
    assert len(why) == 2  # duplicate dropped


def test_build_why_caps_at_limit():
    explanations = [
        {"type": "Captación", "what": f"señal {i}", "severity": "alta"} for i in range(20)
    ]
    why = build_why(explanations, limit=4)
    assert len(why) == 4


def test_heuristic_emits_explanations():
    h = HeuristicClassifier()
    r = h.classify("yo quiero jale, $15,000 semanales 🍕")
    exps = r["explanations"]
    assert len(exps) >= 1
    types = {e["type"] for e in exps}
    assert "Captación" in types
    assert all("severity" in e for e in exps)


# ---------------- pipeline ATENCION→PELIGRO bump ----------------


class _OfflineLLM(LLMLayer):
    @property
    def enabled(self) -> bool:  # pragma: no cover (trivial)
        return False


def test_pipeline_bumps_atencion_to_peligro_when_escalating(tmp_path):
    db = Database(path=tmp_path / "bump.db")
    pipe = Pipeline(llm=_OfflineLLM(), escalation=EscalationDetector(db))
    s = "demo-session"

    # Step 1 — SEGURO baseline.
    r1 = pipe.classify("hola que onda", session_id=s)
    assert r1["risk_level"] == "SEGURO"
    assert r1["escalation_override"] is False

    # Step 2 — captación (ATENCION via single-phase floor).
    r2 = pipe.classify(
        "yo quiero jale, te pago el viaje, $15,000 semanales", session_id=s
    )
    assert r2["risk_level"] == "ATENCION"

    # Step 3 — enganche (still ATENCION but escalation should fire).
    r3 = pipe.classify(
        "pasate a telegram, en que colonia vives, no le digas a nadie",
        session_id=s,
    )
    # Trajectory bump: ATENCION → PELIGRO via escalation_override.
    assert r3["risk_level"] == "PELIGRO"
    assert r3["escalation_override"] is True
    assert r3["escalation"]["alert_escalation"] is True
    assert r3["escalation"]["phase_progression"] is True


def test_pipeline_without_session_skips_escalation():
    h = HeuristicClassifier()
    pipe = Pipeline(heuristic=h, llm=_OfflineLLM())
    r = pipe.classify("yo quiero jale, $15,000 semanales")
    assert r["escalation"] is None
    assert r["escalation_override"] is False
    assert r["why"]


# ---------------- HTTP integration ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "phase4.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    import importlib

    import database.db as db_module
    import main as main_module
    import webhooks as wh_module

    importlib.reload(wh_module)
    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_alert_response_includes_why_and_escalation(tmp_path):
    with _client(tmp_path) as c:
        # First alert with a session_id seeds the history.
        r1 = c.post(
            "/alert",
            json={
                "text": "yo quiero jale, te pago el viaje",
                "session_id": "u1",
            },
        ).json()
        assert "why" in r1
        assert isinstance(r1["why"], list)
        assert "escalation" in r1

        # Second alert escalates → escalation reports increasing.
        r2 = c.post(
            "/alert",
            json={
                "text": "pasate a telegram en que colonia vives",
                "session_id": "u1",
            },
        ).json()
        assert r2["escalation"] is not None
        assert r2["escalation"]["history_length"] == 2


def test_profile_endpoint_no_data(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/profile/unknown")
        assert r.status_code == 200
        assert r.json()["status"] == "no_data"


def test_profile_endpoint_after_two_alerts(tmp_path):
    with _client(tmp_path) as c:
        c.post("/alert", json={"text": "yo quiero jale", "session_id": "u9"})
        c.post(
            "/alert",
            json={
                "text": "pasate a telegram en que colonia vives",
                "session_id": "u9",
            },
        )
        body = c.get("/profile/u9").json()
        assert body["status"] == "ok"
        assert body["total_analyses"] == 2
        assert body["risk_profile"]["dominant_phase"] in {"captacion", "enganche"}
        assert len(body["risk_profile"]["score_timeline"]) == 2


def test_risk_history_get_and_delete(tmp_path):
    with _client(tmp_path) as c:
        c.post("/alert", json={"text": "yo quiero jale", "session_id": "u3"})
        rows = c.get("/risk-history/u3").json()
        assert len(rows) == 1
        d = c.delete("/risk-history/u3")
        assert d.status_code == 204
        assert c.get("/risk-history/u3").json() == []


def test_risk_history_validates_limit(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/risk-history/u3?limit=0")
        assert r.status_code == 400


def test_alert_response_legal_still_present(tmp_path):
    """Phase 3+4 should not break Phase 4 legal block."""
    with _client(tmp_path) as c:
        r = c.post(
            "/alert",
            json={"text": "te voy a matar", "session_id": "u5"},
        ).json()
        assert "legal" in r
        assert r["legal"]["urgency"] == "inmediata"
        assert r["why"]


# ---------------- /alerts/{id}/why endpoint ----------------


def test_alert_why_endpoint_recovers_specific_explanations(tmp_path):
    with _client(tmp_path) as c:
        aid = c.post(
            "/alert",
            json={"text": "yo quiero jale, te pago el viaje, $15,000 semanales 🍕"},
        ).json()["id"]
        r = c.get(f"/alerts/{aid}/why")
        body = r.json()
        assert r.status_code == 200
        assert body["alert_id"] == aid
        # Per-pattern explanations should surface concrete language now.
        joined = " ".join(body["why"]).lower()
        assert "narco" in joined or "jerga" in joined
        assert "captación" in joined.lower() or "captacion" in joined.lower()
        assert len(body["pattern_ids"]) > 0


def test_alert_why_endpoint_404_for_missing_alert(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/alerts/99999/why")
        assert r.status_code == 404


def test_explanations_from_ids_returns_specific_text():
    from classifier.heuristic import HeuristicClassifier

    h = HeuristicClassifier()
    # Real-dataset id for "te voy a matar" (Marco's manifest, Apr 2026).
    explanations = h.explanations_from_ids(["f3_001"])
    assert len(explanations) == 1
    assert "amenaza" in explanations[0]["what"]
    assert explanations[0]["type"] == "Coerción"
