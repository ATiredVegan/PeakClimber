#!/usr/bin/env bash
# One-time setup for PeakClimber: creates a virtual environment in .venv
# and installs the required packages into it.
#
# Usage:  bash setup.sh
# To use a specific Python:  PYTHON=python3.13 bash setup.sh

set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

# Check that Python exists and is new enough
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Error: '$PYTHON' not found. Install Python 3.10 or newer from python.org."
    exit 1
fi

if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "Error: PeakClimber needs Python 3.10 or newer. Found: $("$PYTHON" --version)"
    exit 1
fi

# The GUI needs tkinter, which some Python installs (e.g. Homebrew) ship separately
if ! "$PYTHON" -c 'import tkinter' >/dev/null 2>&1; then
    echo "Error: this Python is missing tkinter, which the PeakClimber window needs."
    echo "  Homebrew users: brew install python-tk@$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    echo "  Or install Python from python.org, which includes tkinter."
    exit 1
fi

echo "Creating virtual environment with $("$PYTHON" --version)..."
"$PYTHON" -m venv .venv

echo "Installing packages..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

chmod +x run_peakclimber.command 2>/dev/null || true
xattr -d com.apple.quarantine run_peakclimber.command 2>/dev/null || true

echo ""
echo "Setup complete. To start PeakClimber, run:  bash run_peakclimber.command"
echo "(On a Mac you can also double-click run_peakclimber.command in Finder.)"
