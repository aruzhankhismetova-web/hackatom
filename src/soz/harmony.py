"""Буын үндестігі и дыбыс үндестігі для қазақша, суффиксы для oʻzbekcha.

Модель эти правила не перепроверяет: их закрывает детерминированный слой.
"""

from __future__ import annotations

import re

from soz.tokens import mask_tokens

_BACK = set("аоұы")
_FRONT = set("әөүіеэ")
_NEUTRAL = set("у")
_VOICELESS = set("пфкқтсшхцч")
_PLURAL_D = set("лмнңжзбвгғд")

# (suffix, kind, vowel, consonant class)
_KK_SUFFIXES: tuple[tuple[str, str, str, str], ...] = (
    ("дар", "plural", "back", "D"),
    ("дер", "plural", "front", "D"),
    ("тар", "plural", "back", "T"),
    ("тер", "plural", "front", "T"),
    ("лар", "plural", "back", "L"),
    ("лер", "plural", "front", "L"),
    ("дан", "abl", "back", "D"),
    ("ден", "abl", "front", "D"),
    ("тан", "abl", "back", "T"),
    ("тен", "abl", "front", "T"),
    ("ға", "dat", "back", "D"),
    ("ге", "dat", "front", "D"),
    ("қа", "dat", "back", "T"),
    ("ке", "dat", "front", "T"),
    ("да", "loc", "back", "D"),
    ("де", "loc", "front", "D"),
    ("та", "loc", "back", "T"),
    ("те", "loc", "front", "T"),
)

_KK_BY_LENGTH = tuple(sorted(_KK_SUFFIXES, key=lambda item: len(item[0]), reverse=True))

_WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F\u0400-\u04FF''\u2018\u2019\u02BB\u02BC]+")
_PUNCT = ".,!?:;«»\"“”()[]…—"

_UZ_CANON = {
    "dokon": "Doʻkon",
    "oynash": "Oʻynash",
    "galaba": "gʻalaba",
    "royxat": "roʻyxat",
    "royxatdan": "roʻyxatdan",
    "dost": "doʻst",
    "dostlar": "doʻstlar",
    "sovga": "sovgʻa",
    "ogil": "oʻgʻil",
}

_UZ_SKIP_DE = {"sinde"}


def kk_harmony_issues(text: str, skip: set[str] | None = None) -> list[tuple[str, str, str, str]]:
    """Возвращает (слово, исправленное слово, code, заголовок правила)."""
    masked = mask_tokens(text)
    found: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for word in _words(masked):
        if word in seen or _skip(word, skip):
            continue
        fixed = fix_kk_word(word)
        if fixed is None:
            continue
        seen.add(word)
        found.append((word, *fixed))
    return found


def fix_kk_word(word: str) -> tuple[str, str, str] | None:
    bare = word.strip(_PUNCT)
    folded = bare.casefold()
    for suffix, kind, vowel, cons in _KK_BY_LENGTH:
        if not folded.endswith(suffix):
            continue
        stem = folded[: -len(suffix)]
        if len(stem) < 2 or not _has_vowel(stem):
            return None
        stem_vowel = _vowel_class(stem)
        stem_cons = _consonant_class(stem, kind)
        vowel_bad = stem_vowel in {"back", "front"} and stem_vowel != vowel
        cons_bad = stem_cons != cons
        if not vowel_bad and not cons_bad:
            return None
        correct = _pick_suffix(kind, stem_vowel if stem_vowel in {"back", "front"} else vowel, stem_cons)
        if correct == suffix:
            return None
        rebuilt = _match_stem_case(bare, stem + correct)
        code = "vowel_harmony" if vowel_bad else "consonant_harmony"
        title = "Буын үндестігі" if vowel_bad else "Дыбыс үндестігі"
        return rebuilt, code, title
    return None


def uz_morph_issues(text: str, skip: set[str] | None = None) -> list[tuple[str, str, str, str]]:
    masked = mask_tokens(text)
    found: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for word in _words(masked):
        if word in seen or _skip(word, skip):
            continue
        fixed = fix_uz_word(word)
        if fixed is None:
            continue
        seen.add(word)
        found.append((word, *fixed))
    return found


def fix_uz_word(word: str) -> tuple[str, str, str] | None:
    bare = word.strip(_PUNCT)
    folded = bare.casefold()
    if folded in _UZ_CANON:
        canon = _apply_case(bare, _UZ_CANON[folded])
        if canon != bare:
            return canon, "uz_apostrophe", "Орфография oʻ/gʻ"
    apostrophe = _fix_apostrophe(bare)
    if apostrophe is not None:
        return apostrophe, "uz_apostrophe", "Орфография oʻ/gʻ"
    if folded.endswith("ler") and len(folded) > 5:
        return _apply_case(bare, folded[:-3] + "lar"), "uz_plural_suffix", "Чужой суффикс -ler"
    if re.search(r"[kq]ga$", folded) and len(folded) > 4:
        fixed = re.sub(r"([kq])ga$", lambda match: match.group(1) * 2 + "a", folded)
        return _apply_case(bare, fixed), "uz_dative", "Датив после k/q"
    if folded.endswith("de") and len(folded) > 3 and folded not in _UZ_SKIP_DE:
        return _apply_case(bare, folded[:-2] + "da"), "uz_locative", "Локатив -da"
    if folded.endswith("te") and len(folded) > 3:
        return _apply_case(bare, folded[:-2] + "ta"), "uz_locative", "Локатив -da"
    return None


def apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    updated = text
    for old, new in pairs:
        updated = _replace_word(updated, old, new)
    return updated


def _replace_word(text: str, old: str, new: str) -> str:
    pattern = re.compile(
        rf"(?<![\w\u02BB''\u2019]){re.escape(old)}(?![\w\u02BB''\u2019])"
    )
    return pattern.sub(lambda _match: new, text)


def _words(text: str) -> list[str]:
    return [word for word in _WORD_RE.findall(text) if len(word) >= 3]


def _skip(word: str, skip: set[str] | None) -> bool:
    if not skip:
        return False
    folded = word.casefold()
    if folded in skip:
        return True
    return any(folded.startswith(form) and 0 < len(folded) - len(form) <= 6 for form in skip)


def _has_vowel(stem: str) -> bool:
    return any(char in _BACK or char in _FRONT or char in _NEUTRAL for char in stem)


def _vowel_class(stem: str) -> str:
    for char in reversed(stem):
        if char in _BACK:
            return "back"
        if char in _FRONT:
            return "front"
        if char in _NEUTRAL:
            return "neutral"
    return "neutral"


def _consonant_class(stem: str, kind: str) -> str:
    last = stem[-1]
    if last in _VOICELESS:
        return "T"
    if kind == "plural" and last in _PLURAL_D:
        return "D"
    if kind == "plural":
        return "L"
    return "D"


def _pick_suffix(kind: str, vowel: str, cons: str) -> str:
    for suffix, suffix_kind, suffix_vowel, suffix_cons in _KK_SUFFIXES:
        if suffix_kind == kind and suffix_vowel == vowel and suffix_cons == cons:
            return suffix
    return ""


def _match_stem_case(original: str, rebuilt: str) -> str:
    if original.isupper():
        return rebuilt.upper()
    if original[:1].isupper():
        return rebuilt[:1].upper() + rebuilt[1:]
    return rebuilt


def _apply_case(original: str, canon: str) -> str:
    if original.islower():
        return canon[:1].lower() + canon[1:]
    if original.isupper():
        return canon.upper()
    if original[:1].isupper():
        return canon[:1].upper() + canon[1:]
    return canon


def _fix_apostrophe(word: str) -> str | None:
    fixed, count = re.subn(
        r"([OoGg])['\u2018\u2019\u02BC]",
        lambda match: match.group(1) + "\u02bb",
        word,
    )
    if count and fixed != word:
        return fixed
    return None
