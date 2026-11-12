"""Техническая проверка: плейсхолдеры, теги, үндестік, орфография uz, числа."""

from __future__ import annotations

import re

from soz.glossary import Glossary
from soz.harmony import apply_replacements, kk_harmony_issues, uz_morph_issues
from soz.models import Entry, Finding
from soz.tokens import mask_tokens, tags_balanced, token_counter

_KK_NUMBER = re.compile(
    r"(?P<num>\d+|\{[^{}]+\})\s+(?P<word>\S*?(?:лар|лер|дар|дер|тар|тер))\b",
    re.IGNORECASE,
)
_UZ_DOUBLE = re.compile(r"(\d+)\s+ta\s+([A-Za-zʻʼ']+)lar\b", re.IGNORECASE)
_UZ_NUMBER = re.compile(r"(\d+)\s+(?!ta\b)([A-Za-zʻʼ']+)lar\b", re.IGNORECASE)
_PLURAL_TAIL = re.compile(r"(?:лар|лер|дар|дер|тар|тер)$", re.IGNORECASE)
_LEGACY_LATIN = re.compile(r"[öğşçÖĞŞÇ]")
_MOJIBAKE = re.compile(r"\ufffd|Ð.|Ã.|â€")
_LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
_CYR_WORD = re.compile(r"[\u0400-\u04FF]{2,}")


def technical_findings(entry: Entry, glossary: Glossary | None = None) -> list[Finding]:
    target = entry.target or ""
    source = entry.source or ""
    findings: list[Finding] = []

    if source.strip() and not target.strip():
        findings.append(_make(entry, "missing_translation", "critical", "Пустой перевод при заполненном источнике."))
        return findings

    if _mojibake(target):
        findings.append(_make(entry, "mojibake", "critical", "Похоже на битую кодировку или символ замены."))

    placeholder_gap = _counter_gap(source, target, kind="placeholder")
    if placeholder_gap:
        findings.append(
            _make(
                entry,
                "placeholder_mismatch",
                "critical",
                f"Плейсхолдеры источника и перевода не совпадают: {placeholder_gap}.",
            )
        )

    tag_gap = _counter_gap(source, target, kind="tag")
    if tag_gap:
        findings.append(
            _make(
                entry,
                "tag_mismatch",
                "critical",
                f"Теги форматирования разъехались: {tag_gap}.",
            )
        )
    elif target and not tags_balanced(target):
        findings.append(_make(entry, "unclosed_tag", "critical", "В переводе не закрыт тег форматирования."))

    if _same_as_source(entry):
        findings.append(
            _make(entry, "untranslated", "high", "Строка совпадает с источником и не переведена.")
        )
    else:
        findings.extend(_script_findings(entry))

    if re.search(r" {2,}|\s+[,.!?;:]", target):
        findings.append(_make(entry, "whitespace", "medium", "Лишние пробелы или пробел перед знаком препинания."))

    if entry.context == "ui_button" and len(target) > 24:
        findings.append(
            _make(
                entry,
                "length",
                "medium",
                f"Кнопка длиннее 24 символов ({len(target)}). Для UI нужен короткий вариант.",
            )
        )

    if entry.locale == "kk":
        findings.extend(_kk_number(entry))
        findings.extend(_kk_harmony(entry, glossary))
    elif entry.locale == "uz":
        findings.extend(_uz_number(entry))
        findings.extend(_uz_morph(entry, glossary))
        if _LEGACY_LATIN.search(target):
            findings.append(
                _make(
                    entry,
                    "uz_latin_legacy",
                    "info",
                    "Буквы ö ğ ş ç до 22 апреля 2027 в билде не требуются. Оставляйте текущую латиницу и U+02BB.",
                )
            )
    return findings


def _kk_harmony(entry: Entry, glossary: Glossary | None) -> list[Finding]:
    issues = kk_harmony_issues(entry.target, _skip_forms(glossary))
    if not issues:
        return []
    suggestion = apply_replacements(entry.target, [(old, new) for old, new, _code, _title in issues])
    return [
        _make(
            entry,
            code,
            "high",
            f"{title}: «{old}» → «{new}».",
            suggestion,
        )
        for old, new, code, title in issues
    ]


def _uz_morph(entry: Entry, glossary: Glossary | None) -> list[Finding]:
    issues = uz_morph_issues(entry.target, _skip_forms(glossary))
    if not issues:
        return []
    suggestion = apply_replacements(entry.target, [(old, new) for old, new, _code, _title in issues])
    return [
        _make(entry, code, "high", f"{title}: «{old}» → «{new}».", suggestion)
        for old, new, code, title in issues
    ]


def _kk_number(entry: Entry) -> list[Finding]:
    match = _KK_NUMBER.search(entry.target)
    if not match:
        return []
    word = match.group("word")
    stem = _PLURAL_TAIL.sub("", word)
    if not stem or stem == word:
        return []
    suggestion = entry.target[: match.start("word")] + stem + entry.target[match.end("word") :]
    return [
        _make(
            entry,
            "number_plural",
            "high",
            f"После числа көптік не ставится: «{word}» → «{stem}».",
            suggestion,
        )
    ]


def _uz_number(entry: Entry) -> list[Finding]:
    double = _UZ_DOUBLE.search(entry.target)
    if double:
        noun = double.group(2)
        suggestion = _UZ_DOUBLE.sub(rf"\1 ta {noun}", entry.target, count=1)
        return [
            _make(
                entry,
                "uz_double_plural",
                "high",
                f"«ta» уже считает предмет, суффикс -lar лишний: «{double.group(0)}» → «{double.group(1)} ta {noun}».",
                suggestion,
            )
        ]
    plain = _UZ_NUMBER.search(entry.target)
    if plain:
        noun = plain.group(2)
        suggestion = _UZ_NUMBER.sub(rf"\1 {noun}", entry.target, count=1)
        return [
            _make(
                entry,
                "number_plural",
                "high",
                f"После числа множественное -lar не ставится: «{plain.group(0)}» → «{plain.group(1)} {noun}».",
                suggestion,
            )
        ]
    return []


def _script_findings(entry: Entry) -> list[Finding]:
    masked = mask_tokens(entry.target)
    findings: list[Finding] = []
    for raw in re.findall(r"\S+", masked):
        word = raw.strip(".,!?:;«»\"“”()[]…")
        if len(word) < 2:
            continue
        has_cyr = bool(re.search(r"[\u0400-\u04FF]", word))
        has_lat = bool(re.search(r"[A-Za-z]", word))
        if has_cyr and has_lat:
            findings.append(
                _make(entry, "script_mix", "high", f"В одном слове смешаны кириллица и латиница: «{word}».")
            )
            continue
        if entry.locale == "kk" and _LATIN_WORD.fullmatch(word):
            findings.append(
                _make(entry, "script_mix", "high", f"В казахской строке осталось латинское слово «{word}».")
            )
        elif entry.locale == "uz" and _CYR_WORD.fullmatch(word):
            findings.append(
                _make(entry, "script_mix", "high", f"В узбекской строке осталось кириллическое слово «{word}».")
            )
    return findings[:4]


def _same_as_source(entry: Entry) -> bool:
    if entry.locale not in {"kk", "uz"}:
        return False
    if not entry.source.strip():
        return False
    return entry.target.casefold() == entry.source.casefold() and bool(_LATIN_WORD.search(entry.source))


def _counter_gap(source: str, target: str, kind: str) -> str:
    from soz.tokens import find_tokens

    def pick(text: str) -> list[str]:
        tokens = find_tokens(text)
        if kind == "tag":
            return [token for token in tokens if token.startswith("<")]
        return [token for token in tokens if not token.startswith("<")]

    left = pick(source)
    right = pick(target)
    if sorted(left) == sorted(right):
        return ""
    return f"источник {left or '—'}, перевод {right or '—'}"


def _mojibake(text: str) -> bool:
    return _MOJIBAKE.search(text) is not None


def _skip_forms(glossary: Glossary | None) -> set[str]:
    if glossary is None:
        return set()
    return {form.casefold() for term in glossary.terms for form in term.forbidden}


def _make(
    entry: Entry,
    code: str,
    severity: str,
    message: str,
    suggestion: str = "",
) -> Finding:
    return Finding(
        file=entry.file,
        key=entry.key,
        locale=entry.locale,
        context=entry.context,
        severity=severity,
        engine="technical",
        code=code,
        message=message,
        source=entry.source,
        target=entry.target,
        suggestion=suggestion,
    )
