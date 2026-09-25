#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
PYTHON="${PYTHON:-/opt/homebrew/bin/python3}"
exec "$PYTHON" -m agent_harness "$@"
