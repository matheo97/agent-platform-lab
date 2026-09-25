# 02 — Agent harness

## Problem

Most “AI demos” hide the agent loop. Platform roles care about the **harness**: tool schemas, timeouts/policies, auditable transcripts, and a stop condition you can reason about.

## What this proves

- A real agent loop: **plan → tool → observe → stop**
- Typed tools: filesystem (workspace-scoped), HTTP GET, restricted shell allowlist
- JSONL transcripts + minimal span tracing for every LLM/tool step
- Runs fully local on **Ollama** (`llama3.1:8b`) with **stdlib-only** Python

## Architecture

```
CLI ──► Agent loop ──► Ollama /api/chat (tools)
              │
              ├── ToolRegistry (list/read/write/http/shell)
              ├── Transcript (runs/*.jsonl)
              └── Tracer (runs/*.spans.json)
```

## Quickstart

Requires Theme 01 (Ollama running + a model):

```bash
brew services start ollama
ollama pull llama3.1:8b

cd modules/02-agent-harness
./run.sh --demo
```

Custom goal:

```bash
./run.sh "Create workspace/report.txt with the text ready and then read it back"
```

Uses `/opt/homebrew/bin/python3` by default (`PYTHON=...` to override). No pip install required.

## Demo evidence

See [`../../demos/02-agent-harness-sample-run.md`](../../demos/02-agent-harness-sample-run.md).

Verified locally: write_file → read_file → http_get(example.com → 200) → run_shell(`ls notes`) → final summary (5 steps).

## Design decisions

1. **Own harness, not LangGraph/Crew** — ownership and clarity for portfolio interviews.
2. **One tool per turn** — more reliable with 8B local models.
3. **Workspace sandbox for files + shell allowlist** — policy before full Docker sandbox (Theme 05).
4. **Fallback JSON parser** — if a model prints tool intents as text, the harness still recovers (logged as `fallback_parsed`).

## Failure we hit / fix

First demo: the model listed tools in prose instead of native `tool_calls`. Fix: stricter system prompt (“one tool per turn”, “no JSON in text”) + content fallback parser. After the prompt change, `llama3.1:8b` used native tool calls for the full demo.

## Status

**Done** for Theme 02 core DoD (CLI + 3 tool classes + transcript + demo write-up).
