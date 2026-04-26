"""Extract false negatives + positives from the partial _selffeed_run logs.

The harness's CSV write happens only at the end (after 192 phrases). With
the rate limiting on production both runs got partway through, but we
can still recover the per-phrase verdicts from stdout.

This script parses both logs, dedupes by phrase, classifies as
FALSE_NEGATIVE / ALREADY_COVERED, and writes the CSV that the patcher
needs.
"""
import re
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
LOGS = [
    ROOT / "scripts" / "_selffeed_run.log",
    ROOT / "scripts" / "_selffeed_run2.log",
]
OUT_CSV = ROOT / "scripts" / "dataset_self_feed_results.csv"
OUT_NEG = ROOT / "scripts" / "_selffeed_neg.json"

# Map phrases to candidate metadata from the harness file.
HARNESS = ROOT / "scripts" / "_selffeed_run.py"

# Pull CANDIDATES tuples from the harness source.
src = HARNESS.read_text(encoding="utf-8")
# Match  ("phrase", "url", N, "cat", weight),
candidate_re = re.compile(
    r'\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*,\s*(\d)\s*,\s*"([^"]+)"\s*,\s*([\d.]+)\s*\)',
)
CANDIDATES = {}
for m in candidate_re.finditer(src):
    phrase = m.group(1)
    CANDIDATES[phrase.lower()] = {
        "phrase": phrase,
        "source_url": m.group(2),
        "expected_phase": int(m.group(3)),
        "category": m.group(4),
        "weight": float(m.group(5)),
    }

# Parse log lines: "[N/192] LEVEL  SCORE  phrase..."
line_re = re.compile(
    r"^\[\d+/\d+\]\s+(SEGURO|ATENCION|PELIGRO|ERROR)\s+(\d+\.\d+)?\s*(.*)$"
)
results = {}  # phrase → {level, score}
for log in LOGS:
    if not log.exists():
        continue
    raw = log.read_bytes().decode("utf-8", errors="replace")
    for line in raw.splitlines():
        m = line_re.match(line.strip())
        if not m:
            continue
        level = m.group(1)
        score = float(m.group(2)) if m.group(2) else 0.0
        text = m.group(3).strip()
        if not text or level == "ERROR":
            continue
        # The phrase is the rest after the score; harness prints first 60 chars.
        # Use it as a key, lowercase for matching CANDIDATES dict.
        results[text.lower()] = (level, score)

print(f"Parsed {len(results)} unique results from {len(LOGS)} logs.")

# Build CSV rows by joining harness candidates with parsed verdicts.
rows = []
falsneg = []
covered = 0
for key, meta in CANDIDATES.items():
    if key not in results:
        # not yet tested
        continue
    level, score = results[key]
    if level == "SEGURO":
        verdict = "FALSE_NEGATIVE"
        falsneg.append({
            "phrase": key,
            "phrase_raw": meta["phrase"],
            "source_url": meta["source_url"],
            "expected_phase": meta["expected_phase"],
            "suggested_category": meta["category"],
            "suggested_weight": meta["weight"],
        })
    else:
        verdict = "ALREADY_COVERED"
        covered += 1
    rows.append({
        "phrase": meta["phrase"],
        "source_url": meta["source_url"],
        "expected_phase": meta["expected_phase"],
        "actual_level": level,
        "actual_score": f"{score:.3f}",
        "verdict": verdict,
        "suggested_weight": meta["weight"],
        "suggested_category": meta["category"],
    })

# Write CSV.
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "phrase", "source_url", "expected_phase",
            "actual_level", "actual_score", "verdict",
            "suggested_weight", "suggested_category",
        ],
    )
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"CSV written: {OUT_CSV} ({len(rows)} rows)")

OUT_NEG.write_text(json.dumps(falsneg, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"FN JSON: {OUT_NEG} ({len(falsneg)} false negatives)")

# Summary
by_phase = {1: 0, 2: 0, 3: 0, 4: 0}
for fn in falsneg:
    by_phase[fn["expected_phase"]] = by_phase.get(fn["expected_phase"], 0) + 1
print()
print("=" * 60)
print("SUMMARY")
print(f"  Total tested phrases:    {len(rows)}")
print(f"  Already covered:         {covered}")
print(f"  False negatives found:   {len(falsneg)}")
for p, n in sorted(by_phase.items()):
    print(f"    phase{p}: {n}")
print("=" * 60)
