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
pip install -r requirements.txt --quiet

echo "Running converter..."
python3 converter.py
