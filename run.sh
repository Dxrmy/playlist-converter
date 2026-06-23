#!/bin/bash
set -e

# honestly python venvs are annoying but it keeps the system clean


echo "=== Playlist Converter Setup ==="
echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed. Go install it first!"
    exit 1
fi

APP_DIR="$HOME/.local/share/PlaylistConverter"
mkdir -p "$APP_DIR"
VENV_PATH="$APP_DIR/.venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Setting up environment..."
    python3 -m venv "$VENV_PATH"
    echo "Installing dependencies..."
    # shhh pip dont tell me to upgrade
    "$VENV_PATH/bin/pip" install spotapi ytmusicapi requests pymongo redis websockets rich --quiet --disable-pip-version-check
fi

echo "Downloading converter..."
curl -sO https://raw.githubusercontent.com/Dxrmy/playlist-converter/b16da8d9637452cddeb67555da9c17743010a733/converter.py

echo "Running converter..."
set +e
"$VENV_PATH/bin/python" converter.py
set -e

echo "Cleaning up..."
rm -f converter.py
echo "Done!"
