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


_CHAT_ABBREVIATIONS = [
    # word-boundary aware → won't munge "que" → "que" or "para" → "p ara"
    (r"\bxq\b", "porque"),
    (r"\bpq\b", "porque"),
    (r"\bxk\b", "porque"),
    (r"\bx\b", "por"),
    (r"\bq\b", "que"),
    (r"\bk\b", "que"),
    (r"\bd\b", "de"),
    (r"\bpa\b", "para"),
    (r"\bpa'", "para"),
    (r"\bpal\b", "para el"),
    (r"\btoy\b", "estoy"),
    (r"\btoi\b", "estoy"),
    (r"\btmb\b", "tambien"),
    (r"\btb\b", "tambien"),
    (r"\bbn\b", "bien"),
    (r"\bps\b", "pues"),
    (r"\bpz\b", "pues"),
    (r"\bwey\b", "guey"),
    (r"\bwe\b", "guey"),
    (r"\bnmms\b", "no mames"),
    (r"\bvrdd\b", "verdad"),
    (r"\bvdd\b", "verdad"),
    (r"\bplis\b", "porfavor"),
    (r"\bxfa\b", "porfavor"),
    (r"\bxfis\b", "porfavor"),
]

# Spanish-written numbers → digit form. Order matters: longer first so
# "quince mil" doesn't get partially replaced by "quince". CRITICAL: do
# NOT include bare "mil" here — it would clobber "15 mil" → "15 1000"
# before the digit-based regex can produce "15000". Bare "mil" is handled
# by the regex below.
_NUMBER_WORDS = [
    ("un millon", "1000000"), ("medio millon", "500000"),
    ("cien mil", "100000"), ("cincuenta mil", "50000"),
    ("treinta mil", "30000"), ("veinticinco mil", "25000"),
    ("veinte mil", "20000"), ("quince mil", "15000"),
    ("diez mil", "10000"), ("ocho mil", "8000"),
    ("cinco mil", "5000"), ("cuatro mil", "4000"),
    ("tres mil", "3000"), ("dos mil", "2000"),
    ("mil quinientos", "1500"),
]

# Common typos that bypass detection. Real-world chat data from Marco's
# field testing. The fix-list is small and high-confidence — no risk of
# turning unrelated words into pattern hits.
_TYPO_FIXES = [
    ("ofresieron", "ofrecieron"),
    ("ofresio",    "ofrecio"),
    ("ofrese",     "ofrece"),
    ("amenasaron", "amenazaron"),
    ("amenasa",    "amenaza"),
    ("amenasar",   "amenazar"),
    ("travajo",    "trabajo"),
    ("travajar",   "trabajar"),
    ("matarme",    "matarme"),  # noop, just here for visibility
    ("dinero fasil", "dinero facil"),
    ("rrancho", "rancho"),
    ("desidir", "decidir"),
]


def _strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize(text: str) -> str:
    """Advanced normalization for Mexican-Spanish chat input.

    Steps (each idempotent):
    1. Lowercase + strip diacritics (diacritic-insensitive matching).
    2. Expand chat abbreviations (x→por, q→que, pa→para, toy→estoy…).
    3. Spanish-written numbers → digits ("quince mil" → "15000").
    4. Money formats — strip commas/dots in 4+ digit groups
       ("15,000" → "15000", "$15.000" → "$15000"); collapse "N mil" with
       digits ("15 mil" → "15000").
    5. Common typos → canonical (ofresieron → ofrecieron).
    6. Collapse whitespace.

    Designed so the same regex pattern fires on both the dataset's
    canonical form ("me ofrecieron 15000 a la semana") AND the way users
    actually type it ("me ofresieron 15 mil x semana").
    """
    text = text.lower()
    text = _strip_diacritics(text)

    # Step 2 — chat abbrevs.
    for pat, rep in _CHAT_ABBREVIATIONS:
        text = re.sub(pat, rep, text)

    # Step 3 — written numbers (longest first via list ordering above).
    for word, num in _NUMBER_WORDS:
        text = text.replace(word, num)

    # Step 4 — money normalisation.
    # "15 mil" / "15mil" → "15000". Captures bare digits or "N mil pesos".
    text = re.sub(
        r"(\d+)\s*mil(?=\s|$|[,.])",
        lambda m: str(int(m.group(1)) * 1000),
        text,
    )
    # "$15,000" → "$15000" (and "15.000" → "15000" Euro-style).
    text = re.sub(r"(\d{1,3})[,\.](\d{3}\b)", r"\1\2", text)

    # Step 5 — typo fixes.
    for typo, fix in _TYPO_FIXES:
        text = text.replace(typo, fix)

    # Step 6 — collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


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
            self._compile_patterns_into(phase_key, data.get("patterns", []))
            self._whitelists[phase_key] = [
                re.compile(re.escape(_normalize(w)), re.IGNORECASE)
                for w in data.get("whitelist", [])
            ]

            # Optional sibling: phaseN_research.json — generated by
            # scripts/etl_dataset_to_keywords.py from Marco's CSV. Adds
            # high-confidence research patterns without touching the
            # hand-curated main file. Whitelist stays only in the main.
            research_path = self.keywords_dir / f"{phase_key}_research.json"
            if research_path.exists():
                with research_path.open(encoding="utf-8") as f:
                    research = json.load(f)
                self._compile_patterns_into(phase_key, research.get("patterns", []))

        emojis_path = self.keywords_dir / "emojis_narco.json"
        with emojis_path.open(encoding="utf-8") as f:
            self._emojis = json.load(f).get("emojis", [])
        # Emoji pattern ids: stable hash of the emoji codepoint.
        for idx, e in enumerate(self._emojis):
            self._emoji_ids[e["emoji"]] = e.get("id") or f"emoji.{idx:03d}"

    def _compile_patterns_into(
        self, phase_key: str, patterns: list[dict[str, Any]]
    ) -> None:
        """Compile a list of pattern dicts and append them to the per-phase
        bucket. Shared by the main file and the optional `_research.json`
        sibling so both paths stay in lock-step.
        """
        existing_count = len(self._compiled_patterns[phase_key])
        seen_ids: set[str] = {p[3] for p in self._compiled_patterns[phase_key]}
        for idx, p in enumerate(patterns):
            raw_pattern = p["pattern"]
            is_regex = bool(p.get("regex", False))
            pattern = raw_pattern if is_regex else re.escape(raw_pattern)
            # Both regex and literal patterns are diacritic-stripped so they
            # match the normalized input. Stripping accents inside character
            # classes (e.g. d(o|ó)nde → d(o|o)nde) is a match-wise no-op.
            pattern = _normalize(pattern)
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
            except re.error:
                # Bad regex from the research dataset shouldn't crash boot.
                continue
            # Stable pattern id: use explicit id if provided, otherwise
            # synthesize from phase + offset. Used for anonymous
            # contributions and the panel's ¿Por qué? recompute path.
            pattern_id = (
                p.get("id")
                or f"{phase_key}.{(existing_count + idx):03d}"
            )
            # Research file may overlap with main; skip duplicates so we
            # don't double-count pattern fires.
            if pattern_id in seen_ids:
                continue
            seen_ids.add(pattern_id)
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
