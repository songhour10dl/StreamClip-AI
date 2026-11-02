@echo off
echo ========================================
echo  StreamClip AI - Application Launcher
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
echo [OK] Python detected

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js detected

echo.
echo Starting StreamClip AI...
echo.

REM Start backend in new window
echo [1/2] Starting Backend Server...
start "StreamClip AI - Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo [2/2] Starting Frontend...
start "StreamClip AI - Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo  StreamClip AI is starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:1420
echo.
echo Press any key to exit this launcher...
echo (Backend and Frontend will continue running)
pause >nul
