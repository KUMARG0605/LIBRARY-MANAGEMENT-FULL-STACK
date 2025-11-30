# Library Management System - Run Script

Write-Host "Starting Library Management System..." -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found! Run setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚠ .env file not found! Copying from .env.example" -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Run the application
Write-Host "`nStarting Flask application..." -ForegroundColor Yellow
Write-Host "Visit: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python app_new.py
