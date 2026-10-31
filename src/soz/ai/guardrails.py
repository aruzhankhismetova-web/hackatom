"""Ограждения поверх любой подсказки, в том числе ответа модели.

Подсказка отбрасывается, если она ломает плейсхолдеры, теги, согласование
или приносит запрещённый термин. На чистой строке модель обязана промолчать.
"""

from __future__ import annotations

import re

from soz.glossary import Glossary, introduces_forbidden
from soz.models import Entry, Finding
from soz.tokens import token_counter

_KK_SIZ = re.compile(r"(?iu)(?<![\w])сіз(?![\w])")
_KK_WORD = re.compile(r"(?iu)[а-яёәғқңөұүіһ]+", re.IGNORECASE)
_UZ_SIZ = re.compile(r"(?i)(?<![\w])siz(?![\w])")
_UZ_WORD = re.compile(r"(?i)[a-zʻʼ']+")

_AI_CODES = {"calque_ru", "calque_en", "glossary_term", "register", "meaning"}


def breaks_agreement(text: str, locale: str) -> bool:
    """Формальное «сіз/siz» с глаголом на «ты» — запрещённая подсказка."""
    if locale == "kk":
        if not _KK_SIZ.search(text):
            return False
        for word in _KK_WORD.findall(text):
            folded = word.casefold()
            if folded == "сіз":
                continue
            if folded.endswith(("дыңыз", "діңіз", "тыңыз", "тіңіз")):
                continue
            if folded.endswith(("сыз", "сіз")):
                continue
            if folded.endswith(("дың", "дің", "тың", "тің", "сың", "сің")):
                return True
        return False
    if locale == "uz":
        if not _UZ_SIZ.search(text):
            return False
        for word in _UZ_WORD.findall(text):
            folded = word.casefold()
            if folded == "siz":
                continue
            if folded.endswith(("dingiz", "tingiz")):
                continue
            if folded.endswith(("ding", "ting")):
                return True
        return False
    return False


def suggestion_ok(suggestion: str, entry: Entry, glossary: Glossary | None) -> bool:
    if not suggestion or not suggestion.strip():
        return False
    if "⟦" in suggestion:
        return False
    if token_counter(suggestion) != token_counter(entry.target):
        return False
    if breaks_agreement(suggestion, entry.locale):
        return False
    if introduces_forbidden(suggestion, glossary):
        return False
    if suggestion.strip() == entry.target.strip():
        return False
    return True


def filter_findings(
    findings: list[Finding],
    entry: Entry,
    glossary: Glossary | None,
    *,
    known_clean: bool,
) -> tuple[list[Finding], int]:
    kept: list[Finding] = []
    dropped = 0
    for finding in findings:
        if finding.engine == "ai" and finding.code not in _AI_CODES:
            dropped += 1
            continue
        if finding.engine == "ai" and known_clean:
            dropped += 1
            continue
        if finding.suggestion and finding.engine == "ai":
            if not suggestion_ok(finding.suggestion, entry, glossary):
                dropped += 1
                continue
        elif finding.engine == "ai":
            dropped += 1
            continue
        kept.append(finding)
    return kept, dropped
