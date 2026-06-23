#!/bin/bash
set -e

echo "=== Playlist Converter Setup ==="
echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is required but not installed."
    exit 1
fi

echo "Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install spotapi ytmusicapi requests --quiet

echo "Downloading converter..."
curl -sO https://raw.githubusercontent.com/Dxrmy/playlist-converter/main/converter.py

echo "Running converter..."
python3 converter.py

echo "Cleaning up..."
rm -rf .venv
rm -f converter.py
echo "Done!"
