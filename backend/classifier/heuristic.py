"""
Layer 1: Heuristic classifier.

Loads keyword JSON files for each phase + narco emojis. Computes a per-phase
score in [0.0, 1.0] using weighted matches.

Scoring per phase:
    raw_score = sum(weight) for matched patterns - sum(weight) for whitelist hits
    score = clamp(raw_score / saturation, 0.0, 1.0)

The saturation factor controls how many strong patterns are needed to reach 1.0.
With saturation=1.5 a single 1.0 pattern (like "si intentas escapar te
descuartizo") immediately saturates Phase 3.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

KEYWORDS_DIR = Path(__file__).parent / "keywords"

PHASE_FILES = {
    "phase1": "phase1_captacion.json",
    "phase2": "phase2_enganche.json",
    "phase3": "phase3_coercion.json",
    "phase4": "phase4_explotacion.json",
}

PHASE_NAMES = {
    "phase1": "captacion",
    "phase2": "enganche",
    "phase3": "coercion",
    "phase4": "explotacion",
}

# Display labels for user-facing explanations / WhatsApp messages /
# the panel "why?" view. Keep these capitalized + accented.
PHASE_DISPLAY = {
    "phase1": "Captación",
    "phase2": "Enganche",
    "phase3": "Coerción",
    "phase4": "Explotación",
}

# Saturation factor: divides accumulated weights to produce the phase score.
# At 1.0 each pattern's JSON weight maps directly to a per-phase score share, so
# a single weight=1.0 pattern (e.g. an explicit death threat) saturates the
# phase and triggers override; multi-pattern accumulation simply clamps to 1.0.
SATURATION = 1.0


# Generic, human-readable explanation per phase. Used as a fallback when a
# pattern's JSON entry doesn't carry an `explanation` field. The bot turns
# these into "Se detectó <what> (fase: <type>)" lines for the WA reply.
DEFAULT_EXPLANATIONS: dict[str, str] = {
    "captacion": "lenguaje de oferta económica o reclutamiento aspiracional",
    "enganche": "intento de aislamiento o solicitud de datos personales",
    "coercion": "lenguaje de amenaza, presión o intimidación",
    "explotacion": "instrucción operativa, sextorsión o demanda económica",
}


def _normalize(text: str) -> str:
    """Lowercase + strip diacritics for diacritic-insensitive matching."""
    text = text.lower()
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class HeuristicClassifier:
    def __init__(self, keywords_dir: Path | str = KEYWORDS_DIR) -> None:
        self.keywords_dir = Path(keywords_dir)
        self._phase_data: dict[str, dict[str, Any]] = {}
        # (compiled, weight, source, pattern_id, explanation)
        self._compiled_patterns: dict[
            str, list[tuple[re.Pattern[str], float, str, str, str]]
        ] = {}
        self._whitelists: dict[str, list[re.Pattern[str]]] = {}
        self._emojis: list[dict[str, Any]] = []
        # (emoji, weight, [phase_affinity], pattern_id)
        self._emoji_ids: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        for phase_key, fname in PHASE_FILES.items():
            path = self.keywords_dir / fname
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            self._phase_data[phase_key] = data
            self._compiled_patterns[phase_key] = []
            for idx, p in enumerate(data.get("patterns", [])):
                raw_pattern = p["pattern"]
                is_regex = bool(p.get("regex", False))
                pattern = raw_pattern if is_regex else re.escape(raw_pattern)
                # Both regex and literal patterns are diacritic-stripped so they match
                # the normalized input. Stripping accents inside character classes
                # (e.g. d(o|ó)nde → d(o|o)nde) is a no-op match-wise.
                pattern = _normalize(pattern)
                compiled = re.compile(pattern, re.IGNORECASE)
                # Stable pattern id: use explicit id if provided in JSON,
                # otherwise synthesize from phase + index. Used for anonymous
                # contributions (Phase 3) so we can aggregate which patterns
                # fire across populations without exposing message text.
                pattern_id = p.get("id") or f"{phase_key}.{idx:03d}"
                explanation = (
                    p.get("explanation")
                    or p.get("category")
                    or DEFAULT_EXPLANATIONS[PHASE_NAMES[phase_key]]
                )
                self._compiled_patterns[phase_key].append(
                    (
                        compiled,
                        float(p["weight"]),
                        p.get("source", ""),
                        pattern_id,
                        explanation,
                    )
                )
            self._whitelists[phase_key] = [
                re.compile(re.escape(_normalize(w)), re.IGNORECASE)
                for w in data.get("whitelist", [])
            ]

        emojis_path = self.keywords_dir / "emojis_narco.json"
        with emojis_path.open(encoding="utf-8") as f:
            self._emojis = json.load(f).get("emojis", [])
        # Emoji pattern ids: stable hash of the emoji codepoint.
        for idx, e in enumerate(self._emojis):
            self._emoji_ids[e["emoji"]] = e.get("id") or f"emoji.{idx:03d}"

    def _score_phase(
        self,
        phase_key: str,
        normalized: str,
        weight_overrides: Any = None,
    ) -> tuple[float, list[str], list[str], list[dict[str, str]]]:
        matched_descriptions: list[str] = []
        matched_ids: list[str] = []
        explanations: list[dict[str, str]] = []
        raw = 0.0
        max_matched_weight = 0.0
        phase_label = PHASE_DISPLAY[phase_key]
        for compiled, base_weight, source, pattern_id, exp in self._compiled_patterns[
            phase_key
        ]:
            if compiled.search(normalized):
                # Auto-tuner overlay: ask the precision processor for the
                # adjusted weight. Falls back to base when no overrides.
                if weight_overrides is not None and hasattr(
                    weight_overrides, "get_adjusted_weight"
                ):
                    weight = weight_overrides.get_adjusted_weight(
                        pattern_id, base_weight
                    )
                else:
                    weight = base_weight
                raw += weight
                max_matched_weight = max(max_matched_weight, weight)
                matched_descriptions.append(f"{compiled.pattern} ({source})")
                matched_ids.append(pattern_id)
                # Severity is a UX cue, computed from the *adjusted* weight
                # so the user-facing "alta/media/baja" reflects what the
                # tuner has learned about each pattern.
                severity = (
                    "alta" if weight >= 0.7 else "media" if weight >= 0.4 else "baja"
                )
                explanations.append(
                    {"type": phase_label, "what": exp, "severity": severity}
                )
        # Whitelist penalty is proportional to matched signal: a benign-but-similar
        # phrase shouldn't wipe out a strong threat signal, but should neutralize
        # weak signals (low matched weights).
        for wl in self._whitelists[phase_key]:
            if wl.search(normalized):
                raw -= min(0.5, max_matched_weight * 0.6 + 0.1)
        score = max(0.0, min(1.0, raw / SATURATION))
        return score, matched_descriptions, matched_ids, explanations

    def _score_emojis(
        self, raw_text: str
    ) -> tuple[dict[str, float], list[str], list[str], list[dict[str, str]]]:
        boosts = {"phase1": 0.0, "phase2": 0.0, "phase3": 0.0, "phase4": 0.0}
        categories: list[str] = []
        ids: list[str] = []
        explanations: list[dict[str, str]] = []
        for e in self._emojis:
            if e["emoji"] in raw_text:
                weight = float(e["weight"])
                for affinity in e.get("phase_affinity", []):
                    phase_key = next(
                        (k for k, v in PHASE_NAMES.items() if v == affinity), None
                    )
                    if phase_key:
                        boosts[phase_key] += weight * 0.4
                slug = _normalize(e["meaning"].split("(")[0]).strip().lower()
                slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
                categories.append(f"narco_emoji_{slug}")
                ids.append(self._emoji_ids[e["emoji"]])
                severity = (
                    "alta" if weight >= 0.7 else "media" if weight >= 0.4 else "baja"
                )
                explanations.append(
                    {
                        "type": "Narcocultura",
                        "what": f"emoji asociado a {e['meaning']}",
                        "severity": severity,
                    }
                )
        return boosts, categories, ids, explanations

    def classify(
        self, text: str, weight_overrides: Any = None
    ) -> dict[str, Any]:
        normalized = _normalize(text)
        per_phase: dict[str, float] = {}
        matched_per_phase: dict[str, list[str]] = {}
        ids_per_phase: dict[str, list[str]] = {}
        all_explanations: list[dict[str, str]] = []

        for phase_key in PHASE_FILES:
            score, matched, ids, explanations = self._score_phase(
                phase_key, normalized, weight_overrides=weight_overrides
            )
            per_phase[phase_key] = score
            matched_per_phase[phase_key] = matched
            ids_per_phase[phase_key] = ids
            all_explanations.extend(explanations)

        emoji_boosts, emoji_categories, emoji_ids, emoji_explanations = (
            self._score_emojis(text)
        )
        for k, boost in emoji_boosts.items():
            per_phase[k] = max(0.0, min(1.0, per_phase[k] + boost))
        all_explanations.extend(emoji_explanations)

        categories: list[str] = []
        for phase_key, matched in matched_per_phase.items():
            if matched:
                categories.append(PHASE_NAMES[phase_key])
        categories.extend(emoji_categories)

        # Flat list of all matched pattern IDs across phases + emojis. Stable
        # across reorderings as long as patterns keep their position in the
        # JSON (we synthesize ids by index when none is provided).
        matched_pattern_ids: list[str] = []
        for ids in ids_per_phase.values():
            matched_pattern_ids.extend(ids)
        matched_pattern_ids.extend(emoji_ids)

        return {
            "phase_scores": per_phase,
            "matched_patterns": matched_per_phase,
            "matched_pattern_ids": matched_pattern_ids,
            "categories": list(dict.fromkeys(categories)),
            "emoji_boosts": emoji_boosts,
            "explanations": all_explanations,
        }

    def explanations_from_ids(
        self, pattern_ids: list[str]
    ) -> list[dict[str, str]]:
        """Reconstruct user-facing `explanations` for a stored alert.

        Used by GET /alerts/{id}/why so the panel can render the same
        "¿Por qué?" view that the bot saw at analysis time, without
        having to re-classify (we never persist the original text).
        """
        target = set(pattern_ids or [])
        if not target:
            return []
        out: list[dict[str, str]] = []
        for phase_key, patterns in self._compiled_patterns.items():
            phase_label = PHASE_DISPLAY[phase_key]
            for _compiled, weight, _source, pid, exp in patterns:
                if pid in target:
                    severity = (
                        "alta"
                        if weight >= 0.7
                        else "media"
                        if weight >= 0.4
                        else "baja"
                    )
                    out.append(
                        {"type": phase_label, "what": exp, "severity": severity}
                    )
        # Emojis stored by id → meaning lookup
        emoji_by_id = {pid: e for e, pid in zip(self._emojis, self._emoji_ids.values())}
        for pid, e in emoji_by_id.items():
            if pid in target:
                weight = float(e["weight"])
                severity = (
                    "alta" if weight >= 0.7 else "media" if weight >= 0.4 else "baja"
                )
                out.append(
                    {
                        "type": "Narcocultura",
                        "what": f"emoji asociado a {e['meaning']}",
                        "severity": severity,
                    }
                )
        return out
