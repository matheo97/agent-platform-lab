from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .llm import OllamaClient
from .tools import ToolRegistry
from .tracing import Tracer, Transcript

SYSTEM_PROMPT = """You are a careful platform agent inside a local harness.

Rules:
- Use the provided function/tools via native tool calls only.
- Never print tool calls as markdown or JSON in your assistant text.
- Call ONE tool per turn, then wait for the tool result.
- After the task is fully done, respond with a short final answer and no tool call.
- File paths are relative to the workspace. Shell is restricted to an allowlist.
"""

_TOOL_JSON_RE = re.compile(
    r"\{[^{}]*\"name\"\s*:\s*\"([a-zA-Z0-9_]+)\"\s*,\s*\"parameters\"\s*:\s*(\{[^{}]*\})[^{}]*\}",
    re.DOTALL,
)


@dataclass
class RunResult:
    final_text: str
    steps: int
    transcript_path: str
    spans: list[dict[str, Any]]


def _normalize_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    calls = message.get("tool_calls") or []
    normalized: list[dict[str, Any]] = []
    for call in calls:
        fn = call.get("function") or {}
        name = fn.get("name") or call.get("name")
        raw_args = fn.get("arguments", call.get("arguments", {}))
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args) if raw_args else {}
            except json.JSONDecodeError:
                args = {"_raw": raw_args}
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            args = {}
        normalized.append(
            {
                "id": call.get("id") or f"call_{len(normalized)}",
                "name": name,
                "arguments": args,
            }
        )
    return normalized


def _fallback_tool_calls_from_content(content: str) -> list[dict[str, Any]]:
    """Recover when a model prints tool intents as JSON instead of native tool_calls."""
    found: list[dict[str, Any]] = []
    for match in _TOOL_JSON_RE.finditer(content or ""):
        name = match.group(1)
        try:
            args = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        if not isinstance(args, dict):
            continue
        found.append({"id": f"fallback_{len(found)}", "name": name, "arguments": args})
    return found


def run_agent(
    goal: str,
    *,
    client: OllamaClient,
    tools: ToolRegistry,
    transcript: Transcript,
    tracer: Tracer,
    max_steps: int = 12,
) -> RunResult:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    transcript.write({"type": "goal", "goal": goal, "model": client.model})

    final_text = ""
    steps = 0
    content = ""

    for step in range(1, max_steps + 1):
        steps = step
        span = tracer.start("llm.chat", step=step)
        try:
            response = client.chat(messages, tools=tools.schemas())
            tracer.end(span, latency_ms=response.latency_ms)
        except Exception as exc:  # noqa: BLE001
            tracer.end(span, error=str(exc))
            transcript.write({"type": "error", "step": step, "error": str(exc)})
            raise

        message = response.message
        content = message.get("content") or ""
        tool_calls = _normalize_tool_calls(message)
        used_fallback = False
        if not tool_calls:
            tool_calls = _fallback_tool_calls_from_content(content)
            used_fallback = bool(tool_calls)

        transcript.write(
            {
                "type": "llm",
                "step": step,
                "latency_ms": response.latency_ms,
                "content": content,
                "tool_calls": tool_calls,
                "fallback_parsed": used_fallback,
            }
        )

        if not tool_calls:
            assistant_msg: dict[str, Any] = {"role": "assistant", "content": content}
            messages.append(assistant_msg)
            final_text = content.strip() or "(no final content)"
            break

        # Prefer one tool per turn for smaller local models.
        call = tool_calls[0]
        name = call["name"] or ""
        args = call["arguments"]

        if message.get("tool_calls"):
            native = message["tool_calls"]
            assistant_msg = {
                "role": "assistant",
                "content": content or "",
                "tool_calls": native[:1] if isinstance(native, list) else native,
            }
        else:
            assistant_msg = {
                "role": "assistant",
                "content": content or "",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {"name": name, "arguments": args},
                    }
                ],
            }
        messages.append(assistant_msg)

        tspan = tracer.start("tool.call", step=step, tool=name)
        result = tools.call(name, args)
        tracer.end(tspan, result_chars=len(result))
        transcript.write(
            {
                "type": "tool",
                "step": step,
                "tool": name,
                "arguments": args,
                "result": result,
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_name": name,
                "content": result,
            }
        )
    else:
        final_text = content.strip() if content else f"(stopped after {max_steps} steps)"

    transcript.write({"type": "final", "steps": steps, "final_text": final_text})
    return RunResult(
        final_text=final_text,
        steps=steps,
        transcript_path=str(transcript.path),
        spans=tracer.as_dicts(),
    )
