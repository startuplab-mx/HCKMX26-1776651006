@echo off
REM Nahual demo launcher (Windows). Opens 3 windows: backend, panel, bot.
REM Pre-req: backend deps installed (pip install -r backend/requirements.txt)
REM           bot deps installed (cd bot && npm install)

echo === NAHUAL — demo launcher ===

start "Nahual Backend" cmd /k "cd /d %~dp0backend && set PYTHONIOENCODING=utf-8 && python -m uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak >nul

start "Nahual Panel" cmd /k "cd /d %~dp0panel && python -m http.server 3000"
timeout /t 1 /nobreak >nul

echo.
echo Backend: http://localhost:8000/docs
echo Panel:   http://localhost:3000
echo.
echo Para ejecutar el bot:        cd bot ^&^& node index.js
echo Para simulacion sin WA:      cd bot ^&^& node simulate.js
echo Para sembrar datos demo:     python scripts/seed_test_data.py
echo.
pause
