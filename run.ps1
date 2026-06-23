$ErrorActionPreference = 'Stop'

Write-Host "=== Playlist Converter Setup ==="
Write-Host "Checking for Python..."
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is required but not installed." -ForegroundColor Red
    exit 1
}

Write-Host "Setting up virtual environment..."
python -m venv .venv

Write-Host "Installing dependencies..."
.\.venv\Scripts\pip.exe install spotapi ytmusicapi requests pymongo redis websockets --quiet

Write-Host "Downloading converter..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Dxrmy/playlist-converter/cde7d6c5aa9ef3b4211dc44d358d7b1a0629373c/converter.py" -OutFile "converter.py"

Write-Host "Running converter..."
try {
    .\.venv\Scripts\python.exe converter.py
} finally {
    Write-Host "Cleaning up..."
    if (Test-Path ".venv") {
        Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
    }
    if (Test-Path "converter.py") {
        Remove-Item -Force converter.py -ErrorAction SilentlyContinue
    }
    Write-Host "Done!"
}
