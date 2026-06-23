$ErrorActionPreference = 'Stop'

Write-Host "=== Playlist Converter Setup ==="
Write-Host "Checking for Python..."
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is required but not installed." -ForegroundColor Red
    exit 1
}

$AppDir = Join-Path $env:LOCALAPPDATA "PlaylistConverter"
if (-not (Test-Path $AppDir)) { New-Item -ItemType Directory -Path $AppDir | Out-Null }
$VenvPath = Join-Path $AppDir ".venv"

if (-not (Test-Path $VenvPath)) {
    Write-Host "Setting up environment..."
    python -m venv $VenvPath
    Write-Host "Installing dependencies..."
    & (Join-Path $VenvPath "Scripts\pip.exe") install spotapi ytmusicapi requests pymongo redis websockets rich --quiet --disable-pip-version-check
}

Write-Host "Downloading converter..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Dxrmy/playlist-converter/d5bec2eba2a2bcb0f04ecb693f18f66b0a11ab64/converter.py" -OutFile "converter.py"

Write-Host "Running converter..."
try {
    & (Join-Path $VenvPath "Scripts\python.exe") converter.py
} finally {
    Write-Host "Cleaning up..."
    if (Test-Path "converter.py") {
        Remove-Item -Force converter.py -ErrorAction SilentlyContinue
    }
    Write-Host "Done!"
}
