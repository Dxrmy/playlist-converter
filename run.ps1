$ErrorActionPreference = 'Stop'

Write-Host "=== Playlist Converter Setup ==="
Write-Host "Checking for Python..."
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is required but not installed." -ForegroundColor Red
    exit 1
}

Write-Host "Setting up virtual environment..."
python -m venv .venv
$activate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
    & $activate
}

Write-Host "Installing dependencies..."
pip install -r requirements.txt --quiet

Write-Host "Running converter..."
python converter.py
