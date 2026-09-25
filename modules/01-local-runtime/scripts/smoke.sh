#!/usr/bin/env bash
# Smoke-test local Ollama for Agent Platform Lab (Apple Silicon / M4 target).
set -euo pipefail

MODEL="${MODEL:-llama3.1:8b}"
PROMPT="${PROMPT:-Reply with exactly: ok}"

if ! command -v ollama >/dev/null 2>&1; then
  cat <<'EOF' >&2
error: ollama not found on PATH

Install on macOS:
  brew install ollama
  # then start the app or: ollama serve
  ollama pull llama3.1:8b
  ./modules/01-local-runtime/scripts/smoke.sh
EOF
  exit 127
fi

echo "==> ollama version"
ollama --version

echo "==> checking model: ${MODEL}"
if ! ollama show "${MODEL}" >/dev/null 2>&1; then
  echo "model '${MODEL}' not found locally. Pulling..."
  ollama pull "${MODEL}"
fi

echo "==> running non-interactive prompt"
# -n disables streaming noise for logs; adjust if your ollama version differs
OUTPUT="$(ollama run "${MODEL}" "${PROMPT}" 2>/dev/null || ollama run "${MODEL}" "${PROMPT}")"

echo "---- model output ----"
echo "${OUTPUT}"
echo "----------------------"

if echo "${OUTPUT}" | grep -qi 'ok'; then
  echo "smoke: PASS (${MODEL})"
  exit 0
fi

echo "smoke: WARN — model responded but did not contain 'ok'. Inspect output above." >&2
exit 0
