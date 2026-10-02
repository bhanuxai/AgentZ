@echo off
TITLE AgentZ — AI Personal Device Agent (Laptop & Android)
color 0B

echo =======================================================================
echo          AgentZ — Autonomous AI Personal Device Agent
echo          "Tell me what you want. I'll handle the steps."
echo =======================================================================
echo.
echo [1/3] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.9+.
    pause
    exit /b 1
)

echo [2/3] Checking AgentZ Backend Service (Port 8081)...
netstat -ano | findstr :8081 >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting AgentZ Backend Server on http://localhost:8081 ...
    start "AgentZ Backend Server" /min python -m uvicorn main:app --app-dir "%~dp0backend" --host 0.0.0.0 --port 8081
    timeout /t 2 /nobreak >nul
) else (
    echo AgentZ Backend Server is already active on port 8081.
)

echo [3/3] Launching AgentZ Web Interface in your browser...
start http://localhost:8081/

echo.
echo =======================================================================
echo AgentZ is ready!
echo URL: http://localhost:8081/
echo.
echo You can give commands like:
echo   - "Check laptop battery and CPU stats"
echo   - "Open Notepad and save meeting notes"
echo   - "Search latest AI news on Google"
echo   - "Take a screenshot of my laptop screen"
echo   - "Book me a Rapido from my current location to LPU"
echo   - "Open Calculator"
echo =======================================================================
echo.
pause
