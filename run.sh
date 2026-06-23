#!/bin/bash
set -e

echo "=== Playlist Converter Setup ==="
echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is required but not installed."
    exit 1
fi

APP_DIR="$HOME/.local/share/PlaylistConverter"
mkdir -p "$APP_DIR"
VENV_PATH="$APP_DIR/.venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Setting up environment..."
    python3 -m venv "$VENV_PATH"
    echo "Installing dependencies..."
    "$VENV_PATH/bin/pip" install spotapi ytmusicapi requests pymongo redis websockets --quiet --disable-pip-version-check
fi

echo "Downloading converter..."
curl -sO https://raw.githubusercontent.com/Dxrmy/playlist-converter/d5bec2eba2a2bcb0f04ecb693f18f66b0a11ab64/converter.py

echo "Running converter..."
set +e
"$VENV_PATH/bin/python" converter.py
set -e

echo "Cleaning up..."
rm -f converter.py
echo "Done!"
