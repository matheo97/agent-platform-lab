from __future__ import annotations

import json
import shlex
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ToolFn = Callable[[dict[str, Any]], str]


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: ToolFn

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


ALLOWED_SHELL = frozenset({"ls", "pwd", "echo", "wc", "cat", "head", "tail", "uname"})


class ToolRegistry:
    def __init__(self, workspace: Path, shell_timeout_s: float = 5.0, http_timeout_s: float = 10.0):
        self.workspace = workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.shell_timeout_s = shell_timeout_s
        self.http_timeout_s = http_timeout_s
        self._tools: dict[str, Tool] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            Tool(
                name="list_dir",
                description="List files in a directory under the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path inside workspace. Use '.' for root.",
                        }
                    },
                    "required": ["path"],
                },
                fn=self._list_dir,
            )
        )
        self.register(
            Tool(
                name="read_file",
                description="Read a UTF-8 text file under the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path inside workspace."}
                    },
                    "required": ["path"],
                },
                fn=self._read_file,
            )
        )
        self.register(
            Tool(
                name="write_file",
                description="Write UTF-8 text to a file under the workspace (creates parents).",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
                fn=self._write_file,
            )
        )
        self.register(
            Tool(
                name="http_get",
                description="HTTP GET a URL and return status + truncated body text.",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "max_bytes": {"type": "integer", "description": "Max response bytes (default 4000)."},
                    },
                    "required": ["url"],
                },
                fn=self._http_get,
            )
        )
        self.register(
            Tool(
                name="run_shell",
                description=(
                    "Run a restricted shell command. Only these binaries are allowed as argv[0]: "
                    + ", ".join(sorted(ALLOWED_SHELL))
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Simple command string, e.g. 'ls -la' or 'wc -l notes.txt'.",
                        }
                    },
                    "required": ["command"],
                },
                fn=self._run_shell,
            )
        )

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]

    def call(self, name: str, arguments: dict[str, Any] | str) -> str:
        if name not in self._tools:
            return json.dumps({"error": f"unknown tool: {name}"})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments else {}
            except json.JSONDecodeError:
                return json.dumps({"error": "arguments must be JSON object", "raw": arguments})
        if not isinstance(arguments, dict):
            return json.dumps({"error": "arguments must be an object"})
        try:
            return self._tools[name].fn(arguments)
        except Exception as exc:  # noqa: BLE001 - surface to agent loop
            return json.dumps({"error": str(exc), "type": type(exc).__name__})

    def _safe_path(self, rel: str) -> Path:
        if not rel or rel.strip() == "":
            raise ValueError("path is required")
        candidate = (self.workspace / rel).resolve()
        if not str(candidate).startswith(str(self.workspace)):
            raise PermissionError(f"path escapes workspace: {rel}")
        return candidate

    def _list_dir(self, args: dict[str, Any]) -> str:
        path = self._safe_path(str(args.get("path", ".")))
        if not path.exists():
            return json.dumps({"error": "not found", "path": str(path.relative_to(self.workspace))})
        if not path.is_dir():
            return json.dumps({"error": "not a directory", "path": str(path.relative_to(self.workspace))})
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in path.iterdir())
        return json.dumps({"path": str(path.relative_to(self.workspace)), "entries": entries})

    def _read_file(self, args: dict[str, Any]) -> str:
        path = self._safe_path(str(args["path"]))
        if not path.is_file():
            return json.dumps({"error": "not a file", "path": str(args["path"])})
        text = path.read_text(encoding="utf-8")
        if len(text) > 20_000:
            text = text[:20_000] + "\n...[truncated]..."
        return json.dumps({"path": str(args["path"]), "content": text})

    def _write_file(self, args: dict[str, Any]) -> str:
        path = self._safe_path(str(args["path"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        content = str(args.get("content", ""))
        path.write_text(content, encoding="utf-8")
        return json.dumps({"ok": True, "path": str(args["path"]), "bytes": len(content.encode("utf-8"))})

    def _http_get(self, args: dict[str, Any]) -> str:
        url = str(args["url"])
        if not (url.startswith("http://") or url.startswith("https://")):
            return json.dumps({"error": "url must start with http:// or https://"})
        max_bytes = int(args.get("max_bytes") or 4000)
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "agent-platform-lab/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=self.http_timeout_s) as resp:
                raw = resp.read(max_bytes + 1)
                truncated = len(raw) > max_bytes
                body = raw[:max_bytes].decode("utf-8", errors="replace")
                return json.dumps(
                    {
                        "status": getattr(resp, "status", None),
                        "url": url,
                        "truncated": truncated,
                        "body": body,
                    }
                )
        except urllib.error.HTTPError as exc:
            return json.dumps({"error": str(exc), "status": exc.code, "url": url})
        except urllib.error.URLError as exc:
            return json.dumps({"error": str(exc.reason), "url": url})

    def _run_shell(self, args: dict[str, Any]) -> str:
        command = str(args.get("command", "")).strip()
        if not command:
            return json.dumps({"error": "command is required"})
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            return json.dumps({"error": f"could not parse command: {exc}"})
        if not argv:
            return json.dumps({"error": "empty command"})
        binary = Path(argv[0]).name
        if binary not in ALLOWED_SHELL:
            return json.dumps(
                {
                    "error": "command not allowed",
                    "binary": binary,
                    "allowed": sorted(ALLOWED_SHELL),
                }
            )
        # Force relative paths to resolve under workspace by cwd
        try:
            completed = subprocess.run(
                argv,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=self.shell_timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return json.dumps({"error": "timeout", "timeout_s": self.shell_timeout_s})
        return json.dumps(
            {
                "argv": argv,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-2000:],
            }
        )
