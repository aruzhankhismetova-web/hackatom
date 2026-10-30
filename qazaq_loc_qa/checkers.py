"""Детерминированные проверки kk и uz.

Технические чекеры (плейсхолдеры, теги, кодировка) не зависят от языка.
Языковые чекеры знают сингармонизм казахского, латинский стандарт узбекского
и глоссарий Grand Mobile.
"""

from __future__ import annotations

import re
from collections import Counter

from qazaq_loc_qa.glossary_data import APPROVED_LOAN_STRINGS, RUSSIAN_LEAKS, TERMS
from qazaq_loc_qa.models import CheckConfig, Finding, Segment
from qazaq_loc_qa.textutil import (
    DATIVE_SOFT_TAIL,
    LATIN_ALLOW,
    PLURAL_MID_TAIL,
    PLURAL_SOFT_TAIL,
    UZ_ENGLISH_WORDS,
    DOUBLE_SPACE_RE,
    MOJIBAKE_RE,
    SPACE_BEFORE_PUNCT_RE,
    WHITESPACE_EDGE_RE,
    has_bad_uz_apostrophe,
    has_cyrillic,
    kazakh_only_letters,
    kk_tokens,
    last_harmony_vowel,
    latin_words,
    newline_units,
    normalize_uz_apostrophes,
    placeholder_counts,
    same_text,
    strip_markup,
    tag_balance_error,
    tags,
    vowel_class,
)

PLURAL_SUFFIXES = (
    ("лар", "back", "soft"),
    ("лер", "front", "soft"),
    ("дар", "back", "mid"),
    ("дер", "front", "mid"),
    ("тар", "back", "hard"),
    ("тер", "front", "hard"),
)
DATIVE_SUFFIXES = (
    ("ға", "back", "soft"),
    ("ге", "front", "soft"),
    ("қа", "back", "hard"),
    ("ке", "front", "hard"),
)


def check_segment(segment: Segment, config: CheckConfig) -> list[Finding]:
    source = segment.texts.get(config.source_language, "")
    findings: list[Finding] = []
    for language in config.targets:
        if language not in segment.texts:
            findings.append(
                _finding(
                    "missing_translation",
                    "critical",
                    language,
                    segment,
                    source,
                    "",
                    "Ключа нет в файле этого языка.",
                )
            )
            continue
        target = segment.texts[language]
        findings.extend(_check_language(segment, source, target, language, config))
    return findings


def _check_language(
    segment: Segment,
    source: str,
    target: str,
    language: str,
    config: CheckConfig,
) -> list[Finding]:
    findings: list[Finding] = []
    reference = segment.texts.get(config.reference_language, "")

    if target.strip() == "" and source.strip():
        findings.append(
            _finding(
                "missing_translation",
                "critical",
                language,
                segment,
                source,
                target,
                "Перевод пустой, а в источнике текст есть.",
            )
        )
        return findings

    if MOJIBAKE_RE.search(target):
        findings.append(
            _finding(
                "mojibake",
                "critical",
                language,
                segment,
                source,
                target,
                "Похоже на битую кодировку: UTF-8 прочитан не той кодовой страницей.",
            )
        )
        findings.extend(_technical(segment, source, target, language))
        return findings

    findings.extend(_technical(segment, source, target, language))

    if _is_untranslated_english(target, source):
        findings.append(
            _finding(
                "untranslated",
                "critical",
                language,
                segment,
                source,
                target,
                "Строка совпадает с английским источником и не выглядит как игровой маркер.",
            )
        )
        return findings

    # Кириллица в узбекском важнее пометки «копия русского»:
    # жюри и локализатор сразу видят нарушение письменности.
    if language == "uz" and has_cyrillic(target):
        findings.extend(_glossary(segment, source, reference, target, language))
        findings.extend(_uzbek(segment, source, target))
        findings.extend(_length(segment, source, target, language))
        return findings

    if (
        reference
        and same_text(target, reference)
        and not same_text(target, source)
        and not _approved_loan(language, target)
    ):
        findings.append(
            _finding(
                "copy_from_ru",
                "high",
                language,
                segment,
                source,
                target,
                "Строка совпадает с русской. Для игрока это калька, а не перевод.",
            )
        )
        return findings

    findings.extend(_glossary(segment, source, reference, target, language))
    if language == "kk":
        findings.extend(_russian_leaks(segment, source, target))
        findings.extend(_harmony(segment, source, target))
        findings.extend(_foreign_letters(segment, source, target))
        findings.extend(_script_mix(segment, source, target))
    if language == "uz":
        findings.extend(_uzbek(segment, source, target))
    findings.extend(_length(segment, source, target, language))
    return findings


def _technical(
    segment: Segment, source: str, target: str, language: str
) -> list[Finding]:
    findings: list[Finding] = []
    source_ph = placeholder_counts(source)
    target_ph = placeholder_counts(target)
    if source_ph != target_ph:
        missing = list((source_ph - target_ph).elements())
        extra = list((target_ph - source_ph).elements())
        details = []
        if missing:
            details.append("нет " + ", ".join(missing))
        if extra:
            details.append("лишние " + ", ".join(extra))
        findings.append(
            _finding(
                "placeholder_mismatch",
                "critical",
                language,
                segment,
                source,
                target,
                "Плейсхолдеры не совпали с источником: " + "; ".join(details) + ".",
            )
        )

    source_tags = Counter(tags(source))
    target_tags = Counter(tags(target))
    balance = tag_balance_error(target)
    if source_tags != target_tags or balance:
        message = "Теги форматирования разъехались с источником."
        if balance:
            message = f"Теги сломаны: {balance}."
        findings.append(
            _finding(
                "tag_mismatch",
                "critical",
                language,
                segment,
                source,
                target,
                message,
            )
        )

    if newline_units(source) != newline_units(target):
        findings.append(
            _finding(
                "newline_mismatch",
                "high",
                language,
                segment,
                source,
                target,
                "Число переводов строки не совпадает с источником.",
            )
        )

    if WHITESPACE_EDGE_RE.search(target) or DOUBLE_SPACE_RE.search(target):
        findings.append(
            _finding(
                "whitespace",
                "medium",
                language,
                segment,
                source,
                target,
                "Лишние пробелы по краям или двойной пробел внутри строки.",
            )
        )

    if SPACE_BEFORE_PUNCT_RE.search(target):
        findings.append(
            _finding(
                "punctuation",
                "medium",
                language,
                segment,
                source,
                target,
                "Пробел стоит перед ? или !.",
            )
        )
    return findings


def _is_untranslated_english(target: str, source: str) -> bool:
    if not source.strip() or not same_text(target, source):
        return False
    words = [word.casefold() for word in latin_words(target)]
    meaningful = [word for word in words if len(word) >= 3 and word not in LATIN_ALLOW]
    return bool(meaningful)


def _approved_loan(language: str, target: str) -> bool:
    allowed = APPROVED_LOAN_STRINGS.get(language, set())
    return target.strip().casefold() in allowed


def _triggered(term: dict, source: str, reference: str) -> bool:
    haystack = {"en": source.casefold(), "ru": reference.casefold()}
    for language, needles in term["triggers"].items():
        text = haystack.get(language, "")
        for needle in needles:
            if _contains_term(text, needle):
                return True
    return False


def _contains_term(text: str, needle: str) -> bool:
    folded = text.casefold()
    for form in _term_forms(needle):
        pattern = r"(?<!\w)" + re.escape(form.casefold())
        if re.search(pattern, folded):
            return True
    return False


def _term_forms(needle: str) -> list[str]:
    """п/к/қ озвончаются перед гласным окончанием: көлік → көлігіңіз, кәсіп → кәсібіңіз."""
    forms = [needle]
    voiced = {"п": "б", "к": "г", "қ": "ғ"}
    if needle and needle[-1] in voiced:
        forms.append(needle[:-1] + voiced[needle[-1]])
    return forms


def _glossary(
    segment: Segment,
    source: str,
    reference: str,
    target: str,
    language: str,
) -> list[Finding]:
    findings: list[Finding] = []
    folded = target.casefold()
    preferred_key = language
    bad_key = f"{language}_bad"
    if preferred_key not in ("kk", "uz"):
        return findings
    for term in TERMS:
        if not _triggered(term, source, reference):
            continue
        bad_hits = [item for item in term.get(bad_key, []) if _contains_term(folded, item)]
        preferred = term.get(preferred_key, [])
        has_preferred = any(_contains_term(folded, item) for item in preferred)
        if bad_hits:
            findings.append(
                _finding(
                    "glossary",
                    "high",
                    language,
                    segment,
                    source,
                    target,
                    f"Термин «{term['id']}» дан запрещённой формой «{bad_hits[0]}». "
                    f"В глоссарии: {', '.join(preferred)}.",
                )
            )
        elif preferred and not has_preferred:
            findings.append(
                _finding(
                    "glossary",
                    "high",
                    language,
                    segment,
                    source,
                    target,
                    f"Для термина «{term['id']}» нет формы из глоссария "
                    f"({', '.join(preferred)}).",
                )
            )
    return findings


def _russian_leaks(segment: Segment, source: str, target: str) -> list[Finding]:
    folded = target.casefold()
    hits = [word for word in RUSSIAN_LEAKS if _contains_term(folded, word)]
    if not hits:
        return []
    preview = ", ".join(hits[:4])
    return [
        _finding(
            "ru_calque",
            "high",
            "kk",
            segment,
            source,
            target,
            f"В казахской строке русские слова: {preview}.",
        )
    ]


def _harmony(segment: Segment, source: str, target: str) -> list[Finding]:
    findings: list[Finding] = []
    for word in kk_tokens(target):
        issue = _harmony_word(word)
        if issue is None:
            continue
        checker, message = issue
        findings.append(
            _finding(checker, "high", "kk", segment, source, target, message)
        )
        break
    return findings


def _harmony_word(word: str) -> tuple[str, str] | None:
    folded = word.casefold()
    if len(folded) < 4 or any(char.isdigit() for char in folded):
        return None
    for suffix, suffix_class, consonant_class in PLURAL_SUFFIXES + DATIVE_SUFFIXES:
        if not folded.endswith(suffix) or len(folded) <= len(suffix) + 1:
            continue
        stem = folded[: -len(suffix)]
        stem_class = vowel_class(last_harmony_vowel(stem))
        if stem_class and stem_class != suffix_class:
            expect = _expected_pair(suffix, stem_class)
            return (
                "kk_vowel_harmony",
                f"«{word}»: после гласных основы окончание должно быть {expect}, "
                "а не противоположного ряда. Это нарушение сингармонизма.",
            )
        tail = stem[-1]
        if suffix in {"лар", "лер", "дар", "дер", "тар", "тер"}:
            actual = consonant_class
            expected = _plural_class(tail)
            if actual != expected:
                better = _plural_suffix(suffix_class, expected)
                return (
                    "kk_suffix_consonant",
                    f"«{word}»: после «{tail}» множественное число пишется с «-{better}», "
                    f"не с «-{suffix}».",
                )
        if suffix in {"ға", "ге", "қа", "ке"}:
            expected = "soft" if tail in DATIVE_SOFT_TAIL else "hard"
            if consonant_class != expected:
                better = _dative_suffix(suffix_class, expected)
                return (
                    "kk_suffix_consonant",
                    f"«{word}»: после «{tail}» барыс септік — «-{better}», не «-{suffix}».",
                )
        return None
    return None


def _expected_pair(suffix: str, stem_class: str) -> str:
    pairs = {
        "лар": ("лар", "лер"),
        "лер": ("лар", "лер"),
        "дар": ("дар", "дер"),
        "дер": ("дар", "дер"),
        "тар": ("тар", "тер"),
        "тер": ("тар", "тер"),
        "ға": ("ға", "ге"),
        "ге": ("ға", "ге"),
        "қа": ("қа", "ке"),
        "ке": ("қа", "ке"),
    }
    back, front = pairs[suffix]
    return f"-{back}" if stem_class == "back" else f"-{front}"


def _plural_class(tail: str) -> str:
    if tail in PLURAL_SOFT_TAIL:
        return "soft"
    if tail in PLURAL_MID_TAIL:
        return "mid"
    return "hard"


def _plural_suffix(vowel: str, consonant_class: str) -> str:
    table = {
        ("back", "soft"): "лар",
        ("front", "soft"): "лер",
        ("back", "mid"): "дар",
        ("front", "mid"): "дер",
        ("back", "hard"): "тар",
        ("front", "hard"): "тер",
    }
    return table[(vowel, consonant_class)]


def _dative_suffix(vowel: str, consonant_class: str) -> str:
    table = {
        ("back", "soft"): "ға",
        ("front", "soft"): "ге",
        ("back", "hard"): "қа",
        ("front", "hard"): "ке",
    }
    return table[(vowel, consonant_class)]


def _foreign_letters(segment: Segment, source: str, target: str) -> list[Finding]:
    found = sorted({char for char in target if char in "ёЁъЪщЩ"})
    if not found:
        return []
    shown = " ".join(found)
    return [
        _finding(
            "kk_foreign_letter",
            "high",
            "kk",
            segment,
            source,
            target,
            f"В казахской кириллице не нужны буквы: {shown}.",
        )
    ]


def _script_mix(segment: Segment, source: str, target: str) -> list[Finding]:
    words = [word for word in latin_words(target) if word.casefold() not in LATIN_ALLOW]
    long_words = [word for word in words if len(word) >= 3]
    if long_words and has_cyrillic(target):
        return [
            _finding(
                "script_mix",
                "high",
                "kk",
                segment,
                source,
                target,
                "В одной строке смешаны казахская кириллица и латиница: "
                + ", ".join(long_words[:4])
                + ".",
            )
        ]
    return []


def _uzbek(segment: Segment, source: str, target: str) -> list[Finding]:
    findings: list[Finding] = []
    letters = kazakh_only_letters(target)
    if has_cyrillic(target):
        extra = ""
        if letters:
            extra = " Есть казахские буквы: " + " ".join(sorted(set(letters))) + "."
        findings.append(
            _finding(
                "uz_cyrillic",
                "high",
                "uz",
                segment,
                source,
                target,
                "Для узбекского в игре принята латиница. В строке осталась кириллица."
                + extra,
            )
        )
    bad_english = [
        word
        for word in latin_words(target)
        if word.casefold() in UZ_ENGLISH_WORDS
    ]
    if bad_english and not has_cyrillic(target):
        findings.append(
            _finding(
                "uz_english",
                "high",
                "uz",
                segment,
                source,
                target,
                "Английские UI-слова внутри узбекской строки: "
                + ", ".join(bad_english[:4])
                + ".",
            )
        )
    if has_bad_uz_apostrophe(target):
        findings.append(
            _finding(
                "uz_apostrophe",
                "medium",
                "uz",
                segment,
                source,
                target,
                "Апостроф в oʻ/gʻ набран как ASCII '. Нужен ў-апостроф (U+02BB): "
                + normalize_uz_apostrophes(target),
            )
        )
    return findings


def _length(segment: Segment, source: str, target: str, language: str) -> list[Finding]:
    source_len = len(strip_markup(source).strip())
    target_len = len(strip_markup(target).strip())
    if source_len <= 24 and target_len > source_len * 2.5 and target_len > source_len + 20:
        return [
            _finding(
                "length_overflow",
                "medium",
                language,
                segment,
                source,
                target,
                f"Строка слишком длинная для UI: {target_len} против {source_len} в источнике.",
            )
        ]
    return []


def _finding(
    checker: str,
    severity: str,
    language: str,
    segment: Segment,
    source: str,
    target: str,
    message: str,
) -> Finding:
    return Finding(
        checker=checker,
        severity=severity,
        language=language,
        key=segment.key,
        message=message,
        source_text=source,
        target_text=target,
        context=segment.context,
    )

