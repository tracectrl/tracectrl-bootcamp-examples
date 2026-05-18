#!/bin/bash
# uv-based runner. Mirrors run_agents_workflow.sh but uses uv for the venv and installs.
# Requires uv: https://docs.astral.sh/uv/getting-started/installation/
set -e
SCRIPT_DIR="$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
    echo "error: uv not found on PATH. Install from https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

# Create venv if it doesn't exist (uv default is .venv)
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv "$SCRIPT_DIR/.venv"
fi

# Activate venv
source "$SCRIPT_DIR/.venv/bin/activate"

# Install packages (uv pip is a drop-in for pip, ~10x faster cold)
uv pip install --quiet "strands-agents[gemini]" strands-agents-tools
uv pip install --quiet tracectrl
uv pip install --quiet tracectrl-instrumentation-strands
uv pip install --quiet google-cloud-aiplatform

# Load env vars
set -a
source "$SCRIPT_DIR/.env"
set +a

python "$SCRIPT_DIR/agents_workflow.py"
