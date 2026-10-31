"""Общие структуры строки локализации и находки."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "info": 3}


@dataclass
class Entry:
    key: str
    source: str
    target: str
    locale: str
    context: str
    file: str
    notes: str = ""

    def blob(self) -> str:
        return " ".join(
            part for part in (self.key, self.context, self.source, self.notes) if part
        )


@dataclass
class Finding:
    file: str
    key: str
    locale: str
    context: str
    severity: str
    engine: str
    code: str
    message: str
    source: str
    target: str
    suggestion: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class AiMeta:
    mode: str
    prompt_version: str
    model: str = ""
    llm_called: int = 0
    silent_skipped: int = 0
    guardrail_dropped: int = 0
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class RunResult:
    entries: list[Entry]
    findings: list[Finding]
    ai: AiMeta

    def to_dict(self) -> dict[str, object]:
        return {
            "entries": len(self.entries),
            "findings": [item.to_dict() for item in self.findings],
            "ai": self.ai.to_dict(),
        }
