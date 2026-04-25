"""
Precision Processor — Auto-Tuning Engine.

Reads `feedback_log` rows in batches, applies per-pattern weight
adjustments in memory, and exposes a `get_adjusted_weight()` lookup the
heuristic uses at scoring time. Never mutates the keyword JSONs — the
overlay lives in process memory and survives via export/import endpoints.

Three feedback sources fund the tuner:

    1. confirm  — implicit signal from the bot flow (user provided the
                  guardian phone after PELIGRO, i.e. acted on the alert)
    2. deny     — implicit signal (user explicitly contradicted the
                  alert)
    3. llm_discrepancy — pipeline observed a >0.3 gap between the
                  heuristic and the Claude API score; the side LLM landed
                  on dictates the nudge direction
    4. operator_fp / operator_fn — explicit panel-level corrections
                  with twice the magnitude of implicit signals

Hard caps protect the system:
    MAX_ADJUSTMENT = 0.20  → any single pattern can move at most ±0.20
    weight clamp   [0.05, 1.0]  → never wipe a pattern out, never run away
"""
from __future__ import annotations

import logging
from collections import defaultdict
from threading import RLock
from typing import Any

logger = logging.getLogger(__name__)


class PrecisionProcessor:
    MIN_FEEDBACK_TO_PROCESS = 5
    MAX_ADJUSTMENT = 0.20
    LLM_DISCREPANCY_THRESHOLD = 0.30

    NUDGE = {
        "confirm": +0.02,
        "deny": -0.05,
        "operator_fp": -0.08,
        "operator_fn": +0.08,
    }

    def __init__(self, db: Any) -> None:
        self.db = db
        self._lock = RLock()
        self.weight_adjustments: dict[str, float] = {}
        # confirmations / denials / llm_overrides / precision_score
        self.pattern_stats: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "confirmations": 0,
                "denials": 0,
                "llm_overrides": 0,
                "precision_score": 1.0,
            }
        )

    # ---------------- Hot path: weight lookup ----------------

    def get_adjusted_weight(self, pattern_id: str, base_weight: float) -> float:
        """Return the runtime-adjusted weight for a pattern. Hot path —
        called from the heuristic on every match. Read-only and lock-free
        on Python's GIL-protected dict reads.
        """
        delta = self.weight_adjustments.get(pattern_id, 0.0)
        return max(0.05, min(base_weight + delta, 1.0))

    # ---------------- Cold path: feedback processing ----------------

    def process_pending_feedback(self) -> dict[str, Any]:
        """Drain the feedback_log queue, apply nudges, mark processed.

        Returns a small report so the caller can log it. Safe to call
        from multiple threads (RLock around adjustments).
        """
        batch = self.db.get_unprocessed_feedback(limit=100)
        if len(batch) < self.MIN_FEEDBACK_TO_PROCESS:
            return {
                "processed": 0,
                "patterns_affected": 0,
                "reason": "insufficient_feedback",
                "pending_count": len(batch),
            }

        adjustments_made: dict[str, float] = {}
        with self._lock:
            for fb in batch:
                pattern_ids = fb.get("pattern_ids") or []
                fb_type = fb["feedback_type"]
                for pid in pattern_ids:
                    stats = self.pattern_stats[pid]
                    if fb_type == "confirm":
                        stats["confirmations"] += 1
                        self._nudge(pid, self.NUDGE["confirm"])
                    elif fb_type == "deny":
                        stats["denials"] += 1
                        self._nudge(pid, self.NUDGE["deny"])
                    elif fb_type == "operator_fp":
                        stats["denials"] += 2
                        self._nudge(pid, self.NUDGE["operator_fp"])
                    elif fb_type == "operator_fn":
                        stats["confirmations"] += 2
                        self._nudge(pid, self.NUDGE["operator_fn"])
                    elif fb_type == "llm_discrepancy":
                        stats["llm_overrides"] += 1
                        h = fb.get("heuristic_score") or 0.0
                        l = fb.get("llm_score") or 0.0
                        # LLM said less risk → heuristic over-fires here → pull weight down.
                        # LLM said more risk → heuristic under-fires → pull weight up.
                        self._nudge(pid, -0.03 if l < h else +0.03)

                    total = stats["confirmations"] + stats["denials"]
                    if total > 0:
                        stats["precision_score"] = stats["confirmations"] / total
                    if pid in self.weight_adjustments:
                        adjustments_made[pid] = self.weight_adjustments[pid]

            self.db.mark_feedback_processed([fb["id"] for fb in batch])

        if adjustments_made:
            logger.info(
                "[precision] processed=%d patterns_affected=%d",
                len(batch),
                len(adjustments_made),
            )
        return {
            "processed": len(batch),
            "patterns_affected": len(adjustments_made),
            "adjustments": {k: round(v, 3) for k, v in adjustments_made.items()},
        }

    def _nudge(self, pattern_id: str, delta: float) -> None:
        new = self.weight_adjustments.get(pattern_id, 0.0) + delta
        self.weight_adjustments[pattern_id] = max(
            -self.MAX_ADJUSTMENT, min(new, self.MAX_ADJUSTMENT)
        )

    # ---------------- Diagnostics ----------------

    def get_diagnostics(self) -> dict[str, Any]:
        """Snapshot for /precision/diagnostics."""
        problematic = {}
        for pid, stats in self.pattern_stats.items():
            total = stats["confirmations"] + stats["denials"]
            if stats["precision_score"] < 0.7 and total >= 3:
                problematic[pid] = {
                    "precision": round(stats["precision_score"], 2),
                    "confirmations": stats["confirmations"],
                    "denials": stats["denials"],
                    "current_adjustment": round(
                        self.weight_adjustments.get(pid, 0.0), 3
                    ),
                }
        active = {
            pid: round(d, 3)
            for pid, d in self.weight_adjustments.items()
            if abs(d) > 0.01
        }
        return {
            "total_patterns_tracked": len(self.pattern_stats),
            "total_adjustments_active": len(active),
            "weight_adjustments": active,
            "problematic_patterns": problematic,
        }

    # ---------------- Persistence (optional) ----------------

    def export_state(self) -> dict[str, Any]:
        with self._lock:
            return {
                "adjustments": dict(self.weight_adjustments),
                "stats": {
                    pid: dict(stats) for pid, stats in self.pattern_stats.items()
                },
            }

    def import_state(self, data: dict[str, Any]) -> None:
        with self._lock:
            self.weight_adjustments = dict(data.get("adjustments", {}))
            for pid, stats in (data.get("stats") or {}).items():
                self.pattern_stats[pid].update(stats)
