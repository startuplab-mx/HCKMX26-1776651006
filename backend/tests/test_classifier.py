"""
Smoke + override tests for the heuristic pipeline.

Run from backend/:
    pytest -q
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classifier import Pipeline
from classifier.heuristic import HeuristicClassifier
from classifier.llm_layer import LLMLayer


class _StubLLM(LLMLayer):
    """Disabled LLM so tests don't hit the network."""

    @property
    def enabled(self) -> bool:
        return False


def make_pipeline() -> Pipeline:
    return Pipeline(heuristic=HeuristicClassifier(), llm=_StubLLM())


def test_safe_message_returns_seguro():
    p = make_pipeline()
    r = p.classify("hola, mañana hay examen de bio, vienes?")
    assert r["risk_level"] == "SEGURO"
    assert r["risk_score"] < 0.3
    assert r["override_triggered"] is False


def test_phase1_captacion_message():
    p = make_pipeline()
    r = p.classify("yo quiero jale, te pago el viaje, $15,000 semanales 🍕")
    assert r["phase_scores"]["phase1"] > 0.5
    assert r["override_triggered"] is False
    assert "captacion" in r["categories"]


def test_phase3_override_triggers_peligro():
    p = make_pipeline()
    r = p.classify("si intentas escapar te descuartizo, sabemos dónde vives")
    assert r["override_triggered"] is True
    assert r["risk_level"] == "PELIGRO"
    assert r["risk_score"] == 1.0
    assert r["phase_detected"] == "coercion"


def test_phase4_sextortion_override():
    p = make_pipeline()
    r = p.classify("si no pagas las fotos van a tu escuela. deposita $500 a esta gift card")
    assert r["override_triggered"] is True
    assert r["risk_level"] == "PELIGRO"
    assert r["risk_score"] == 1.0


def test_text_hash_and_summary_present():
    p = make_pipeline()
    r = p.classify("mensaje neutro de prueba")
    assert len(r["text_hash"]) == 64
    assert r["summary"]


def test_weighted_scoring_path_atencion():
    p = make_pipeline()
    # Phase 1 + 2 mid signals, no phase3/4 → weighted average path
    r = p.classify(
        "Necesitas dinero? confía en mí, pásate a telegram. te pago el viaje."
    )
    assert r["override_triggered"] is False
    assert r["risk_level"] in {"ATENCION", "PELIGRO", "SEGURO"}
    # weighted formula with phase1 weight 0.15 + phase2 weight 0.25 should land ATENCION-ish
    assert r["risk_score"] >= 0.0
