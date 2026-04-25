"""Precision Processor — DB feedback + tuner unit + HTTP integration."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classifier.heuristic import HeuristicClassifier  # noqa: E402
from classifier.llm_layer import LLMLayer  # noqa: E402
from classifier.pipeline import Pipeline  # noqa: E402
from classifier.precision import PrecisionProcessor  # noqa: E402
from database.db import Database  # noqa: E402


# ---------------- DB-level feedback ----------------


def test_save_and_get_unprocessed_feedback(tmp_path):
    db = Database(path=tmp_path / "fb.db")
    fid = db.save_feedback(
        feedback_type="confirm",
        alert_id=1,
        pattern_ids=["phase3.001"],
        session_id="u1",
    )
    pending = db.get_unprocessed_feedback()
    assert len(pending) == 1
    assert pending[0]["id"] == fid
    assert pending[0]["pattern_ids"] == ["phase3.001"]
    assert pending[0]["processed"] == 0


def test_mark_feedback_processed_filters_pending(tmp_path):
    db = Database(path=tmp_path / "fb.db")
    a = db.save_feedback(feedback_type="confirm", pattern_ids=["a"])
    b = db.save_feedback(feedback_type="deny", pattern_ids=["b"])
    db.mark_feedback_processed([a])
    remaining = db.get_unprocessed_feedback()
    assert len(remaining) == 1
    assert remaining[0]["id"] == b


def test_feedback_stats(tmp_path):
    db = Database(path=tmp_path / "fb.db")
    db.save_feedback(feedback_type="confirm", pattern_ids=["a"])
    db.save_feedback(feedback_type="confirm", pattern_ids=["b"])
    db.save_feedback(feedback_type="deny", pattern_ids=["c"])
    stats = db.feedback_stats()
    assert stats["total"] == 3
    assert stats["pending"] == 3
    assert stats["by_type"]["confirm"] == 2
    assert stats["by_type"]["deny"] == 1


# ---------------- PrecisionProcessor unit ----------------


def test_get_adjusted_weight_returns_base_when_no_overrides(tmp_path):
    db = Database(path=tmp_path / "p.db")
    p = PrecisionProcessor(db)
    assert p.get_adjusted_weight("phase3.001", 0.9) == 0.9


def test_process_pending_skips_when_below_min(tmp_path):
    db = Database(path=tmp_path / "p.db")
    db.save_feedback(feedback_type="confirm", pattern_ids=["x"])
    p = PrecisionProcessor(db)
    result = p.process_pending_feedback()
    assert result["processed"] == 0
    assert result["reason"] == "insufficient_feedback"


def test_process_pending_applies_confirm_nudge(tmp_path):
    db = Database(path=tmp_path / "p.db")
    pid = "phase1.000"
    for _ in range(5):
        db.save_feedback(feedback_type="confirm", pattern_ids=[pid])
    p = PrecisionProcessor(db)
    result = p.process_pending_feedback()
    assert result["processed"] == 5
    assert pid in result["adjustments"]
    # confirm nudge is +0.02 per row, 5 rows → +0.10
    assert p.weight_adjustments[pid] == 0.10
    assert p.get_adjusted_weight(pid, 0.5) == 0.60
    # Marked as processed → next call says insufficient.
    assert p.process_pending_feedback()["processed"] == 0


def test_deny_pulls_weight_down_and_clamps(tmp_path):
    db = Database(path=tmp_path / "p.db")
    pid = "phase1.000"
    # 10 denies → -0.50 raw, clamped at -0.20 (MAX_ADJUSTMENT).
    for _ in range(10):
        db.save_feedback(feedback_type="deny", pattern_ids=[pid])
    p = PrecisionProcessor(db)
    p.process_pending_feedback()
    assert p.weight_adjustments[pid] == -0.20
    assert p.get_adjusted_weight(pid, 0.5) == 0.30


def test_operator_signals_have_double_magnitude(tmp_path):
    db = Database(path=tmp_path / "p.db")
    pid = "phase4.000"
    for _ in range(5):
        db.save_feedback(feedback_type="operator_fp", pattern_ids=[pid])
    p = PrecisionProcessor(db)
    p.process_pending_feedback()
    # operator_fp = -0.08 per row → -0.40 raw → clamped at -0.20.
    assert p.weight_adjustments[pid] == -0.20
    stats = p.pattern_stats[pid]
    assert stats["denials"] == 10  # operator_fp counts double


def test_llm_discrepancy_nudges_based_on_direction(tmp_path):
    db = Database(path=tmp_path / "p.db")
    pid_high = "phase3.001"  # heuristic over-fires
    pid_low = "phase3.002"   # heuristic under-fires
    for _ in range(5):
        db.save_feedback(
            feedback_type="llm_discrepancy",
            pattern_ids=[pid_high],
            heuristic_score=0.8,
            llm_score=0.3,
        )
        db.save_feedback(
            feedback_type="llm_discrepancy",
            pattern_ids=[pid_low],
            heuristic_score=0.2,
            llm_score=0.7,
        )
    p = PrecisionProcessor(db)
    p.process_pending_feedback()
    assert p.weight_adjustments[pid_high] < 0
    assert p.weight_adjustments[pid_low] > 0


def test_diagnostics_flags_problematic_patterns(tmp_path):
    db = Database(path=tmp_path / "p.db")
    pid = "phase1.000"
    # 5 denies + 1 confirm → precision_score = 1/6 ≈ 0.17 < 0.7
    for _ in range(5):
        db.save_feedback(feedback_type="deny", pattern_ids=[pid])
    db.save_feedback(feedback_type="confirm", pattern_ids=[pid])
    p = PrecisionProcessor(db)
    p.process_pending_feedback()
    diag = p.get_diagnostics()
    assert pid in diag["problematic_patterns"]
    assert diag["problematic_patterns"][pid]["precision"] < 0.7


def test_export_import_state_roundtrip(tmp_path):
    db = Database(path=tmp_path / "p.db")
    pid = "phase1.000"
    for _ in range(5):
        db.save_feedback(feedback_type="confirm", pattern_ids=[pid])
    p1 = PrecisionProcessor(db)
    p1.process_pending_feedback()
    state = p1.export_state()

    p2 = PrecisionProcessor(db)
    assert p2.get_adjusted_weight(pid, 0.5) == 0.5
    p2.import_state(state)
    assert p2.get_adjusted_weight(pid, 0.5) == 0.6


# ---------------- Heuristic respects overrides ----------------


def test_heuristic_uses_adjusted_weight(tmp_path):
    """Confirm the heuristic actually consults the overrides at scoring time."""
    db = Database(path=tmp_path / "p.db")
    p = PrecisionProcessor(db)
    # Find the pattern_id for "yo quiero jale" and crank it down hard.
    target_id = "phase1.000"  # first phase1 pattern
    p.weight_adjustments[target_id] = -0.20
    h = HeuristicClassifier()
    base = h.classify("yo quiero jale")
    tuned = h.classify("yo quiero jale", weight_overrides=p)
    # Adjusted phase1 score should be ≤ base phase1 score.
    assert tuned["phase_scores"]["phase1"] <= base["phase_scores"]["phase1"]


# ---------------- Pipeline integration ----------------


class _OfflineLLM(LLMLayer):
    @property
    def enabled(self) -> bool:
        return False


def test_pipeline_auto_tunes_after_interval(tmp_path, monkeypatch):
    """Every TUNING_INTERVAL classifications drains the queue."""
    monkeypatch.setenv("PRECISION_TUNING_INTERVAL", "3")
    # Reload pipeline module so it picks up the env var.
    import importlib

    import classifier.pipeline as pipeline_mod

    importlib.reload(pipeline_mod)

    db = Database(path=tmp_path / "p.db")
    p = pipeline_mod.PrecisionProcessor(db)  # exported through module attr fallback
    pipe = pipeline_mod.Pipeline(llm=_OfflineLLM(), precision=p)

    # Seed feedback so the next tune cycle does work.
    for _ in range(5):
        db.save_feedback(feedback_type="confirm", pattern_ids=["phase1.000"])

    # Two classifications — interval is 3, so no tune yet.
    pipe.classify("hola")
    pipe.classify("vienes al cumple?")
    assert db.feedback_stats()["pending"] == 5

    # Third classification triggers _maybe_tune.
    pipe.classify("hola otra vez")
    assert db.feedback_stats()["pending"] == 0


# ---------------- HTTP integration ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "precision_api.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    os.environ["PRECISION_TUNING_INTERVAL"] = "999"  # don't auto-tune in tests
    import importlib

    import database.db as db_module
    import main as main_module
    import webhooks as wh_module

    importlib.reload(wh_module)
    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_post_feedback_persists(tmp_path):
    with _client(tmp_path) as c:
        r = c.post(
            "/feedback",
            json={
                "feedback_type": "confirm",
                "alert_id": 1,
                "pattern_ids": ["phase3.001"],
                "session_id": "demo",
            },
        )
        assert r.status_code == 201
        assert r.json()["received"] is True

        stats = c.get("/precision/stats").json()
        assert stats["total"] == 1
        assert stats["pending"] == 1
        assert stats["by_type"]["confirm"] == 1


def test_post_feedback_rejects_unknown_type(tmp_path):
    with _client(tmp_path) as c:
        r = c.post(
            "/feedback",
            json={"feedback_type": "weird", "pattern_ids": ["x"]},
        )
        assert r.status_code == 422


def test_precision_diagnostics_empty_initially(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/precision/diagnostics")
        body = r.json()
        assert r.status_code == 200
        assert body["total_adjustments_active"] == 0


def test_force_tune_drains_queue(tmp_path):
    with _client(tmp_path) as c:
        for _ in range(5):
            c.post(
                "/feedback",
                json={"feedback_type": "confirm", "pattern_ids": ["phase1.000"]},
            )
        r = c.post("/precision/tune")
        body = r.json()
        assert r.status_code == 200
        assert body["processed"] == 5
        diag = c.get("/precision/diagnostics").json()
        assert "phase1.000" in diag["weight_adjustments"]


def test_state_export_returns_jsonable(tmp_path):
    with _client(tmp_path) as c:
        for _ in range(5):
            c.post(
                "/feedback",
                json={"feedback_type": "deny", "pattern_ids": ["phase4.000"]},
            )
        c.post("/precision/tune")
        state = c.get("/precision/state").json()
        assert "adjustments" in state
        assert "stats" in state
        assert "phase4.000" in state["adjustments"]
