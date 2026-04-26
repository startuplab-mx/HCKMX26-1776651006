"""Run the 240 corpus locally via direct Python import — no HTTP, no rate limit.

Use this for immediate iteration; the HTTP harness validates against
production but is rate-limited.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

# Quiet boot
os.environ.setdefault("DATABASE_PATH", ":memory:")
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("NAHUAL_API_KEY", "")

from test_corpus_v2 import CORPUS  # noqa: E402

# Force the bayesian to load the production model file
prod_model = ROOT / "backend" / "classifier" / "bayesian_model.json"
os.environ["BAYESIAN_MODEL_PATH"] = str(prod_model)

from classifier.pipeline import Pipeline  # noqa: E402

OUT = ROOT / "scripts" / "corpus_v2_local.csv"


def verdict_for(actual: str, expected: str) -> str:
    if expected == "ATENCION_OR_PELIGRO":
        return "PASS" if actual in ("ATENCION", "PELIGRO") else "FAIL_FN"
    if expected == "SEGURO":
        return "PASS" if actual == "SEGURO" else "FAIL_FP"
    if actual == expected:
        return "PASS"
    levels = {"SEGURO": 0, "ATENCION": 1, "PELIGRO": 2}
    return "FAIL_FN" if levels.get(actual, 0) < levels.get(expected, 0) else "FAIL_FP"


def main() -> None:
    pipeline = Pipeline()
    print(f"Running {len(CORPUS)} phrases locally (heuristic + bayesian, no LLM)...")

    counters = {"PASS": 0, "FAIL_FN": 0, "FAIL_FP": 0}
    rows = []

    for i, entry in enumerate(CORPUS, 1):
        phrase, expected_level, expected_phase, category, notes = entry
        r = pipeline.classify(phrase, use_llm=False)
        level = r["risk_level"]
        score = r["risk_score"]
        bay = r.get("bayesian") or {}
        bs = bay.get("risk_score") if bay else None
        bc = bay.get("predicted_class") if bay else None
        v = verdict_for(level, expected_level)
        counters[v] = counters.get(v, 0) + 1
        rows.append({
            "n": i,
            "phrase": phrase,
            "expected_level": expected_level,
            "expected_phase": expected_phase,
            "category": category,
            "notes": notes,
            "actual_level": level,
            "actual_score": f"{score:.3f}",
            "override": r["override_triggered"],
            "bayesian_score": f"{bs:.3f}" if bs is not None else "",
            "bayesian_class": bc or "",
            "verdict": v,
        })
        if i % 30 == 0:
            print(f"  [{i:3d}] PASS={counters['PASS']} FN={counters['FAIL_FN']} FP={counters['FAIL_FP']}")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print()
    print("=" * 70)
    print("LOCAL CORPUS RESULTS (heurístico + bayesiano, NO LLM)")
    print(f"  PASS:    {counters['PASS']:4d} / {len(CORPUS)}  ({100*counters['PASS']//len(CORPUS)}%)")
    print(f"  FAIL_FN: {counters['FAIL_FN']:4d}  (debería disparar pero no lo hizo)")
    print(f"  FAIL_FP: {counters['FAIL_FP']:4d}  (disparó pero no debería)")
    print("=" * 70)
    print(f"CSV: {OUT}")

    # Show sample of fails
    fails = [r for r in rows if r["verdict"] != "PASS"]
    if fails:
        print(f"\nFirst 15 failures:")
        for r in fails[:15]:
            print(f"  [{r['verdict']:7s}] expected={r['expected_level']:18s} got={r['actual_level']:9s} score={r['actual_score']}  | {r['phrase'][:60]}")


if __name__ == "__main__":
    main()
