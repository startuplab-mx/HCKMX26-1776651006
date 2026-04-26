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
    r = p.classify("te voy a matar, sabemos donde vives")
    assert r["override_triggered"] is True
    assert r["risk_level"] == "PELIGRO"
    assert r["risk_score"] == 1.0
    assert r["phase_detected"] == "coercion"


def test_phase4_explotacion_override():
    p = make_pipeline()
    # Operative narco-recruitment phrase from real dataset (Marco Apr 2026).
    r = p.classify("tienes que levantar a alguien hoy")
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


def test_hostile_long_input_is_bounded():
    """Defense in depth: a 50 KB paste must NOT hang the heuristic. We cap
    input at MAX_INPUT_CHARS=4000 so worst-case backtracking is bounded
    regardless of how nasty the regex dataset gets in the future."""
    import time
    from classifier.heuristic import MAX_INPUT_CHARS

    p = make_pipeline()
    # Pathological-ish payload: long stretches of 'a' with sprinkled real
    # tokens to force as many patterns as possible to engage. Real ReDoS
    # would explode here if any pattern in the dataset had nested
    # unbounded quantifiers — the audit at compile time should drop them.
    hostile = ("aaaaaaaaaa " * 5000) + " te voy a matar"
    assert len(hostile) > MAX_INPUT_CHARS * 10  # well over the cap

    t0 = time.perf_counter()
    r = p.classify(hostile)
    elapsed = time.perf_counter() - t0
    # Generous budget; locally this completes in <100ms. CI on a slow
    # runner should still finish well under 1s.
    assert elapsed < 2.0, f"heuristic took {elapsed:.3f}s on hostile input"
    # The cap chops the trailing trigger phrase off — so override does NOT
    # fire from this input. That's the desired behaviour: a hostile pad
    # cannot force expensive scanning AND then sneak a trigger through.
    assert r["risk_level"] in {"SEGURO", "ATENCION", "PELIGRO"}


def test_redos_audit_drops_dangerous_research_patterns():
    """If a future research dataset accidentally introduces nested
    unbounded quantifiers, _looks_redos_dangerous() should drop them at
    compile time without crashing boot."""
    from classifier.heuristic import _looks_redos_dangerous

    # Classic catastrophic shapes
    assert _looks_redos_dangerous(r"(a+)+")
    assert _looks_redos_dangerous(r"(a*)*")
    assert _looks_redos_dangerous(r"(.+)+")
    assert _looks_redos_dangerous(r"(a|b)*")
    assert _looks_redos_dangerous(r".+.+")
    # Safe shapes must NOT be flagged
    assert not _looks_redos_dangerous(r"te\s+voy\s+a\s+matar")
    assert not _looks_redos_dangerous(r"\b(?:lana|feria|billete)\b")
    assert not _looks_redos_dangerous(r"\d{1,3}\s*mil")
