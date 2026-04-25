@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  NAHUAL  -  one-click demo launcher (Windows)
REM ------------------------------------------------------------
REM  Boots backend (FastAPI) + panel (static HTTP) + seeds demo
REM  data, then opens Swagger and the panel in the default
REM  browser. Bot is NOT auto-started so the QR pairing window
REM  stays under the operator's control.
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo   NAHUAL  --  Sistema de Deteccion de Reclutamiento Criminal
echo   Hackathon 404: Threat Not Found  --  StartupLab MX + INL
echo ============================================================
echo.

REM ---- 1. Dependency checks --------------------------------------------------
echo [1/5] Verificando dependencias...
where python >nul 2>nul
if errorlevel 1 (
  echo   [ERROR] Python no encontrado en PATH. Instala Python 3.11+.
  pause & exit /b 1
)
where node >nul 2>nul
if errorlevel 1 (
  echo   [WARN]  Node.js no encontrado. El bot WhatsApp no podra ejecutarse.
)
if not exist "backend\requirements.txt" (
  echo   [ERROR] No estas en la raiz del repo nahual\.
  pause & exit /b 1
)

python -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo   Instalando dependencias del backend...
  python -m pip install -q -r backend\requirements.txt
)
echo   OK: python, fastapi, uvicorn

REM ---- 2. .env check ---------------------------------------------------------
echo [2/5] Verificando .env...
if not exist ".env" (
  echo   No existe .env -- copiando desde .env.example
  copy /Y ".env.example" ".env" >nul
)
echo   OK: .env presente

REM ---- 3. Sembrar datos demo (idempotente) -----------------------------------
echo [3/5] Sembrando datos demo si la base esta vacia...
python -c "import sqlite3, os; p='backend/nahual.db'; n=0 if not os.path.exists(p) else sqlite3.connect(p).execute('select count(*) from alerts').fetchone()[0]; raise SystemExit(0 if n>0 else 1)" >nul 2>nul
if errorlevel 1 (
  python scripts\seed_test_data.py >nul 2>nul
  echo   OK: datos demo sembrados
) else (
  echo   OK: ya hay alertas en la base, no se sembro
)

REM ---- 4. Levantar servicios -------------------------------------------------
echo [4/5] Levantando backend + panel en ventanas separadas...
start "NAHUAL Backend" cmd /k "cd /d %~dp0backend && set PYTHONIOENCODING=utf-8 && python -m uvicorn main:app --port 8000"
timeout /t 4 /nobreak >nul
start "NAHUAL Panel"   cmd /k "cd /d %~dp0panel   && python -m http.server 3000"
timeout /t 2 /nobreak >nul

REM ---- 5. Abrir navegador ----------------------------------------------------
echo [5/5] Abriendo navegador...
start "" "http://localhost:3000"
timeout /t 1 /nobreak >nul
start "" "http://localhost:8000/docs"

echo.
echo ============================================================
echo   Backend:    http://localhost:8000      Swagger: /docs
echo   Panel:      http://localhost:3000
echo   Health:     http://localhost:8000/health
echo.
echo   Bot WhatsApp:    cd bot ^&^& node index.js     (escanea QR)
echo   Demo sin WA:     cd bot ^&^& node simulate.js
echo   Demo en vivo:    python scripts\demo_live.py
echo ============================================================
echo.
echo Cierra las ventanas "NAHUAL Backend" y "NAHUAL Panel" para detener.
pause
