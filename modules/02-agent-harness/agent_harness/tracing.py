from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TextIO


@dataclass
class Span:
    name: str
    started_at: float
    ended_at: float | None = None
    attrs: dict[str, Any] | None = None
    error: str | None = None

    @property
    def duration_ms(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000


class Tracer:
    def __init__(self) -> None:
        self.spans: list[Span] = []

    def start(self, name: str, **attrs: Any) -> Span:
        span = Span(name=name, started_at=time.perf_counter(), attrs=attrs or None)
        self.spans.append(span)
        return span

    def end(self, span: Span, error: str | None = None, **attrs: Any) -> None:
        span.ended_at = time.perf_counter()
        span.error = error
        if attrs:
            span.attrs = {**(span.attrs or {}), **attrs}

    def as_dicts(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for span in self.spans:
            row = asdict(span)
            row["duration_ms"] = span.duration_ms
            out.append(row)
        return out


class Transcript:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: TextIO = self.path.open("w", encoding="utf-8")

    def write(self, event: dict[str, Any]) -> None:
        payload = {"ts": time.time(), **event}
        self._fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()
