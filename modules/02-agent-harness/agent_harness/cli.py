from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .llm import OllamaClient
from .loop import run_agent
from .tools import ToolRegistry
from .tracing import Tracer, Transcript

MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE = MODULE_ROOT / "workspace"
DEFAULT_RUNS = MODULE_ROOT / "runs"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-harness",
        description="Local agent harness (Ollama + typed tools + JSONL transcript).",
    )
    p.add_argument("goal", nargs="?", help="Task for the agent. If omitted, runs the demo goal.")
    p.add_argument("--model", default="llama3.1:8b", help="Ollama model tag")
    p.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    p.add_argument("--max-steps", type=int, default=12)
    p.add_argument("--demo", action="store_true", help="Run the built-in multi-tool demo goal")
    return p


DEMO_GOAL = """Do these steps using tools (one tool per turn):
1. write_file path=notes/hello.txt content=hello from harness
2. read_file path=notes/hello.txt
3. http_get url=https://example.com
4. run_shell command=ls notes
When finished, reply with exactly 3 short bullets summarizing the results (include the HTTP status).
"""


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    goal = DEMO_GOAL if args.demo or not args.goal else args.goal

    runs_dir = DEFAULT_RUNS
    runs_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    transcript_path = runs_dir / f"run-{stamp}.jsonl"

    client = OllamaClient(model=args.model)
    tools = ToolRegistry(workspace=args.workspace)
    tracer = Tracer()
    transcript = Transcript(transcript_path)

    print(f"model={args.model}")
    print(f"workspace={args.workspace.resolve()}")
    print(f"transcript={transcript_path}")
    print("---")

    try:
        result = run_agent(
            goal,
            client=client,
            tools=tools,
            transcript=transcript,
            tracer=tracer,
            max_steps=args.max_steps,
        )
    finally:
        transcript.close()

    print(result.final_text)
    print("---")
    print(json.dumps({"steps": result.steps, "transcript": result.transcript_path}, indent=2))
    spans_path = transcript_path.with_suffix(".spans.json")
    spans_path.write_text(json.dumps(result.spans, indent=2), encoding="utf-8")
    print(f"spans={spans_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
