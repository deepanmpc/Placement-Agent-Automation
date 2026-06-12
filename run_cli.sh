#!/bin/bash
# run_cli.sh - Starts the COWORK Agent E.D.I.T.H. Runtime

# Go to the project root
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the CLI
PYTHONPATH=. python3 cli.py
