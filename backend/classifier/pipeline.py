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

from .escalation import EscalationDetector
from .heuristic import HeuristicClassifier, PHASE_NAMES
from .llm_layer import LLMLayer
from .precision import PrecisionProcessor

OVERRIDE_THRESHOLD = float(os.getenv("OVERRIDE_THRESHOLD", "0.80"))
GREY_ZONE_MIN = float(os.getenv("LLM_GREY_ZONE_MIN", "0.3"))
GREY_ZONE_MAX = float(os.getenv("LLM_GREY_ZONE_MAX", "0.6"))

# When the escalation detector reports rapid growth or phase progression,
# bump ATENCION → PELIGRO. The hackathon UX rule: trajectory matters as
# much as any single message.
ESCALATION_LEVEL_BUMP_VELOCITY = 0.20

# Auto-tuner: how often the pipeline drains the feedback_log queue and
# applies adjustments. Inline + sync because batches are tiny (≤100 rows).
TUNING_INTERVAL = int(os.getenv("PRECISION_TUNING_INTERVAL", "10"))
LLM_DISCREPANCY_THRESHOLD = 0.30

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


def build_why(explanations: list[dict[str, str]], limit: int = 6) -> list[str]:
    """Turn the heuristic's `explanations` into short human-readable lines.

    Cap at `limit` and dedupe so the bot's WhatsApp message stays
    readable. Sorted by severity (alta first) so the most damning
    signals show up at the top.
    """
    severity_rank = {"alta": 0, "media": 1, "baja": 2}
    ordered = sorted(
        explanations, key=lambda e: severity_rank.get(e.get("severity", "baja"), 3)
    )
    why: list[str] = []
    seen: set[str] = set()
    for exp in ordered:
        line = f"Se detectó {exp['what']} (fase: {exp['type']})"
        if line not in seen:
            seen.add(line)
            why.append(line)
        if len(why) >= limit:
            break
    return why


def build_why_from_ids(heuristic, pattern_ids: list[str], limit: int = 6) -> list[str]:
    """Reconstruct the why-list from a stored alert's pattern_ids.

    Lets endpoints like /alerts/{id}/why return the same "¿Por qué?" view
    the bot rendered at analysis time, without re-classifying.
    """
    return build_why(heuristic.explanations_from_ids(pattern_ids), limit=limit)


class Pipeline:
    def __init__(
        self,
        heuristic: HeuristicClassifier | None = None,
        llm: LLMLayer | None = None,
        escalation: EscalationDetector | None = None,
        precision: PrecisionProcessor | None = None,
    ) -> None:
        self.heuristic = heuristic or HeuristicClassifier()
        self.llm = llm or LLMLayer()
        self.escalation = escalation  # set lazily by caller (needs DB)
        self.precision = precision    # set lazily by caller (needs DB)
        self._analysis_count = 0

    def classify(
        self,
        text: str,
        use_llm: bool = True,
        session_id: str | None = None,
        source_type: str = "text",
    ) -> dict[str, Any]:
        # Pass the precision processor to the heuristic so its weights
        # reflect every adjustment the auto-tuner has learned so far.
        h = self.heuristic.classify(text, weight_overrides=self.precision)
        phase_scores: dict[str, float] = h["phase_scores"]
        categories: list[str] = h["categories"]
        pattern_ids: list[str] = h.get("matched_pattern_ids", [])
        explanations: list[dict[str, str]] = h.get("explanations", [])

        if (
            phase_scores["phase3"] >= OVERRIDE_THRESHOLD
            or phase_scores["phase4"] >= OVERRIDE_THRESHOLD
        ):
            override_phase = (
                "coercion"
                if phase_scores["phase3"] >= phase_scores["phase4"]
                else "explotacion"
            )
            return self._finalize(
                risk_score=1.0,
                phase_scores=phase_scores,
                categories=categories,
                pattern_ids=pattern_ids,
                explanations=explanations,
                phase_detected=override_phase,
                override=True,
                llm_used=False,
                llm_rationale=None,
                text=text,
                session_id=session_id,
                source_type=source_type,
            )

        weighted = sum(phase_scores[k] * w for k, w in PHASE_WEIGHTS.items())
        max_phase = max(phase_scores.values()) if phase_scores else 0.0
        if max_phase >= 0.7:
            weighted = max(weighted, 0.40)
        elif max_phase >= 0.5:
            weighted = max(weighted, 0.30)
        weighted = max(0.0, min(1.0, weighted))

        # Contextual boost — multiple weak signals in different categories
        # often add up to a real threat ("incentivo + perfilamiento" =
        # offer + asking for personal info = recruitment). Without this,
        # 3 mid-weight matches (each 0.5) average down instead of up.
        weighted = self._contextual_boost(weighted, phase_scores, categories)

        llm_used = False
        llm_rationale = None
        final_score = weighted

        # ── LLM activation logic ──────────────────────────────────────
        # Three triggers (any one fires the LLM call):
        #   1. Classic grey zone (0.3 ≤ score ≤ 0.6)
        #   2. Score == 0 BUT the text is substantive (>30 chars). This
        #      catches the "Marco gap" — heuristic missed entirely but
        #      the message is suspicious in shape.
        #   3. Low score (<0.3) BUT the text contains money/work/threat
        #      vocabulary that *might* be a recruitment signal in the
        #      wrong arrangement.
        text_lower = text.lower()
        ACTIVATION_KEYWORDS = (
            "pesos", "dinero", "lana", "feria", "billete", "varos",
            "mil", "semana", "diario", "mensual", "quincenal",
            "matar", "amenaz", "morir", "miedo", "peligr", "obligar",
            "rancho", "monte", "punto", "jale", "chamba", "halcon",
            "ofrecieron", "ofrecio", "ofrecen", "pidieron", "piden",
            "dijeron", "dicen", "obligaron", "obligan", "extorsion",
            "pasame", "manda", "fotos", "nudes", "secuestr",
        )
        score_is_zero = weighted == 0
        substantive = len(text.strip()) > 30
        has_keywords = any(k in text_lower for k in ACTIVATION_KEYWORDS)
        in_grey_zone = GREY_ZONE_MIN <= weighted <= GREY_ZONE_MAX
        marco_gap = score_is_zero and substantive
        weak_keywords = weighted < GREY_ZONE_MIN and has_keywords

        if use_llm and self.llm.enabled and (
            in_grey_zone or marco_gap or weak_keywords
        ):
            llm_result = self.llm.analyze(text)
            if llm_result is not None:
                # When the heuristic gave 0 but LLM activated as a safety
                # net, trust the LLM 100% — there's nothing to merge.
                # Otherwise, average heuristic and LLM 50/50.
                if score_is_zero:
                    final_score = max(0.0, min(1.0, llm_result["risk_score"]))
                else:
                    final_score = max(
                        0.0,
                        min(1.0, (weighted + llm_result["risk_score"]) / 2),
                    )
                llm_used = True
                llm_rationale = llm_result["rationale"]
                # Auto-tuner signal: when Claude and the heuristic disagree
                # noticeably on grey-zone text, log the discrepancy so the
                # PrecisionProcessor can nudge the matched pattern weights
                # up or down depending on which side LLM landed on.
                if (
                    self.precision is not None
                    and self.escalation is not None  # implies db exists on db side
                    and abs(llm_result["risk_score"] - weighted)
                    >= LLM_DISCREPANCY_THRESHOLD
                    and pattern_ids
                ):
                    try:
                        self.escalation.db.save_feedback(
                            feedback_type="llm_discrepancy",
                            heuristic_score=round(weighted, 4),
                            llm_score=round(llm_result["risk_score"], 4),
                            final_score=round(final_score, 4),
                            pattern_ids=pattern_ids,
                            text_hash=text_hash(text),
                            session_id=session_id,
                        )
                    except Exception as e:  # noqa: BLE001 — feedback is best-effort
                        # Log so a broken auto-tuner is debuggable. Was just
                        # silently swallowed which made the precision processor
                        # impossible to diagnose in production.
                        import logging as _log
                        _log.getLogger("nahual").warning(
                            "feedback save failed: %s", e
                        )

        result = self._finalize(
            risk_score=final_score,
            phase_scores=phase_scores,
            categories=categories,
            pattern_ids=pattern_ids,
            explanations=explanations,
            phase_detected=dominant_phase(phase_scores),
            override=False,
            llm_used=llm_used,
            llm_rationale=llm_rationale,
            text=text,
            session_id=session_id,
            source_type=source_type,
        )
        self._maybe_tune()
        return result

    # ---------------- Contextual boost ----------------

    # Combos of categories that, when seen together, are MUCH more dangerous
    # than the individual scores suggest. Picked from real-world recruitment
    # patterns (Colmex, REDIM): a stranger who offers money AND asks where
    # you live is doing recruitment surveillance, even if neither signal
    # alone hits the override threshold.
    _DANGER_COMBOS: list[set[str]] = [
        {"oferta_economica", "perfilamiento"},
        {"oferta_economica", "aislamiento"},
        {"oferta_recibida",  "perfilamiento"},
        {"oferta_recibida",  "topologia_narco"},
        {"amenaza",          "orden_directa"},
        {"amenaza_recibida", "extorsion_recibida"},
        {"sextorsion_recibida", "sextorsion_chantaje"},
        {"confianza_falsa",  "perfilamiento"},
        {"jerga_dinero",     "fronts_falsos"},
        {"red_social_dm",    "oferta_economica"},
    ]

    @staticmethod
    def _contextual_boost(
        weighted: float,
        phase_scores: dict[str, float],
        categories: list[str],
    ) -> float:
        """Boost the score when multiple weak signals from DIFFERENT
        categories co-occur. Multiplier:
          * 1.30 if 3+ unique categories matched (broad surface)
          * 1.50 if any DANGER_COMBOS pair is present (specific high-risk)
        Capped at 1.0. Only applied when 0 < weighted < OVERRIDE_THRESHOLD
        (no point boosting a clean 0 or a guaranteed PELIGRO).
        """
        if not (0.0 < weighted < OVERRIDE_THRESHOLD):
            return weighted
        unique = set(categories)
        # Specific dangerous co-occurrence beats the generic count.
        for combo in Pipeline._DANGER_COMBOS:
            if combo.issubset(unique):
                return min(1.0, weighted * 1.50)
        if len(unique) >= 3:
            return min(1.0, weighted * 1.30)
        return weighted

    # ---------------- Auto-tune ----------------

    def _maybe_tune(self) -> None:
        """Run a tuning batch every TUNING_INTERVAL classifications.

        Inline + sync — feedback batches are small (≤100 rows) and the
        cost of a SELECT + a few dict updates is negligible compared to
        the rest of the analysis (regex + optional Claude call).
        """
        if self.precision is None:
            return
        self._analysis_count += 1
        if self._analysis_count % TUNING_INTERVAL == 0:
            try:
                self.precision.process_pending_feedback()
            except Exception:  # noqa: BLE001
                pass

    def _finalize(
        self,
        *,
        risk_score: float,
        phase_scores: dict[str, float],
        categories: list[str],
        pattern_ids: list[str],
        explanations: list[dict[str, str]],
        phase_detected: str,
        override: bool,
        llm_used: bool,
        llm_rationale: str | None,
        text: str,
        session_id: str | None,
        source_type: str,
    ) -> dict[str, Any]:
        risk_level = risk_level_for(risk_score)
        escalation = None
        escalation_override = False

        if session_id and self.escalation is not None:
            escalation = self.escalation.analyze_escalation(
                session_id=session_id,
                current_score=risk_score,
                current_level=risk_level,
                current_phase=phase_detected,
                source_type=source_type,
            )
            # Trajectory override: a string of ATENCION messages that's
            # rapidly climbing should escalate to PELIGRO before the user
            # gets hurt. Keep override flag separate from the static
            # phase3/phase4 override so we can label it correctly.
            # Trajectory bump only triggers with at least 2 prior deltas
            # (history_length >= 3). A single large jump from SEGURO is
            # not enough — we want evidence that risk is sustained.
            if (
                risk_level == "ATENCION"
                and escalation["alert_escalation"]
                and escalation["history_length"] >= 3
                and (
                    escalation["velocity"] >= ESCALATION_LEVEL_BUMP_VELOCITY
                    or escalation["phase_progression"]
                )
            ):
                risk_score = max(risk_score, 0.75)
                risk_level = "PELIGRO"
                escalation_override = True

        return {
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "phase_detected": phase_detected,
            "phase_scores": {k: round(v, 4) for k, v in phase_scores.items()},
            "categories": categories,
            "pattern_ids": pattern_ids,
            "explanations": explanations,
            "why": build_why(explanations),
            "override_triggered": override,
            "escalation_override": escalation_override,
            "escalation": escalation,
            "llm_used": llm_used,
            "llm_rationale": llm_rationale,
            "text_hash": text_hash(text),
            "summary": anonymized_summary(text, categories),
        }
