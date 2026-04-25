#!/usr/bin/env bash
# ============================================================
#  NAHUAL  -  one-click demo launcher (macOS / Linux / WSL)
# ------------------------------------------------------------
#  Boots backend (FastAPI) + panel (static HTTP) + seeds demo
#  data, then opens Swagger and the panel in the default
#  browser. Bot is NOT auto-started.
# ============================================================
set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

cat <<'BANNER'

============================================================
  NAHUAL  --  Sistema de Deteccion de Reclutamiento Criminal
  Hackathon 404: Threat Not Found  --  StartupLab MX + INL
============================================================

BANNER

# Open URLs in the default browser across platforms.
open_url() {
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 &
  elif command -v open >/dev/null 2>&1; then open "$1" >/dev/null 2>&1 &
  elif command -v start >/dev/null 2>&1; then start "$1" >/dev/null 2>&1 &
  fi
}

# ---- 1. Dependency checks ---------------------------------------------------
echo "[1/5] Verificando dependencias..."
command -v python  >/dev/null 2>&1 || PYTHON_BIN=python3
PYTHON_BIN=${PYTHON_BIN:-python}
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "  [ERROR] Python no encontrado. Instala Python 3.11+." ; exit 1
fi
if ! command -v node >/dev/null 2>&1; then
  echo "  [WARN]  Node.js no encontrado. El bot WhatsApp no podra ejecutarse."
fi
if [ ! -f "backend/requirements.txt" ]; then
  echo "  [ERROR] No estas en la raiz del repo nahual/." ; exit 1
fi

if ! "$PYTHON_BIN" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "  Instalando dependencias del backend..."
  "$PYTHON_BIN" -m pip install -q -r backend/requirements.txt
fi
echo "  OK: $PYTHON_BIN, fastapi, uvicorn"

# ---- 2. .env check ----------------------------------------------------------
echo "[2/5] Verificando .env..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  No existia .env -- creado desde .env.example"
fi
echo "  OK: .env presente"

# ---- 3. Seed demo data ------------------------------------------------------
echo "[3/5] Sembrando datos demo si la base esta vacia..."
NEED_SEED=$("$PYTHON_BIN" - <<'PY'
import sqlite3, os
p = "backend/nahual.db"
if not os.path.exists(p):
    print("yes"); raise SystemExit
try:
    n = sqlite3.connect(p).execute("select count(*) from alerts").fetchone()[0]
except Exception:
    print("yes"); raise SystemExit
print("no" if n > 0 else "yes")
PY
)
if [ "$NEED_SEED" = "yes" ]; then
  "$PYTHON_BIN" scripts/seed_test_data.py >/dev/null 2>&1 || true
  echo "  OK: datos demo sembrados"
else
  echo "  OK: ya hay alertas en la base, no se sembro"
fi

# ---- 4. Launch services -----------------------------------------------------
echo "[4/5] Levantando backend + panel..."
cleanup() {
  echo
  echo "Deteniendo procesos en background..."
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(
  cd "$ROOT/backend"
  PYTHONIOENCODING=utf-8 "$PYTHON_BIN" -m uvicorn main:app --port 8000
) &
sleep 4

(
  cd "$ROOT/panel"
  "$PYTHON_BIN" -m http.server 3000
) &
sleep 2

# ---- 5. Open browser --------------------------------------------------------
echo "[5/5] Abriendo navegador..."
open_url "http://localhost:3000"
sleep 1
open_url "http://localhost:8000/docs"

cat <<'POST'

============================================================
  Backend:    http://localhost:8000      Swagger: /docs
  Panel:      http://localhost:3000
  Health:     http://localhost:8000/health

  Bot WhatsApp:    cd bot && node index.js     (escanea QR)
  Demo sin WA:     cd bot && node simulate.js
  Demo en vivo:    python scripts/demo_live.py
============================================================

Ctrl-C para detener.
POST

wait
