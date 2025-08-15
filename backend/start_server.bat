@echo off
echo Starting AI Recruitment Management Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Server may not work properly.
    echo.
)

REM Start the server
echo Starting server on http://localhost:8010
echo Press Ctrl+C to stop the server
echo.
python main.py

REM If server exits, wait for user input
echo.
echo Server stopped. Press any key to exit...
pause >nul
