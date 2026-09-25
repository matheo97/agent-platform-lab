# 01 — Local AI runtime

## Problem

Run open models locally on Apple Silicon (M4 Pro, 24 GB) without paid APIs, with a reproducible smoke check for the rest of the lab.

## What this proves

- Operates local LLMs (Ollama) as platform infrastructure, not a one-off chat UI
- Documents model → RAM / use trade-offs for a constrained laptop
- Gives every later module a stable `llm` dependency

## Architecture

```
smoke.sh ──► ollama list / show / run (non-interactive prompt)
                │
                └── models chosen for ≤24 GB unified memory
```

## Quickstart

```bash
# From repo root
brew install ollama   # if needed
ollama serve          # or open the Ollama app
ollama pull llama3.1:8b

./modules/01-local-runtime/scripts/smoke.sh
```

Optional stronger coding model (heavier):

```bash
ollama pull qwen2.5-coder:14b
MODEL=qwen2.5-coder:14b ./modules/01-local-runtime/scripts/smoke.sh
```

## Model guidance (M4 Pro 24 GB)

| Model | Approx. fit | Use |
|---|---|---|
| `llama3.1:8b` | Comfortable daily driver | General agent loop |
| `qwen2.5-coder:14b` | Tight but usable | Coding / tool-heavy agents |
| 32B+ Q4 | Risky / swap thrash | Avoid for daily harness work |

Numbers are approximate; verify with Activity Monitor while a prompt is running.

## Verified on this machine

| Check | Result |
|---|---|
| Install | Homebrew formula `ollama` 0.34.4 |
| Service | `brew services start ollama` → `127.0.0.1:11434` |
| Model | `llama3.1:8b` (~4.9 GB pull) |
| Smoke | **PASS** — prompt `"Reply with exactly: ok"` → `ok` |
| Wall time | ~**1.6 s** for the smoke prompt (warm path; first load after boot will be slower) |

Command used:

```bash
./modules/01-local-runtime/scripts/smoke.sh
```

## Design decisions

1. **Ollama over raw MLX first** — fewer moving parts for a portfolio quickstart; MLX can be a later ADR.
2. **Smoke script exits non-zero if Ollama is missing** — CI/local gates stay honest.
3. **No cloud fallback in this module** — keeps the free path clear.

## Status

**Done for Theme 01 DoD core** — install path + smoke + model table verified on M4. Optional follow-up: add `qwen2.5-coder:14b` smoke row when pulled.
