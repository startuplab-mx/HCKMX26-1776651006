#!/usr/bin/env bash
# Post-fix pipeline — runs after apply_corpus_fixes.py on the droplet.
#
# 1. Rebuild bayesian model with the new pattern surface
# 2. Restart backend so the heuristic re-loads the JSONs
# 3. Smoke-test 5 known phrases
#
# Idempotent. Run on the droplet (not locally).

set -e
cd /opt/nahual

echo "=== STEP 1: Bootstrap Bayesian with the new dataset ==="
rm -f backend/classifier/bayesian_model.json
backend/venv/bin/python scripts/bootstrap_bayesian.py | tail -10

echo
echo "=== STEP 2: Restart backend ==="
systemctl restart nahual-backend
sleep 3
systemctl is-active nahual-backend

echo
echo "=== STEP 3: Smoke test ==="
for txt in \
  "te voy a matar" \
  "me ofrecieron 15 mil pesos a la semana" \
  "manda fotos o las publico" \
  "vienes al cumple el sabado" \
  "estoy trabajando ahorita"; do
  level=$(curl -sf -X POST http://127.0.0.1:8000/analyze \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"$txt\",\"use_llm\":false}" | \
    python3 -c 'import sys,json; r=json.load(sys.stdin); print(r["risk_level"])')
  echo "  [$level] $txt"
done

echo
echo "=== Dataset stats ==="
curl -sf http://127.0.0.1:8000/admin/dataset-info | python3 -c '
import sys,json
r=json.load(sys.stdin)
print(f"  total={r[\"total_patterns\"]}, high-conf={r[\"high_confidence_patterns\"]}")
'

echo
echo "=== Bayesian stats ==="
curl -sf http://127.0.0.1:8000/bayesian/stats | python3 -c '
import sys,json
r=json.load(sys.stdin)
print(f"  total_docs={r[\"total_training_examples\"]}, vocab={r[\"vocabulary_size\"]}")
print(f"  classes={r[\"class_distribution\"]}")
'
