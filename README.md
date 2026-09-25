# Agent Platform Lab

**Building-in-public portfolio** for AI platform engineering: agent harnesses, evaluation, sandboxes, MCP tooling, event-driven workers (Kafka-compatible), and multi-agent discovery teams.

> Not a chatbot / RAG demo. The goal is production-shaped **agent infrastructure** you can clone, run locally (Mac + Ollama), and inspect.

**Author:** [Mateo Salazar](https://github.com/matheo97) · LATAM remote · overlap with US Pacific

---

## What this demonstrates

| Claim (job-relevant) | Where to look |
|---|---|
| Agent harness / orchestration | [`modules/02-agent-harness`](modules/02-agent-harness) |
| Evaluation frameworks | [`modules/04-evals`](modules/04-evals) |
| Tool sandboxes | [`modules/05-sandbox`](modules/05-sandbox) |
| MCP + skills / hooks / commands | [`modules/03-mcp-skills`](modules/03-mcp-skills) |
| Agent teams (discovery) | [`modules/08-agent-teams`](modules/08-agent-teams) |
| Kafka-compatible event pipeline | [`modules/06-kafka-pipeline`](modules/06-kafka-pipeline) |
| Terraform / AWS-shaped infra | [`modules/07-terraform-aws`](modules/07-terraform-aws) |
| Local open models on Apple Silicon | [`modules/01-local-runtime`](modules/01-local-runtime) |
| Obsidian ↔ agents bridge | [`modules/09-obsidian-bridge`](modules/09-obsidian-bridge) |

---

## Module status

| # | Module | Status | Portfolio pin? |
|---|---|---|---|
| 01 | [local-runtime](modules/01-local-runtime) | **done** (smoke PASS) | — |
| 02 | [agent-harness](modules/02-agent-harness) | **done** (demo PASS) | **PIN #1** |
| 03 | [mcp-skills](modules/03-mcp-skills) | planned | spotlight optional |
| 04 | [evals](modules/04-evals) | planned | **PIN #2** |
| 05 | [sandbox](modules/05-sandbox) | planned | — |
| 06 | [kafka-pipeline](modules/06-kafka-pipeline) | planned | — |
| 07 | [terraform-aws](modules/07-terraform-aws) | planned | — |
| 08 | [agent-teams](modules/08-agent-teams) | planned | **PIN #3** |
| 09 | [obsidian-bridge](modules/09-obsidian-bridge) | planned | — |

Roadmap + Definition of Done per theme: [`docs/ROADMAP.md`](docs/ROADMAP.md)

---

## Stack (local / free-first)

- **Python 3.12+**, Docker Compose
- **Ollama** on Apple Silicon (M4 Pro 24 GB target)
- **Redpanda** (Kafka API) for streaming modules
- **Terraform + LocalStack** for infra modules (avoid surprise cloud bills)
- No paid API required for the core path

---

## Quickstart (today)

```bash
git clone https://github.com/matheo97/agent-platform-lab.git
cd agent-platform-lab

# Theme 01 — local runtime
./modules/01-local-runtime/scripts/smoke.sh

# Theme 02 — agent harness (PIN #1)
cd modules/02-agent-harness && ./run.sh --demo
```

If Ollama is not installed yet:

```bash
brew install ollama
brew services start ollama
ollama pull llama3.1:8b
```

---

## Cadence

~7 hours/week. Each theme is **2–4 weeks** and ends only when the module DoD is met (code + English README + demo artifact pushed). Incomplete themes get **scope cut**, not endless extension.

---

## License

MIT — see [LICENSE](LICENSE)
