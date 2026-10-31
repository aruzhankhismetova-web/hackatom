"""Глоссарий игровых терминов и проверка единообразия."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from soz.models import Entry, Finding


@dataclass
class Term:
    id: str
    source: list[str]
    preferred: str
    accepted: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    contexts: list[str] = field(default_factory=list)
    notes: str = ""
    scope: str = "always"
    ui_limit: int | None = None

    def surfaces(self) -> list[str]:
        return [self.preferred, *self.accepted, *self.forbidden, *self.source]


@dataclass
class Glossary:
    language: str
    game: str
    terms: list[Term]

    def forbidden_fold(self) -> set[str]:
        return {form.casefold() for term in self.terms for form in term.forbidden}

    def relevant(self, entry: Entry) -> list[Term]:
        haystack = f"{entry.source}\n{entry.target}".casefold()
        picked: list[Term] = []
        for term in self.terms:
            if any(form.casefold() in haystack for form in term.surfaces() if form):
                picked.append(term)
        return picked


def load_glossary(directory: Path) -> dict[str, Glossary]:
    books: dict[str, Glossary] = {}
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        language = str(data.get("language") or path.stem)
        terms = [_term(item) for item in data.get("terms", [])]
        books[language] = Glossary(
            language=language,
            game=str(data.get("game") or ""),
            terms=terms,
        )
    return books


def glossary_findings(entry: Entry, glossary: Glossary | None) -> list[Finding]:
    if glossary is None or not entry.target.strip():
        return []
    findings: list[Finding] = []
    for term in glossary.terms:
        if not _term_applies(term, entry):
            continue
        forms = sorted(term.forbidden, key=len, reverse=True)
        for form in forms:
            if not _contains_form(entry.target, form):
                continue
            suggestion = _replace_form(entry.target, form, term.preferred)
            findings.append(
                _finding(
                    entry,
                    "glossary",
                    "glossary_term",
                    "high",
                    f"Термин «{form}» расходится с глоссарием. Норма: «{term.preferred}». {term.notes}".strip(),
                    suggestion,
                )
            )
            break
    return _dedupe(findings)


def inconsistency_findings(entries: list[Entry], books: dict[str, Glossary]) -> list[Finding]:
    grouped: dict[tuple[str, str, str], list[Entry]] = {}
    for entry in entries:
        if not entry.source.strip() or not entry.target.strip():
            continue
        grouped.setdefault((entry.file, entry.locale, entry.source.casefold()), []).append(entry)

    findings: list[Finding] = []
    for bucket in grouped.values():
        targets = {item.target.casefold() for item in bucket}
        if len(targets) < 2:
            continue
        glossary = books.get(bucket[0].locale)
        term = _term_for_source(glossary, bucket[0].source) if glossary else None
        if term is None:
            continue
        rendered = " / ".join(dict.fromkeys(item.target for item in bucket))
        for entry in bucket:
            findings.append(
                _finding(
                    entry,
                    "glossary",
                    "glossary_inconsistency",
                    "medium",
                    f"Источник «{entry.source}» переведён по-разному: {rendered}. Норма глоссария: «{term.preferred}».",
                    term.preferred if _single_term_line(entry.target) else entry.target,
                )
            )
    return findings


def slice_for_prompt(entry: Entry, glossary: Glossary | None) -> list[dict[str, object]]:
    if glossary is None:
        return []
    payload = []
    for term in glossary.relevant(entry):
        payload.append(
            {
                "id": term.id,
                "preferred": term.preferred,
                "accepted": term.accepted,
                "forbidden": term.forbidden,
                "notes": term.notes,
            }
        )
    return payload


def introduces_forbidden(text: str, glossary: Glossary | None) -> str:
    if glossary is None:
        return ""
    for form in sorted(glossary.forbidden_fold(), key=len, reverse=True):
        if _contains_form(text, form):
            return form
    return ""


def _term(item: dict[str, object]) -> Term:
    return Term(
        id=str(item.get("id") or ""),
        source=[str(value) for value in item.get("source", [])],
        preferred=str(item.get("preferred") or ""),
        accepted=[str(value) for value in item.get("accepted", [])],
        forbidden=[str(value) for value in item.get("forbidden", [])],
        contexts=[str(value) for value in item.get("contexts", [])],
        notes=str(item.get("notes") or ""),
        scope=str(item.get("scope") or "always"),
        ui_limit=int(item["ui_limit"]) if item.get("ui_limit") else None,
    )


def _term_applies(term: Term, entry: Entry) -> bool:
    if term.scope == "always":
        return True
    source = entry.source.casefold()
    if any(alias.casefold() in source for alias in term.source):
        return True
    if term.scope == "context" and entry.context in term.contexts:
        return True
    return False


def _term_for_source(glossary: Glossary, source: str) -> Term | None:
    folded = source.casefold()
    for term in glossary.terms:
        if any(alias.casefold() in folded for alias in term.source):
            return term
    return None


def _contains_form(text: str, form: str) -> bool:
    pattern = re.compile(rf"(?i)(?<![\w]){re.escape(form)}(?![\w])")
    return pattern.search(text) is not None


def _replace_form(text: str, form: str, preferred: str) -> str:
    pattern = re.compile(rf"(?i)(?<![\w]){re.escape(form)}(?![\w])")

    def repl(match: re.Match[str]) -> str:
        return _cased(match.group(0), preferred)

    return pattern.sub(repl, text)


def _cased(sample: str, replacement: str) -> str:
    if sample.isupper():
        return replacement.upper()
    if sample[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    if sample[:1].islower():
        return replacement[:1].lower() + replacement[1:]
    return replacement


def _single_term_line(text: str) -> bool:
    return len(text.split()) <= 2


def _finding(
    entry: Entry,
    engine: str,
    code: str,
    severity: str,
    message: str,
    suggestion: str,
) -> Finding:
    return Finding(
        file=entry.file,
        key=entry.key,
        locale=entry.locale,
        context=entry.context,
        severity=severity,
        engine=engine,
        code=code,
        message=message,
        source=entry.source,
        target=entry.target,
        suggestion=suggestion,
    )


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str]] = set()
    unique: list[Finding] = []
    for item in findings:
        mark = (item.code, item.suggestion)
        if mark in seen:
            continue
        seen.add(mark)
        unique.append(item)
    return unique
