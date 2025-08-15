# AI Recruitment Management Server Startup Script
Write-Host "Starting AI Recruitment Management Server..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Server may not work properly." -ForegroundColor Yellow
    Write-Host ""
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "Error: main.py not found in current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting server on http://localhost:8010" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    python main.py
} catch {
    Write-Host "Server stopped with error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Server stopped. Press Enter to exit..." -ForegroundColor Green
Read-Host
