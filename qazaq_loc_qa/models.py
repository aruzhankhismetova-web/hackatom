"""Общие структуры данных локализационного бандла и находок QA."""

from __future__ import annotations

from dataclasses import dataclass, field


SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_PENALTY = {"critical": 15, "high": 6, "medium": 2, "low": 1}


@dataclass
class Segment:
    key: str
    texts: dict[str, str]
    context: str = ""
    source_file: str = ""

    def text(self, language: str) -> str | None:
        if language not in self.texts:
            return None
        return self.texts[language]


@dataclass
class Bundle:
    segments: list[Segment] = field(default_factory=list)
    source_language: str = "en"
    origin: str = ""

    def by_key(self) -> dict[str, Segment]:
        return {segment.key: segment for segment in self.segments}


@dataclass
class Finding:
    checker: str
    severity: str
    language: str
    key: str
    message: str
    source_text: str
    target_text: str
    suggestion: str = ""
    context: str = ""

    @property
    def finding_id(self) -> str:
        return f"{self.severity}:{self.checker}:{self.language}:{self.key}"


@dataclass
class CheckConfig:
    source_language: str = "en"
    targets: tuple[str, ...] = ("kk", "uz")
    reference_language: str = "ru"
    suggestions: dict[tuple[str, str], str] = field(default_factory=dict)


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_RANK.get(item.severity, 9),
            item.language,
            item.key,
            item.checker,
        ),
    )


def quality_score(findings: list[Finding]) -> int:
    penalty = sum(SEVERITY_PENALTY.get(item.severity, 0) for item in findings)
    return max(0, 100 - penalty)
