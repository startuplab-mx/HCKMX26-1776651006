"""
Classifier pipeline: heuristic Layer 1 → optional Claude Layer 2 → override logic.

OVERRIDE RULE (non-negotiable):
    if phase3 >= 0.80 OR phase4 >= 0.80:
        risk_score = 1.0, risk_level = "PELIGRO"

Normal weighted formula:
    risk_score = phase1*0.15 + phase2*0.25 + phase3*0.35 + phase4*0.25

Single-phase saturation floor (UX safeguard):
    When ANY individual phase score saturates, the final risk_score is
    floored so the alert is never silently downgraded:
        max_phase >= 0.7 → risk_score >= 0.40 (ATENCION)
        max_phase >= 0.5 → risk_score >= 0.30 (ATENCION)
    This preserves the spec's weighted formula in multi-phase combinations
    while preventing a single saturated phase (e.g. clear captación) from
    landing in SEGURO due to small phase weights.

Levels:
    SEGURO   [0.00, 0.30)
    ATENCION [0.30, 0.70)
    PELIGRO  [0.70, 1.00]
"""
from __future__ import annotations

import hashlib
import os
from typing import Any

from .heuristic import HeuristicClassifier, PHASE_NAMES
from .llm_layer import LLMLayer

OVERRIDE_THRESHOLD = float(os.getenv("OVERRIDE_THRESHOLD", "0.80"))
GREY_ZONE_MIN = float(os.getenv("LLM_GREY_ZONE_MIN", "0.3"))
GREY_ZONE_MAX = float(os.getenv("LLM_GREY_ZONE_MAX", "0.6"))

PHASE_WEIGHTS = {"phase1": 0.15, "phase2": 0.25, "phase3": 0.35, "phase4": 0.25}


def risk_level_for(score: float) -> str:
    if score >= 0.7:
        return "PELIGRO"
    if score >= 0.3:
        return "ATENCION"
    return "SEGURO"


def dominant_phase(phase_scores: dict[str, float]) -> str:
    if not phase_scores:
        return "ninguna"
    top = max(phase_scores.items(), key=lambda kv: kv[1])
    if top[1] <= 0:
        return "ninguna"
    return PHASE_NAMES.get(top[0], top[0])


def anonymized_summary(text: str, categories: list[str]) -> str:
    """Short anonymized summary for storage. Never persist raw text."""
    cats = ", ".join(categories[:3]) if categories else "sin categorías"
    return f"Mensaje de {len(text)} chars · señales: {cats}"


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Pipeline:
    def __init__(
        self,
        heuristic: HeuristicClassifier | None = None,
        llm: LLMLayer | None = None,
    ) -> None:
        self.heuristic = heuristic or HeuristicClassifier()
        self.llm = llm or LLMLayer()

    def classify(self, text: str, use_llm: bool = True) -> dict[str, Any]:
        h = self.heuristic.classify(text)
        phase_scores: dict[str, float] = h["phase_scores"]
        categories: list[str] = h["categories"]

        if (
            phase_scores["phase3"] >= OVERRIDE_THRESHOLD
            or phase_scores["phase4"] >= OVERRIDE_THRESHOLD
        ):
            override_phase = (
                "coercion"
                if phase_scores["phase3"] >= phase_scores["phase4"]
                else "explotacion"
            )
            return self._build_result(
                risk_score=1.0,
                phase_scores=phase_scores,
                categories=categories,
                phase_detected=override_phase,
                override=True,
                llm_used=False,
                llm_rationale=None,
                text=text,
            )

        weighted = sum(phase_scores[k] * w for k, w in PHASE_WEIGHTS.items())
        max_phase = max(phase_scores.values()) if phase_scores else 0.0
        if max_phase >= 0.7:
            weighted = max(weighted, 0.40)
        elif max_phase >= 0.5:
            weighted = max(weighted, 0.30)
        weighted = max(0.0, min(1.0, weighted))

        llm_used = False
        llm_rationale = None
        final_score = weighted

        if (
            use_llm
            and GREY_ZONE_MIN <= weighted <= GREY_ZONE_MAX
            and self.llm.enabled
        ):
            llm_result = self.llm.analyze(text)
            if llm_result is not None:
                final_score = max(0.0, min(1.0, (weighted + llm_result["risk_score"]) / 2))
                llm_used = True
                llm_rationale = llm_result["rationale"]

        return self._build_result(
            risk_score=final_score,
            phase_scores=phase_scores,
            categories=categories,
            phase_detected=dominant_phase(phase_scores),
            override=False,
            llm_used=llm_used,
            llm_rationale=llm_rationale,
            text=text,
        )

    def _build_result(
        self,
        risk_score: float,
        phase_scores: dict[str, float],
        categories: list[str],
        phase_detected: str,
        override: bool,
        llm_used: bool,
        llm_rationale: str | None,
        text: str,
    ) -> dict[str, Any]:
        return {
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level_for(risk_score),
            "phase_detected": phase_detected,
            "phase_scores": {k: round(v, 4) for k, v in phase_scores.items()},
            "categories": categories,
            "override_triggered": override,
            "llm_used": llm_used,
            "llm_rationale": llm_rationale,
            "text_hash": text_hash(text),
            "summary": anonymized_summary(text, categories),
        }
