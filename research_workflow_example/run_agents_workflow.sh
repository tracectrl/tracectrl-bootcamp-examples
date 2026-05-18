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
pip install --quiet tracectrl
pip install --quiet tracectrl-instrumentation-strands
pip install --quiet google-cloud-aiplatform

# Load env vars
set -a
source "$SCRIPT_DIR/.env"
set +a

python "$SCRIPT_DIR/agents_workflow.py"
