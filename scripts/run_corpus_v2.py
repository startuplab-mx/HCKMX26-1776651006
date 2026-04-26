"""Run the 240+ corpus_v2 test against production /analyze.

Writes incrementally so a rate-limit storm doesn't lose all data.
Output: scripts/corpus_v2_results.csv
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from test_corpus_v2 import CORPUS  # noqa: E402

API = "http://159.223.187.6/analyze"
OUT_CSV = ROOT / "scripts" / "corpus_v2_results.csv"
PACING_SEC = 4.0  # 15/min — under both /analyze and /alert rate limits


USE_LLM = False  # Heurístico + Bayesiano only — tests the layers' real quality.


def post(text: str, attempt: int = 1) -> dict:
    body = json.dumps({"text": text, "use_llm": USE_LLM}).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt < 3:
            time.sleep(15 * attempt)
            return post(text, attempt + 1)
        return {"_error": f"HTTP {e.code}"}
    except Exception as e:
        return {"_error": str(e)[:120]}


def verdict_for(actual_level: str, expected_level: str) -> str:
    """Compare actual vs expected. Returns:
    PASS | FAIL_FN (false negative) | FAIL_FP (false positive)
    """
    if expected_level == "ATENCION_OR_PELIGRO":
        return "PASS" if actual_level in ("ATENCION", "PELIGRO") else "FAIL_FN"
    if expected_level == "SEGURO":
        return "PASS" if actual_level == "SEGURO" else "FAIL_FP"
    if expected_level == actual_level:
        return "PASS"
    # Mismatched level — track direction
    levels = {"SEGURO": 0, "ATENCION": 1, "PELIGRO": 2}
    actual = levels.get(actual_level, 0)
    expected = levels.get(expected_level, 0)
    return "FAIL_FN" if actual < expected else "FAIL_FP"


def main():
    n = len(CORPUS)
    print(f"Corpus: {n} phrases. Pacing: {PACING_SEC}s. ETA: {n * PACING_SEC / 60:.1f} min.")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    counters = {"PASS": 0, "FAIL_FN": 0, "FAIL_FP": 0, "ERROR": 0}

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "n", "phrase", "expected_level", "expected_phase", "category",
                "notes", "actual_level", "actual_score", "override", "llm_used",
                "bayesian_score", "bayesian_class", "verdict",
            ],
        )
        w.writeheader()

        for i, entry in enumerate(CORPUS, 1):
            phrase, expected_level, expected_phase, category, notes = entry
            r = post(phrase)
            if "_error" in r:
                counters["ERROR"] += 1
                level = "ERROR"
                score = 0.0
                ovr = False
                llm = False
                bs = None
                bc = None
                verdict = "ERROR"
            else:
                level = r.get("risk_level", "?")
                score = float(r.get("risk_score", 0.0))
                ovr = bool(r.get("override_triggered", False))
                llm = bool(r.get("llm_used", False))
                bay = r.get("bayesian") or {}
                bs = bay.get("risk_score") if bay else None
                bc = bay.get("predicted_class") if bay else None
                verdict = verdict_for(level, expected_level)
                counters[verdict] = counters.get(verdict, 0) + 1

            row = {
                "n": i,
                "phrase": phrase,
                "expected_level": expected_level,
                "expected_phase": expected_phase,
                "category": category,
                "notes": notes,
                "actual_level": level,
                "actual_score": f"{score:.3f}",
                "override": ovr,
                "llm_used": llm,
                "bayesian_score": f"{bs:.3f}" if bs is not None else "",
                "bayesian_class": bc or "",
                "verdict": verdict,
            }
            rows.append(row)
            w.writerow(row)
            f.flush()

            flag = "OK" if verdict == "PASS" else verdict
            print(f"[{i:3d}/{n}] {flag:8s} {level:9s} {score:.2f} | {phrase[:62]}")

            if i < n:
                time.sleep(PACING_SEC)

    print()
    print("=" * 80)
    print("RESULTS")
    print(f"  PASS:    {counters['PASS']:4d} / {n}")
    print(f"  FAIL_FN: {counters['FAIL_FN']:4d}  (false negatives — should fire but didn't)")
    print(f"  FAIL_FP: {counters['FAIL_FP']:4d}  (false positives — fired but shouldn't)")
    print(f"  ERROR:   {counters['ERROR']:4d}")
    print(f"  Accuracy: {100 * counters['PASS'] / max(1, n):.1f}%")
    print("=" * 80)
    print(f"CSV: {OUT_CSV}")


if __name__ == "__main__":
    main()
