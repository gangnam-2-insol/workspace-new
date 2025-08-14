# AI Recruitment Management Server Startup Script
param(
    [switch]$NonInteractive
)

Write-Host "Starting AI Recruitment Management Server..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    if (-not $NonInteractive) { Read-Host "Press Enter to exit" }
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
    if (-not $NonInteractive) { Read-Host "Press Enter to exit" }
    exit 1
}

Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    if ($NonInteractive) {
        # 비대화식: 백그라운드 + 로그 리다이렉트
        Start-Process -FilePath python -ArgumentList '-u','main.py' -RedirectStandardOutput 'server.log' -RedirectStandardError 'server_error.log' -WindowStyle Hidden | Out-Null
    } else {
        python main.py
    }
} catch {
    Write-Host "Server stopped with error: $_" -ForegroundColor Red
}

if (-not $NonInteractive) {
    Write-Host ""
    Write-Host "Server stopped. Press Enter to exit..." -ForegroundColor Green
    Read-Host
}
