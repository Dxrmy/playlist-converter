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
pip install spotapi ytmusicapi requests --quiet

Write-Host "Downloading converter..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Dxrmy/playlist-converter/main/converter.py" -OutFile "converter.py"

Write-Host "Running converter..."
python converter.py

Write-Host "Cleaning up..."
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force .venv
}
if (Test-Path "converter.py") {
    Remove-Item -Force converter.py
}
Write-Host "Done!"
