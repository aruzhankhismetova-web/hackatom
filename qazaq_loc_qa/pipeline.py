"""Сборка проверки: чекеры, подсказки эталона и безопасные правки."""

from __future__ import annotations

from qazaq_loc_qa.checkers import check_segment
from qazaq_loc_qa.models import Bundle, CheckConfig, Finding, Segment, sort_findings
from qazaq_loc_qa.textutil import normalize_uz_apostrophes, safe_whitespace


def run_checks(bundle: Bundle, config: CheckConfig | None = None) -> list[Finding]:
    settings = config or CheckConfig()
    findings: list[Finding] = []
    for segment in bundle.segments:
        findings.extend(check_segment(segment, settings))
    for finding in findings:
        suggestion = settings.suggestions.get((finding.language, finding.key), "")
        if suggestion and suggestion != finding.target_text:
            finding.suggestion = suggestion
    return sort_findings(findings)


def apply_verified(
    bundle: Bundle,
    suggestions: dict[tuple[str, str], str],
    *,
    languages: tuple[str, ...] = ("kk",),
    normalize_uz: bool = False,
) -> Bundle:
    """Подставить выверенный перевод и механически поправить пробелы.

    Казахский эталон берётся целиком. Для узбекского по умолчанию правится
    только апостроф oʻ/gʻ: смысловой перевод uz оставляет носитель узбекского.
    """
    updated: list[Segment] = []
    for segment in bundle.segments:
        texts = dict(segment.texts)
        for language, text in list(texts.items()):
            if language == "uz" and normalize_uz:
                texts[language] = normalize_uz_apostrophes(text)
            if language in {"kk", "uz"}:
                texts[language] = safe_whitespace(texts[language])
            if language in languages:
                replacement = suggestions.get((language, segment.key))
                if replacement is not None:
                    texts[language] = replacement
        updated.append(
            Segment(
                key=segment.key,
                texts=texts,
                context=segment.context,
                source_file=segment.source_file,
            )
        )
    return Bundle(segments=updated, source_language=bundle.source_language, origin=bundle.origin)
