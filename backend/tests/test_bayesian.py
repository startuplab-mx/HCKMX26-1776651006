"""Tests for the Bayesian classifier (Capa 1.5).

Covers:
- Cold start (insufficient_data invariant)
- Incremental training (train_one + train_many)
- Prediction shape + risk_score mapping
- Persistence (save/load)
- Pipeline integration: bayesian payload appears, doesn't crash without data
- Pipeline integration: bayesian merge contributes to final score when trained
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------- Bayesian unit tests ----------------


def test_cold_start_returns_insufficient_data(tmp_path):
    from classifier.bayesian import NaiveBayesClassifier

    bayes = NaiveBayesClassifier(model_path=tmp_path / "cold.json")
    r = bayes.predict("te voy a matar")
    assert r["insufficient_data"] is True
    assert r["risk_score"] is None
    assert r["predicted_class"] is None


def test_train_one_then_predict(tmp_path):
    from classifier.bayesian import NaiveBayesClassifier

    bayes = NaiveBayesClassifier(model_path=tmp_path / "trained.json")
    # Train with enough examples to clear the insufficient-data threshold (≥5)
    examples = [
        ("hola que tal", "seguro"),
        ("estoy bien", "seguro"),
        ("me ganaron en fortnite", "seguro"),
        ("te voy a matar", "coercion"),
        ("te vamos a matar", "coercion"),
        ("voy a matarte", "coercion"),
    ]
    for text, label in examples:
        assert bayes.train_one(text, label) is True

    r = bayes.predict("te voy a matar")
    assert r["insufficient_data"] is False
    assert r["predicted_class"] == "coercion"
    assert r["risk_score"] > 0.5
    assert "probabilities" in r
    assert sum(r["probabilities"].values()) == pytest_approx(1.0, abs_tol=0.01)


def test_train_many_bulk(tmp_path):
    from classifier.bayesian import NaiveBayesClassifier

    bayes = NaiveBayesClassifier(model_path=tmp_path / "bulk.json")
    accepted = bayes.train_many([
        ("hola amigo", "seguro"),
        ("vamos al cine", "seguro"),
        ("te voy a matar si no respondes", "coercion"),
        ("te pago 15000 semanales", "captacion"),
        ("manda fotos o las publico", "explotacion"),
        ("pasate a telegram secreto", "enganche"),
    ])
    assert accepted == 6
    assert bayes.total_docs == 6
    assert bayes.class_counts["coercion"] == 1
    assert bayes.class_counts["seguro"] == 2


def test_invalid_label_rejected(tmp_path):
    from classifier.bayesian import NaiveBayesClassifier

    bayes = NaiveBayesClassifier(model_path=tmp_path / "bad.json")
    assert bayes.train_one("hola", "spam") is False  # spam not in CLASSES
    assert bayes.total_docs == 0


def test_persistence_roundtrip(tmp_path):
    from classifier.bayesian import NaiveBayesClassifier

    p = tmp_path / "persist.json"
    bayes1 = NaiveBayesClassifier(model_path=p)
    for _ in range(15):
        bayes1.train_one("te voy a matar", "coercion")
    # Force flush (auto-save fires every 10 but this guarantees disk).
    bayes1.save()
    assert p.exists()

    # Fresh instance must inherit counters.
    bayes2 = NaiveBayesClassifier(model_path=p)
    assert bayes2.total_docs == 15
    assert bayes2.class_counts["coercion"] == 15
    r = bayes2.predict("te voy a matar")
    assert r["predicted_class"] == "coercion"


def test_tokenize_caps_huge_input(tmp_path):
    """A 200k-word paste must NOT explode memory or run forever. The
    cap (_MAX_TOKENS_PER_DOC) bounds the n-gram count to O(N)."""
    import time
    from classifier.bayesian import NaiveBayesClassifier, _MAX_TOKENS_PER_DOC

    bayes = NaiveBayesClassifier(model_path=tmp_path / "huge.json")
    huge_text = "matar amenaza " * 100_000  # 200k tokens, ~1.4 MB
    t0 = time.perf_counter()
    feats = bayes._tokenize(huge_text)
    elapsed = time.perf_counter() - t0
    # n-gram fanout is roughly 3x the word count (1+2+3 grams), capped:
    # so feats len is bounded ~3 * _MAX_TOKENS_PER_DOC.
    assert len(feats) <= 3 * _MAX_TOKENS_PER_DOC
    assert elapsed < 2.0, f"tokenize took {elapsed:.3f}s"


def test_atomic_save_no_partial_file_on_kill(tmp_path):
    """If a tmp file is left behind from a prior crash, the next save
    must still succeed and produce a clean model."""
    from classifier.bayesian import NaiveBayesClassifier

    p = tmp_path / "atomic.json"
    bayes = NaiveBayesClassifier(model_path=p)
    bayes.train_many([("te voy a matar", "coercion")] * 6)
    bayes.save()
    assert p.exists()
    # Simulate a stale tmp from a prior crashed process.
    stale = p.with_suffix(p.suffix + f".tmp.{os.getpid()}")
    stale.write_text('{"corrupt')  # half-written JSON
    # New save must overwrite the model atomically.
    bayes.train_one("manda fotos o las publico", "explotacion")
    bayes.save()
    # The committed file is well-formed JSON with our data.
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["total_docs"] == 7


def test_get_stats_shape(tmp_path):
    from classifier.bayesian import NaiveBayesClassifier

    bayes = NaiveBayesClassifier(model_path=tmp_path / "stats.json")
    bayes.train_many([("hola", "seguro")] * 3 + [("te voy a matar", "coercion")] * 3)
    s = bayes.get_stats()
    assert s["total_training_examples"] == 6
    assert s["vocabulary_size"] >= 2
    assert "class_distribution" in s
    assert s["min_docs_required"] == 5


# ---------------- Pipeline integration ----------------


def _client(tmp_path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "bay.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    os.environ["NAHUAL_API_KEY"] = ""
    import importlib

    import database.db as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)
    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_pipeline_works_without_bayesian_data(tmp_path):
    """When bayesian has no data (or fails to load), /analyze still works."""
    with _client(tmp_path) as c:
        r = c.post("/analyze", json={"text": "vienes al cumple el sabado"})
        assert r.status_code == 200
        body = r.json()
        # Bayesian field exists in schema; may be None when insufficient_data.
        assert "bayesian" in body
        # Score isn't broken by the layer.
        assert body["risk_level"] == "SEGURO"


def test_bayesian_endpoints_exposed(tmp_path):
    with _client(tmp_path) as c:
        # /bayesian/stats always responds (even with cold model).
        r = c.get("/bayesian/stats")
        assert r.status_code == 200
        body = r.json()
        assert body.get("available") is True
        assert "total_training_examples" in body
        # /bayesian/predict on cold model returns insufficient_data.
        r2 = c.post("/bayesian/predict", json={"text": "te voy a matar"})
        assert r2.status_code == 200
        assert r2.json().get("insufficient_data") is True


def test_pipeline_bayesian_payload_present_after_training(tmp_path):
    """After training the in-memory bayesian, /analyze surfaces the payload."""
    c = _client(tmp_path)
    with c:
        # The TestClient triggers the FastAPI lifespan which sets
        # app.state.pipeline. Reach in via the app the client wraps.
        bayes = c.app.state.pipeline.bayesian
        assert bayes is not None
        # Inject enough examples to clear the threshold.
        for _ in range(3):
            bayes.train_one("hola que tal", "seguro")
            bayes.train_one("vamos al cine", "seguro")
            bayes.train_one("te voy a matar", "coercion")
        # /bayesian/stats now reports activity.
        r = c.get("/bayesian/stats")
        assert r.status_code == 200
        assert r.json().get("total_training_examples") >= 9
        # /analyze includes bayesian payload (non-None now that it has data).
        r2 = c.post("/analyze", json={"text": "te voy a matar"})
        body = r2.json()
        assert body.get("bayesian") is not None
        # The bayesian agreed with the heuristic on a clear coercion phrase.
        assert body["bayesian"]["predicted_class"] in (
            "coercion", "captacion", "explotacion"
        )


# ---------------- helpers ----------------


def pytest_approx(value, abs_tol=1e-6):
    """Tiny stand-in for pytest.approx with absolute tolerance only."""
    class _Approx:
        def __init__(self, v, tol):
            self._v = v
            self._tol = tol

        def __eq__(self, other):
            try:
                return abs(other - self._v) <= self._tol
            except Exception:
                return False

        def __repr__(self):
            return f"~{self._v}±{self._tol}"

    return _Approx(value, abs_tol)
