# Roadmap

Pace: **~7 h/week**. Each theme closes in **2–4 weeks** with a public GitHub artifact.

## Definition of Done (every theme)

- [ ] Code pushed to this public repo (tag optional: `tema-N-done`)
- [ ] Module `README.md` in English: Problem / Architecture / Quickstart / What this proves
- [ ] Demo: GIF, asciinema, or `demos/` sample output (no secrets)
- [ ] Short design notes (3 decisions + 1 failure/fix)
- [ ] Root README status table updated
- [ ] CV-ready link: `https://github.com/matheo97/agent-platform-lab/tree/main/modules/...`

## Themes

### 01 — Local AI runtime (2 weeks) — in progress

- Ollama on M4, 1–2 stable models, smoke script, RAM guidance
- **Artifact:** `modules/01-local-runtime`

### 02 — Agent harness (3–4 weeks) — PIN #1

- Agent loop, typed tools, timeouts, JSONL transcripts, minimal tracing
- **Artifact:** `modules/02-agent-harness` (+ optional spotlight repo later)

### 03 — MCP + Skills + Commands + Hooks (2–3 weeks)

- Python MCP server + repo skills/hooks patterns
- **Artifact:** `modules/03-mcp-skills`

### 04 — Evaluation framework (2–3 weeks) — PIN #2

- Dataset, metrics, `make eval`, before/after report in repo
- **Artifact:** `modules/04-evals`

### 05 — Sandboxes (2–3 weeks)

- Ephemeral Docker tool execution + allowlist policy + deny/allow demo
- **Artifact:** `modules/05-sandbox`

### 06 — Kafka / events (3–4 weeks)

- Redpanda topics, workers, DLQ, kill-worker reproof demo
- **Artifact:** `modules/06-kafka-pipeline`

### 07 — Terraform + AWS-shaped (3 weeks)

- TF modules + LocalStack (default) or tightly scoped Free Tier
- **Artifact:** `modules/07-terraform-aws`

### 08 — Agent Teams / discovery (3–4 weeks) — PIN #3

- Researcher / Critic / Synthesizer, persistent team state, sample backlog
- **Artifact:** `modules/08-agent-teams`

### 09 — Obsidian bridge (2 weeks)

- MCP/skill over **fixture vault only** (never personal notes)
- **Artifact:** `modules/09-obsidian-bridge`

## Priority if time is tight

1. Harness → 2. Evals → 3. Sandbox → 4. Agent Teams → 5. Kafka → then MCP / Terraform / Obsidian
