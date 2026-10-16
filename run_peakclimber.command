#!/usr/bin/env bash
# Starts PeakClimber using the virtual environment created by setup.sh.
# On macOS this file can be double-clicked in Finder.

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "PeakClimber isn't set up yet. Run this first:  bash setup.sh"
    exit 1
fi

exec .venv/bin/python gui_main.py
