"""Сводка технического слоя, глоссария и смыслового ревью."""

from __future__ import annotations

from soz.ai.client import LlmClient
from soz.ai.guardrails import filter_findings
from soz.ai.prompts import load_prompt_assets, system_prompt, user_prompt
from soz.ai.reviewer import known_clean, looks_unresolved, semantic_review
from soz.glossary import Glossary, glossary_findings, inconsistency_findings, introduces_forbidden, slice_for_prompt
from soz.models import SEVERITY_RANK, AiMeta, Entry, Finding, RunResult
from soz.paths import repo_root
from soz.technical import technical_findings


def run(
    entries: list[Entry],
    books: dict[str, Glossary],
    *,
    ai_mode: str = "auto",
    client: LlmClient | None = None,
) -> RunResult:
    client = client or LlmClient()
    assets = load_prompt_assets(repo_root())
    few_shot = assets["few_shot"]
    assert isinstance(few_shot, dict)
    mode = _resolve_mode(ai_mode, client)
    meta = AiMeta(
        mode=mode,
        prompt_version=str(assets["version"]),
        model=client.model if mode == "api" else "",
    )
    system = system_prompt(assets) if mode == "api" else ""
    findings: list[Finding] = []

    for entry in entries:
        glossary = books.get(entry.locale)
        technical = technical_findings(entry, glossary)
        glossary_hits = glossary_findings(entry, glossary)
        semantic: list[Finding] = []
        if mode != "off":
            semantic = semantic_review(entry, glossary, few_shot)
            semantic, dropped = filter_findings(
                semantic,
                entry,
                glossary,
                known_clean=False,
            )
            meta.guardrail_dropped += dropped

        clean = known_clean(entry, few_shot, glossary)
        if mode == "api" and _needs_model(entry, semantic, glossary_hits, clean, glossary):
            meta.llm_called += 1
            try:
                proposed = client.review(
                    entry,
                    system,
                    user_prompt(
                        entry,
                        slice_for_prompt(entry, glossary),
                        sorted({item.code for item in technical}),
                    ),
                )
            except Exception:
                meta.unresolved.append(f"{entry.key}: модель не ответила")
                proposed = []
            proposed, dropped = filter_findings(
                proposed,
                entry,
                glossary,
                known_clean=clean,
            )
            meta.guardrail_dropped += dropped
            have = {(item.key, item.code) for item in semantic}
            for item in proposed:
                if (item.key, item.code) in have:
                    continue
                semantic.append(item)
                have.add((item.key, item.code))
        elif mode != "off" and not semantic and not glossary_hits and looks_unresolved(entry):
            meta.unresolved.append(entry.key)

        if mode != "off" and clean and not semantic:
            meta.silent_skipped += 1

        findings.extend(technical)
        findings.extend(glossary_hits)
        findings.extend(semantic)

    findings.extend(inconsistency_findings(entries, books))
    findings = _drop_glossary_fixed_by_ai(findings, books)
    findings.sort(key=lambda item: (SEVERITY_RANK.get(item.severity, 9), item.file, item.key, item.engine, item.code))
    return RunResult(entries=entries, findings=findings, ai=meta)


def _needs_model(
    entry: Entry,
    semantic: list[Finding],
    glossary_hits: list[Finding],
    clean: bool,
    glossary: Glossary | None,
) -> bool:
    if semantic or clean:
        return False
    if any(item.code == "glossary_term" for item in glossary_hits):
        return False
    return looks_unresolved(entry) or bool(introduces_forbidden(entry.target, glossary))


def _resolve_mode(ai_mode: str, client: LlmClient) -> str:
    if ai_mode == "auto":
        return "api" if client.available() else "local"
    if ai_mode == "api" and not client.available():
        return "local"
    return ai_mode


def _drop_glossary_fixed_by_ai(
    findings: list[Finding],
    books: dict[str, Glossary],
) -> list[Finding]:
    suggestions: dict[tuple[str, str], list[str]] = {}
    for finding in findings:
        if finding.engine == "ai" and finding.suggestion:
            suggestions.setdefault((finding.file, finding.key), []).append(finding.suggestion)

    kept: list[Finding] = []
    for finding in findings:
        if finding.code != "glossary_term":
            kept.append(finding)
            continue
        glossary = books.get(finding.locale)
        options = suggestions.get((finding.file, finding.key), [])
        if glossary and options and _ai_removed_forbidden(finding.target, options, glossary):
            continue
        kept.append(finding)
    return kept


def _ai_removed_forbidden(target: str, suggestions: list[str], glossary: Glossary) -> bool:
    present = [form for form in glossary.forbidden_fold() if _has(target, form)]
    if not present:
        return False
    for suggestion in suggestions:
        if any(_has(suggestion, form) for form in present):
            continue
        if any(_has(target, form) and not _has(suggestion, form) for form in present):
            return True
    return False


def _has(text: str, form: str) -> bool:
    return introduces_forbidden(text, _OneForm(form)) != ""


class _OneForm:
    """Минимальный объект, чтобы переиспользовать поиск запретной формы."""

    def __init__(self, form: str) -> None:
        self.form = form

    def forbidden_fold(self) -> set[str]:
        return {self.form}
