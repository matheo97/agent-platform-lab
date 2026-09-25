# Demo: agent harness multi-tool run

**Model:** `llama3.1:8b` (Ollama)  
**Command:** `./run.sh --demo` from `modules/02-agent-harness`  
**Steps:** 5

## Tool sequence

1. `write_file` → `notes/hello.txt` = `hello from harness`
2. `read_file` → same content returned
3. `http_get` → `https://example.com` → status **200**
4. `run_shell` → `ls notes` → lists `hello.txt`
5. Final assistant summary (no tool call)

## Final answer (model)

```text
* A file named "hello.txt" was created with the content "hello from harness".
* The content of "hello.txt" is "hello from harness".
* The HTTP request to https://example.com was successful with a status code of 200.
```

## Transcript shape (abridged)

Each line in `runs/run-*.jsonl` is one event:

- `goal` — user task
- `llm` — model turn (`latency_ms`, `tool_calls`, `fallback_parsed`)
- `tool` — name, arguments, JSON result
- `final` — stop

Companion file: `runs/run-*.spans.json` with `llm.chat` / `tool.call` spans.

## Reproduce

```bash
cd modules/02-agent-harness
./run.sh --demo
```
