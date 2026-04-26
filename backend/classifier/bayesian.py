"""
backend/classifier/bayesian.py

Clasificador Bayesiano Naive (Capa 1.5) para detección de reclutamiento.

Diseño:
- 0 dependencias nuevas (Python stdlib puro)
- Entrenamiento incremental (cada feedback confirma/niega → train_one)
- N-gramas (1,2,3) como features (en lugar de bag-of-words)
- Smoothing de Laplace para evitar probabilidad 0
- Persistencia atómica en JSON
- Auto-save cada 10 entrenamientos
- Mapeo a risk_score 0-1 ponderando 5 clases (seguro / 4 fases)

NO reemplaza al heurístico ni al LLM — los complementa.
Si el modelo tiene < 5 ejemplos, retorna `insufficient_data: true` y
el pipeline cae al merge sin esta capa.
"""
from __future__ import annotations

import json
import math
import os
import re
import threading
import unicodedata
from collections import defaultdict
from pathlib import Path

# 5-class taxonomy: 4 fases del reclutamiento + clase neutra "seguro".
CLASSES = ("seguro", "captacion", "enganche", "coercion", "explotacion")

# Risk-score mapping per class. Pondera la probabilidad de cada clase
# para producir un único score 0-1 comparable con el heurístico/LLM.
_RISK_MAP = {
    "seguro":      0.0,
    "captacion":   0.3,
    "enganche":    0.5,
    "coercion":    0.8,
    "explotacion": 0.9,
}

def _resolve_default_model_path() -> Path:
    """Path of the persisted JSON model.

    Override at deploy/test time via the `BAYESIAN_MODEL_PATH` env var so
    pytest can isolate per-test models in tmp directories without
    poisoning the production-bootstrapped file.
    """
    env_path = os.getenv("BAYESIAN_MODEL_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent / "bayesian_model.json"


_DEFAULT_MODEL_PATH = _resolve_default_model_path()

# Mínimo de docs antes de que predict() devuelva algo útil.
_MIN_DOCS_FOR_PREDICTION = 5
# Auto-save cada N entrenamientos.
_AUTOSAVE_EVERY = 10
# Frecuencia mínima para que un feature aparezca en top_features (evita ruido).
_TOP_FEATURE_MIN_COUNT = 2
# Hard cap on tokens emitted per call to _tokenize. A 1 MB pasted file
# would otherwise produce ~3 million n-grams and OOM the worker. WhatsApp
# messages cap at ~4 KB / ~700 tokens; legitimate research-paper paragraphs
# stay under 2k tokens. We round up generously.
_MAX_TOKENS_PER_DOC = 5000


def _normalize(text: str) -> str:
    """Lowercase + strip diacritics + alphanum-only.

    Distinto del normalizador del heurístico (que expande abreviaciones de
    chat MX) — aquí queremos features simples y estables. Lo que importa
    es que el bootstrap y el predict usen exactamente la misma función.
    """
    text = (text or "").lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Conserva ñ y ü explícitamente; reemplaza el resto no-alfanumérico por espacio.
    text = re.sub(r"[^\w\sñü]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class NaiveBayesClassifier:
    """Naive Bayes con smoothing de Laplace y n-gramas (1,2,3)."""

    SMOOTHING = 1.0

    def __init__(self, model_path: str | Path | None = None) -> None:
        # Re-resolve at call time so a test that sets BAYESIAN_MODEL_PATH
        # after import still gets the new path. (Module-level constant
        # was captured at import time, before the test could override.)
        self.model_path = Path(model_path or _resolve_default_model_path())
        # class → {feature: count}
        self.feature_counts: dict[str, dict[str, int]] = {
            c: defaultdict(int) for c in CLASSES
        }
        # class → total docs trained as that class
        self.class_counts: dict[str, int] = {c: 0 for c in CLASSES}
        # Total docs (sum of class_counts)
        self.total_docs: int = 0
        # Vocab union of all classes (deduped)
        self.vocab: set[str] = set()
        # Mutex for concurrent trains/predicts (FastAPI runs in threadpool).
        self._lock = threading.RLock()
        self._load()

    # -------- Public API --------

    def train_one(self, text: str, label: str) -> bool:
        """Update counters with one labeled document. Returns True on success."""
        if label not in CLASSES:
            return False
        features = self._tokenize(text)
        if not features:
            return False
        with self._lock:
            self.class_counts[label] += 1
            self.total_docs += 1
            for f in features:
                self.feature_counts[label][f] += 1
                self.vocab.add(f)
            if self.total_docs % _AUTOSAVE_EVERY == 0:
                self._save_unlocked()
        return True

    def train_many(self, examples: list[tuple[str, str]]) -> int:
        """Bulk train. Returns number of accepted examples."""
        accepted = 0
        with self._lock:
            for text, label in examples:
                if label not in CLASSES:
                    continue
                features = self._tokenize(text)
                if not features:
                    continue
                self.class_counts[label] += 1
                self.total_docs += 1
                for f in features:
                    self.feature_counts[label][f] += 1
                    self.vocab.add(f)
                accepted += 1
            self._save_unlocked()
        return accepted

    def predict(self, text: str) -> dict:
        """Predict the class distribution + risk_score for a piece of text.

        Schema:
            {
                "predicted_class": "coercion" | None,
                "confidence": 0.87,
                "probabilities": {"seguro": 0.05, ...},
                "risk_score": 0.82,
                "insufficient_data": False,
            }

        When `total_docs < _MIN_DOCS_FOR_PREDICTION`, returns
        `insufficient_data=True` and the pipeline ignores this layer.
        """
        if self.total_docs < _MIN_DOCS_FOR_PREDICTION:
            return {
                "predicted_class": None,
                "confidence": 0.0,
                "probabilities": {},
                "risk_score": None,
                "insufficient_data": True,
            }

        with self._lock:
            features = self._tokenize(text)
            if not features:
                return {
                    "predicted_class": None,
                    "confidence": 0.0,
                    "probabilities": {},
                    "risk_score": None,
                    "insufficient_data": True,
                }

            vocab_size = max(len(self.vocab), 1)
            log_probs: dict[str, float] = {}
            for cls in CLASSES:
                # Prior P(class) con smoothing
                log_prior = math.log(
                    (self.class_counts[cls] + self.SMOOTHING)
                    / (self.total_docs + self.SMOOTHING * len(CLASSES))
                )
                # Likelihood P(features | class) con smoothing por feature
                total_features_in_class = sum(self.feature_counts[cls].values())
                log_likelihood = 0.0
                for f in features:
                    count = self.feature_counts[cls].get(f, 0)
                    log_likelihood += math.log(
                        (count + self.SMOOTHING)
                        / (total_features_in_class + self.SMOOTHING * vocab_size)
                    )
                log_probs[cls] = log_prior + log_likelihood

            # log-sum-exp para evitar underflow
            max_log = max(log_probs.values())
            exp_probs = {cls: math.exp(lp - max_log) for cls, lp in log_probs.items()}
            total_exp = sum(exp_probs.values()) or 1.0
            probs = {cls: ep / total_exp for cls, ep in exp_probs.items()}

            predicted = max(probs, key=probs.get)
            confidence = probs[predicted]
            # Score ponderado por probabilidad
            risk_score = sum(probs[c] * _RISK_MAP[c] for c in CLASSES)

            return {
                "predicted_class": predicted,
                "confidence": round(confidence, 3),
                "probabilities": {k: round(v, 3) for k, v in probs.items()},
                "risk_score": round(risk_score, 3),
                "insufficient_data": False,
            }

    def get_stats(self) -> dict:
        """Diagnostic snapshot for /bayesian/stats."""
        with self._lock:
            top_features: dict[str, list[tuple[str, int]]] = {}
            for cls in CLASSES:
                items = self.feature_counts[cls].items()
                # Filter out features that fired only once (likely noise) and rank by count.
                ranked = sorted(
                    [(f, n) for f, n in items if n >= _TOP_FEATURE_MIN_COUNT],
                    key=lambda x: -x[1],
                )[:10]
                if ranked:
                    top_features[cls] = ranked
            return {
                "total_training_examples": self.total_docs,
                "class_distribution": dict(self.class_counts),
                "vocabulary_size": len(self.vocab),
                "top_features_per_class": top_features,
                "model_path": str(self.model_path),
                "min_docs_required": _MIN_DOCS_FOR_PREDICTION,
            }

    def save(self) -> None:
        """Force-flush the model to disk."""
        with self._lock:
            self._save_unlocked()

    # -------- Internals --------

    def _tokenize(self, text: str) -> list[str]:
        """Return n-grams (1,2,3) from normalized text.

        Bounded by _MAX_TOKENS_PER_DOC to keep memory predictable: a
        1 MB hostile paste from /feedback would otherwise allocate ~3M
        n-gram strings and OOM the worker. We trim *words* before
        emitting n-grams so the n-gram count stays O(N).
        """
        norm = _normalize(text)
        if not norm or len(norm) < 3:
            return []
        words = norm.split()
        if not words:
            return []
        # Bound work per call. A huge paste at /feedback would otherwise
        # blow up training time + RAM linearly with input size.
        if len(words) > _MAX_TOKENS_PER_DOC:
            words = words[:_MAX_TOKENS_PER_DOC]
        features: list[str] = list(words)  # unigrams
        for i in range(len(words) - 1):
            features.append(f"{words[i]}_{words[i + 1]}")
        for i in range(len(words) - 2):
            features.append(f"{words[i]}_{words[i + 1]}_{words[i + 2]}")
        return features

    def _save_unlocked(self) -> None:
        data = {
            "version": 1,
            "total_docs": self.total_docs,
            "class_counts": dict(self.class_counts),
            "feature_counts": {
                cls: dict(counts) for cls, counts in self.feature_counts.items()
            },
        }
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            # Atomic write: tmp then rename so a crash never leaves a partial
            # file. Use a per-PID tmp suffix so two concurrent processes
            # (e.g. systemd reload while a worker is mid-train) don't clobber
            # each other's partial files.
            tmp = self.model_path.with_suffix(
                self.model_path.suffix + f".tmp.{os.getpid()}"
            )
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
                # fsync the file's contents to disk before the rename so
                # a power loss between rename + sync can't surface a
                # zero-byte model on next boot.
                f.flush()
                try:
                    os.fsync(f.fileno())
                except (OSError, AttributeError):
                    # Some filesystems (CIFS, /tmp on test runners) reject
                    # fsync; the rename below is still atomic via os.replace
                    # so durability is best-effort.
                    pass
            os.replace(tmp, self.model_path)
        except Exception:
            # Persist is best-effort; if we crash here the next train_one
            # retries. Best-effort tmp cleanup so we don't leak files.
            try:
                if "tmp" in locals() and tmp.exists():
                    tmp.unlink()
            except Exception:
                pass

    def _load(self) -> None:
        if not self.model_path.exists():
            return
        try:
            data = json.loads(self.model_path.read_text(encoding="utf-8"))
            self.total_docs = int(data.get("total_docs", 0))
            cc = data.get("class_counts") or {}
            for c in CLASSES:
                self.class_counts[c] = int(cc.get(c, 0))
            fc = data.get("feature_counts") or {}
            self.feature_counts = {
                c: defaultdict(int, {k: int(v) for k, v in fc.get(c, {}).items()})
                for c in CLASSES
            }
            self.vocab = set()
            for counts in self.feature_counts.values():
                self.vocab.update(counts.keys())
        except Exception:
            # Corrupted file → start fresh (and the next save will overwrite it).
            pass


# Singleton-style helper for FastAPI app.state wiring.
_DEFAULT_INSTANCE: NaiveBayesClassifier | None = None


def get_bayesian(force_new: bool = False) -> NaiveBayesClassifier:
    global _DEFAULT_INSTANCE
    if _DEFAULT_INSTANCE is None or force_new:
        _DEFAULT_INSTANCE = NaiveBayesClassifier()
    return _DEFAULT_INSTANCE


def _reset_singleton_for_tests() -> None:
    """Clear the module-level singleton so the next get_bayesian() builds
    a fresh instance pointing at whatever BAYESIAN_MODEL_PATH currently is.
    Test-only helper — production code should never call this.
    """
    global _DEFAULT_INSTANCE
    _DEFAULT_INSTANCE = None
