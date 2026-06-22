@echo off
REM ===========================================================================
REM  22PM — Launch Script (Windows)
REM  Activates backend AI engine + opens frontend interface.
REM  Cost: $0 (all free-tier tools)
REM ===========================================================================
TITLE 22PM AI Engine

cd /d "%~dp0"

echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║           22PM — AI Workflow Engine                 ║
echo  ║     Zero Capital · Infinite Ambition                 ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
echo  [INFO] Starting 22PM services...
echo  [INFO] All costs: $0 (free-tier LLMs)
echo.

REM === Check Python ===
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)
echo  [✓] Python detected

REM === Install dependencies ===
if not exist "engine\venv" (
    echo  [INFO] Creating virtual environment...
    python -m venv engine\venv
)

echo  [INFO] Installing dependencies...
call engine\venv\Scripts\python.exe -m pip install -q -r "engine\requirements.txt" 2>nul

REM === Check/Create .env ===
if not exist "engine\.env" (
    echo  [INFO] Creating .env from template...
    copy engine\.env.template engine\.env >nul
    echo  [WARN] Edit engine\.env to add your API keys:
    echo         GEMINI_API_KEY (60 req/min free)
    echo         GROQ_API_KEY (30 req/min free)
    echo.
    echo  Get keys at:
    echo    Gemini: https://aistudio.google.com/app/apikey
    echo    Groq:   https://console.groq.com
    echo.
)

REM === Check logo ===
if not exist "22pmlogo24.png" (
    echo  [INFO] Logo not found. Skipping logo copy.
)

echo.
echo  [INFO] Starting backend AI engine...
echo.

REM === Start backend ===
start "22PM Engine" cmd /c "cd engine && ..\engine\venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM === Wait for server ===
echo  [INFO] Waiting for server to start...
timeout /t 3 /nobreak >nul

REM === Open frontend ===
echo  [INFO] Opening web interface...
start "" "index.html"

REM === Open API docs ===
echo  [INFO] Opening API documentation...
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/docs"

echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║                  ALL SYSTEMS ACTIVE                  ║
echo  ╠═══════════════════════════════════════════════════════╣
echo  ║  Web Interface: index.html                          ║
echo  ║  API Server:    http://localhost:8000               ║
echo  ║  API Docs:      http://localhost:8000/docs          ║
echo  ║  Health Check:  http://localhost:8000/health        ║
echo  ╠═══════════════════════════════════════════════════════╣
echo  ║  Providers: Gemini 60rpm / Groq 30rpm (auto-fallback)║
echo  ║  Cost: $0 (free tiers)                               ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
echo  Press any key to stop the server...
echo.
pause >nul

REM === Cleanup ===
echo  [INFO] Shutting down 22PM...
taskkill /f /fi "WINDOWTITLE eq 22PM Engine" >nul 2>&1
echo  [✓] Services stopped.
echo.