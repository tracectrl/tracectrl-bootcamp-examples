#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate venv
source "$SCRIPT_DIR/venv/bin/activate"

# Install packages if not already installed
pip install --quiet "strands-agents[gemini]" strands-agents-tools
TRACECTRL_SDK="<TRACECTRL_SDK>"
pip install --quiet "$TRACECTRL_SDK/tracectrl"
pip install --quiet "$TRACECTRL_SDK/tracectrl-instrumentation-strands"

# Load env vars
set -a
source "$SCRIPT_DIR/.env"
set +a

python "$SCRIPT_DIR/teachers_assistant.py"
