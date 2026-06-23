$ErrorActionPreference = 'Stop'

# honestly python on windows is a nightmare so we're just making a venv in localappdata
Write-Host "=== Playlist Converter Setup ==="
Write-Host "Checking for Python..."
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is required but not installed. Go install it first!" -ForegroundColor Red
    exit 1
}

$AppDir = Join-Path $env:LOCALAPPDATA "PlaylistConverter"
if (-not (Test-Path $AppDir)) { New-Item -ItemType Directory -Path $AppDir | Out-Null }
$VenvPath = Join-Path $AppDir ".venv"

if (-not (Test-Path $VenvPath)) {
    Write-Host "Setting up environment..."
    python -m venv $VenvPath
    Write-Host "Installing dependencies..."
    # shhh pip dont tell me to upgrade
    & (Join-Path $VenvPath "Scripts\pip.exe") install spotapi ytmusicapi requests pymongo redis websockets rich --quiet --disable-pip-version-check
}

Write-Host "Downloading converter..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Dxrmy/playlist-converter/b16da8d9637452cddeb67555da9c17743010a733/converter.py" -OutFile "converter.py"

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
