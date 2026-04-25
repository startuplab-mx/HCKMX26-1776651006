"""
Risk-escalation detector.

Catches the case where individual messages each land in ATENCION but the
overall trajectory is climbing toward PELIGRO. Uses the per-session
risk_history table written on every analysis.

Operates as a pure helper — the pipeline calls
`detector.analyze_escalation(...)` after the heuristic+LLM produce a
risk_score, and consumes the returned dict to optionally bump the
risk_level. The detector itself never mutates the pipeline result.
"""
from __future__ import annotations

from typing import Any

# Numeric ordering so we can detect "captacion → enganche → coercion"
# even if intermediate steps are missing.
PHASE_ORDER: dict[str, int] = {
    "captacion": 1,
    "enganche": 2,
    "coercion": 3,
    "explotacion": 4,
}


class EscalationDetector:
    MIN_HISTORY = 2          # need 2 prior points to compute a trend
    ESCALATION_THRESHOLD = 0.15  # avg per-step delta that qualifies as escalating
    RAPID_ESCALATION = 0.30  # one-step delta that we surface as "rapid"

    def __init__(self, db) -> None:
        self.db = db

    def analyze_escalation(
        self,
        session_id: str,
        current_score: float,
        current_level: str,
        current_phase: str | None,
        source_type: str = "text",
    ) -> dict[str, Any]:
        """Persist the current point and return a trend report.

        Always writes a row to risk_history first so the demo's chart and
        the /profile endpoint stay consistent. The returned dict is
        JSON-serializable for direct inclusion in the API response.
        """
        self.db.save_risk_history(
            session_id=session_id,
            risk_score=current_score,
            risk_level=current_level,
            phase_detected=current_phase,
            source_type=source_type,
        )
        history = self.db.get_risk_history(session_id)
        if len(history) < self.MIN_HISTORY:
            return {
                "trend": "insufficient_data",
                "velocity": 0.0,
                "phase_progression": False,
                "alert_escalation": False,
                "rapid": False,
                "history_length": len(history),
                "score_history": [h["risk_score"] for h in history],
                "phase_history": [h["phase_detected"] for h in history],
                "description": None,
            }

        scores = [h["risk_score"] for h in history]
        phases = [h["phase_detected"] for h in history]
        diffs = [scores[i + 1] - scores[i] for i in range(len(scores) - 1)]
        avg_diff = sum(diffs) / len(diffs)
        last_diff = diffs[-1]

        if avg_diff > 0.05:
            trend = "increasing"
        elif avg_diff < -0.05:
            trend = "decreasing"
        else:
            trend = "stable"

        phase_prog = self._detect_phase_progression(phases)
        rapid = last_diff >= self.RAPID_ESCALATION

        alert_escalation = trend == "increasing" and (
            avg_diff >= self.ESCALATION_THRESHOLD or phase_prog or rapid
        )

        return {
            "trend": trend,
            "velocity": round(avg_diff, 3),
            "phase_progression": phase_prog,
            "alert_escalation": alert_escalation,
            "rapid": rapid,
            "history_length": len(history),
            "score_history": [round(s, 3) for s in scores[-5:]],
            "phase_history": [p for p in phases[-5:]],
            "description": self._describe(trend, avg_diff, phase_prog, rapid, len(scores)),
        }

    @staticmethod
    def _detect_phase_progression(phases: list[str | None]) -> bool:
        ranks = [PHASE_ORDER.get(p or "", 0) for p in phases]
        ranks = [r for r in ranks if r > 0]
        if len(ranks) < 2:
            return False
        # Strictly later rank than the first observed — covers skips like
        # captacion → coercion (very common in real recruitment).
        return ranks[-1] > ranks[0]

    @staticmethod
    def _describe(
        trend: str,
        velocity: float,
        phase_prog: bool,
        rapid: bool,
        n: int,
    ) -> str | None:
        if trend != "increasing":
            return None
        bits = [f"el riesgo aumentó en los últimos {n} análisis"]
        if rapid:
            bits.append("con un salto rápido en el último paso")
        elif velocity >= 0.15:
            bits.append(f"a un ritmo de +{velocity * 100:.0f}% por mensaje")
        if phase_prog:
            bits.append("y las fases de reclutamiento están progresando")
        return "; ".join(bits) + "."
