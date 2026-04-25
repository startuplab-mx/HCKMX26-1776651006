#!/usr/bin/env bash
# Nahual demo launcher (macOS/Linux/MSYS2).
# Pre-req: backend + bot deps installed.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== NAHUAL — demo launcher ==="

cleanup() {
  echo
  echo "Stopping background processes..."
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT

(cd "$ROOT/backend" && PYTHONIOENCODING=utf-8 python -m uvicorn main:app --reload --port 8000) &
sleep 3

(cd "$ROOT/panel" && python -m http.server 3000) &

echo
echo "Backend: http://localhost:8000/docs"
echo "Panel:   http://localhost:3000"
echo
echo "Para ejecutar el bot:        cd bot && node index.js"
echo "Para simulación sin WA:      cd bot && node simulate.js"
echo "Para sembrar datos demo:     python scripts/seed_test_data.py"
echo
echo "Ctrl-C para detener."
wait
