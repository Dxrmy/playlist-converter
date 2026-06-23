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

echo "Installing dependencies..."
./.venv/bin/pip install spotapi ytmusicapi requests pymongo redis websockets --quiet

echo "Downloading converter..."
curl -sO https://raw.githubusercontent.com/Dxrmy/playlist-converter/cde7d6c5aa9ef3b4211dc44d358d7b1a0629373c/converter.py

echo "Running converter..."
set +e
./.venv/bin/python converter.py
set -e

echo "Cleaning up..."
rm -rf .venv
rm -f converter.py
echo "Done!"
