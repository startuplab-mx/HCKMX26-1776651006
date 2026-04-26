"""Iteration 2 — re-run only the rows that failed in iteration 1.

Reads scripts/corpus_v2_results.csv, filters to FAIL_FN + FAIL_FP, re-runs
those phrases, and writes scripts/corpus_v2_iter2.csv. Much faster than
re-running the full 240.
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
SRC = ROOT / "scripts" / "corpus_v2_results.csv"
OUT = ROOT / "scripts" / "corpus_v2_iter2.csv"
API = "http://159.223.187.6/analyze"
PACING = 4.0


def post(text):
    body = json.dumps({"text": text, "use_llm": False}).encode("utf-8")
    req = urllib.request.Request(
        API, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(15 * (attempt + 1))
                continue
            return {"_error": f"HTTP {e.code}"}
        except Exception as e:
            return {"_error": str(e)[:120]}
    return {"_error": "max_retries"}


def main():
    if not SRC.exists():
        print(f"ERROR: {SRC} not found")
        sys.exit(1)

    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    targets = [r for r in rows if r["verdict"] in ("FAIL_FN", "FAIL_FP")]
    print(f"iter1 had {len(targets)} failures: {sum(1 for r in targets if r['verdict']=='FAIL_FN')} FN, {sum(1 for r in targets if r['verdict']=='FAIL_FP')} FP")
    if not targets:
        print("Nothing to re-check.")
        return

    print(f"Re-checking {len(targets)} phrases. ETA: {len(targets) * PACING / 60:.1f} min")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "n", "phrase", "expected_level", "expected_phase", "category",
            "iter1_level", "iter1_score", "iter1_verdict",
            "iter2_level", "iter2_score", "iter2_verdict",
            "improvement",
        ])
        w.writeheader()

        improved = 0
        regressed = 0
        same = 0
        for i, row in enumerate(targets, 1):
            r = post(row["phrase"])
            if "_error" in r:
                level = "ERROR"
                score = 0.0
            else:
                level = r.get("risk_level", "?")
                score = float(r.get("risk_score", 0.0))

            # Decide iter2 verdict using same logic as iter1
            exp = row["expected_level"]
            if exp == "ATENCION_OR_PELIGRO":
                iter2_verdict = "PASS" if level in ("ATENCION", "PELIGRO") else "FAIL_FN"
            elif exp == "SEGURO":
                iter2_verdict = "PASS" if level == "SEGURO" else "FAIL_FP"
            else:
                iter2_verdict = "PASS" if level == exp else (
                    "FAIL_FN" if level == "SEGURO" else "FAIL_FP"
                )

            # Improvement direction
            if row["verdict"] != "PASS" and iter2_verdict == "PASS":
                improvement = "FIXED"
                improved += 1
            elif row["verdict"] == "PASS" and iter2_verdict != "PASS":
                improvement = "REGRESSED"
                regressed += 1
            else:
                improvement = "SAME"
                same += 1

            w.writerow({
                "n": i,
                "phrase": row["phrase"],
                "expected_level": exp,
                "expected_phase": row["expected_phase"],
                "category": row["category"],
                "iter1_level": row["actual_level"],
                "iter1_score": row["actual_score"],
                "iter1_verdict": row["verdict"],
                "iter2_level": level,
                "iter2_score": f"{score:.3f}",
                "iter2_verdict": iter2_verdict,
                "improvement": improvement,
            })
            f.flush()

            print(f"[{i}/{len(targets)}] {row['phrase'][:50]:50s} | iter1:{row['actual_level']:8s}→ iter2:{level:8s} [{improvement}]")
            if i < len(targets):
                time.sleep(PACING)

    print()
    print("=" * 60)
    print(f"ITER2 SUMMARY")
    print(f"  Phrases re-checked: {len(targets)}")
    print(f"  FIXED:     {improved}")
    print(f"  SAME:      {same}")
    print(f"  REGRESSED: {regressed}")
    print(f"  CSV: {OUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
