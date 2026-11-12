"""Разбор плейсхолдеров, тегов и токенов локализационной строки."""

from __future__ import annotations

import re
from collections import Counter

PLACEHOLDER_RE = re.compile(
    r"%(?:\d+\$)?[sdif]"
    r"|\{\{[^{}]+\}\}"
    r"|\{[^{}]+\}"
    r"|\$\{[^{}]+\}"
)
TAG_RE = re.compile(r"<(/?)([A-Za-z][\w:-]*)([^<>]*)>")
TAG_LITERAL_RE = re.compile(r"<[^>]+>")
LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{1,}")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі]")
KAZAKH_ONLY_RE = re.compile(r"[ӘәҒғҚқҢңӨөҰұҮүҺһІі]")
MOJIBAKE_RE = re.compile(r"(?:Ð.|Ã.|Â.|Ñ.|ðŸ|пїЅ|\ufffd)")
BAD_UZ_APOSTROPHE_RE = re.compile(r"([oOgG])['\u2018\u2019\u02bc`\u00b4]")
WHITESPACE_EDGE_RE = re.compile(r"^\s|\s$")
DOUBLE_SPACE_RE = re.compile(r" {2,}")
SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+[?!]")

# Короткие игровые маркеры, которые законно остаются латиницей.
LATIN_ALLOW = {
    "ok",
    "hp",
    "xp",
    "vip",
    "rp",
    "gps",
    "sms",
    "id",
    "ui",
    "npc",
    "pvp",
    "fps",
    "dlc",
    "url",
}

UZ_ENGLISH_WORDS = {
    "login",
    "inventory",
    "skin",
    "battle",
    "pass",
    "connection",
    "loading",
    "continue",
    "quest",
    "donate",
    "finish",
    "top",
    "skip",
    "password",
    "settings",
    "purchase",
}

BACK_VOWELS = set("аоұы")
FRONT_VOWELS = set("әөүіеэ")
NEUTRAL_VOWELS = set("уиюяё")

# После каких букв основы какое окончание множественного числа.
PLURAL_SOFT_TAIL = set("аәеёиоуұүыіэюямнңрй")
PLURAL_MID_TAIL = set("лжз")
DATIVE_SOFT_TAIL = set("аәеёиоуұүыіэюямнңрйлжз")


def placeholders(text: str) -> list[str]:
    return PLACEHOLDER_RE.findall(text or "")


def placeholder_counts(text: str) -> Counter[str]:
    return Counter(placeholders(text))


def tags(text: str) -> list[str]:
    return TAG_LITERAL_RE.findall(text or "")


def tag_balance_error(text: str) -> str | None:
    stack: list[str] = []
    for match in TAG_RE.finditer(text or ""):
        closing, name, attrs = match.group(1), match.group(2).lower(), match.group(3)
        if attrs.rstrip().endswith("/"):
            continue
        if closing:
            if not stack or stack[-1] != name:
                return f"лишний закрывающий тег </{name}>"
            stack.pop()
        else:
            stack.append(name)
    if stack:
        return "не закрыт тег <" + stack[-1] + ">"
    return None


def newline_units(text: str) -> int:
    raw = text or ""
    return raw.count("\n") + raw.count("\\n")


def strip_markup(text: str) -> str:
    cleaned = TAG_LITERAL_RE.sub(" ", text or "")
    cleaned = PLACEHOLDER_RE.sub(" ", cleaned)
    return cleaned


def latin_words(text: str) -> list[str]:
    return LATIN_WORD_RE.findall(strip_markup(text))


def has_cyrillic(text: str) -> bool:
    return CYRILLIC_RE.search(strip_markup(text)) is not None


def kazakh_only_letters(text: str) -> list[str]:
    return KAZAKH_ONLY_RE.findall(text or "")


def same_text(left: str, right: str) -> bool:
    return (left or "").strip().casefold() == (right or "").strip().casefold()


def normalize_uz_apostrophes(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return match.group(1) + "\u02bb"

    return BAD_UZ_APOSTROPHE_RE.sub(repl, text or "")


def has_bad_uz_apostrophe(text: str) -> bool:
    return BAD_UZ_APOSTROPHE_RE.search(text or "") is not None


def kk_tokens(text: str) -> list[str]:
    cleaned = strip_markup(text)
    raw_tokens = re.split(r"\s+", cleaned)
    tokens: list[str] = []
    for token in raw_tokens:
        word = token.strip(".,!?;:«»\"“”()[]…—–-")
        if word:
            tokens.append(word)
    return tokens


def last_harmony_vowel(stem: str) -> str | None:
    for char in reversed(stem.casefold()):
        if char in BACK_VOWELS or char in FRONT_VOWELS:
            return char
        if char in NEUTRAL_VOWELS:
            continue
    return None


def vowel_class(char: str | None) -> str | None:
    if char is None:
        return None
    if char in BACK_VOWELS:
        return "back"
    if char in FRONT_VOWELS:
        return "front"
    return None


def safe_whitespace(text: str) -> str:
    cleaned = (text or "").replace("\u00a0", " ")
    cleaned = DOUBLE_SPACE_RE.sub(" ", cleaned)
    cleaned = SPACE_BEFORE_PUNCT_RE.sub(lambda match: match.group(0).strip(), cleaned)
    # Крайние пробелы убираем, внутренние переводы строк сохраняем.
    return cleaned.strip()
