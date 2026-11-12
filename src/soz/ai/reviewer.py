"""Локальный ревьюер: те же решения, что зафиксированы в prompts/few_shot.json.

Он не заменяет модель на длинном хвосте. Он закрывает случаи, где ошибка
уже известна, и не даёт модели переписывать диалог, тост и плейсхолдеры.
"""

from __future__ import annotations

import re

from soz.ai.guardrails import breaks_agreement
from soz.ai.prompts import normalize_text
from soz.context import mentions_exit
from soz.glossary import Glossary, introduces_forbidden
from soz.models import Entry, Finding

_SURE = re.compile(r"(?i)^\s*сенімдісіз\s+(?:бе|ма|ба|пе|па|ме)\s*\??\s*$")
_BUTTON = re.compile(r"(?i)кнопк\w*\s+басыңыз")
_UZ_SURE = re.compile(r"(?i)^\s*siz\s+ishonchingiz\s+komilmi\s*\??\s*$")
_RU_MARKERS = {
    "ваш",
    "ваша",
    "ваше",
    "это",
    "чтобы",
    "кнопка",
    "кнопке",
    "кнопку",
    "настройки",
    "выйти",
    "загрузка",
    "нажмите",
}


def semantic_review(
    entry: Entry,
    glossary: Glossary | None,
    few_shot: dict[str, object],
) -> list[Finding]:
    if not entry.target.strip():
        return []
    fix = _match_fix(entry, few_shot)
    if fix is not None:
        return [fix]
    if _match_silent(entry, few_shot):
        return []

    suggestion = _phrase_suggestion(entry)
    if suggestion and suggestion != entry.target:
        return [
            _ai(
                entry,
                "calque_ru",
                "Калька с русского в игровой реплике. Заменяется строка целиком, термин берётся из глоссария.",
                suggestion,
            )
        ]

    agreement = _agreement_suggestion(entry)
    if agreement:
        return [
            _ai(
                entry,
                "register",
                "Местоимение и глагол в разных регистрах. Нельзя оставить «сіз/siz» с формой на «ты».",
                agreement,
            )
        ]
    return []


def known_clean(entry: Entry, few_shot: dict[str, object], glossary: Glossary | None) -> bool:
    if _match_silent(entry, few_shot):
        return True
    if introduces_forbidden(entry.target, glossary):
        return False
    if _phrase_suggestion(entry):
        return False
    if entry.context == "dialog" and _informal_agrees(entry):
        return True
    if entry.context == "toast" and _informal_agrees(entry):
        return True
    return False


def looks_unresolved(entry: Entry) -> bool:
    words = {word.casefold() for word in re.findall(r"[А-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүІіҺһ]+", entry.target)}
    return bool(words & _RU_MARKERS)


def _match_fix(entry: Entry, few_shot: dict[str, object]) -> Finding | None:
    for example in few_shot.get("fix", []):
        if not isinstance(example, dict):
            continue
        if not _same_example(entry, example):
            continue
        return _ai(
            entry,
            str(example.get("code") or "calque_ru"),
            str(example.get("why") or "Калька. Строка заменяется целиком."),
            str(example.get("suggestion") or ""),
        )
    return None


def _match_silent(entry: Entry, few_shot: dict[str, object]) -> bool:
    for example in few_shot.get("silent", []):
        if isinstance(example, dict) and _same_example(entry, example):
            return True
    return False


def _same_example(entry: Entry, example: dict[str, object]) -> bool:
    if example.get("locale") and example.get("locale") != entry.locale:
        return False
    if example.get("context") and example.get("context") != entry.context:
        return False
    if example.get("key") and example.get("key") != entry.key:
        return False
    target = example.get("target")
    if isinstance(target, str) and normalize_text(target) != normalize_text(entry.target):
        return False
    blob = entry.blob().casefold()
    require = example.get("require_any") or []
    if isinstance(require, list) and require:
        if not any(str(token).casefold() in blob for token in require):
            return False
    reject = example.get("reject_if_any") or []
    if isinstance(reject, list) and any(str(token).casefold() in blob for token in reject):
        return False
    return True


def _phrase_suggestion(entry: Entry) -> str:
    text = entry.target.strip()
    if entry.locale == "kk" and _SURE.match(text):
        if mentions_exit(entry.blob()):
            return "Шыққыңыз келе ме?"
        return "Растайсыз ба?"
    if entry.locale == "kk" and _BUTTON.search(text):
        return _BUTTON.sub("Батырманы басыңыз", entry.target)
    if entry.locale == "uz" and _UZ_SURE.match(text) and mentions_exit(entry.blob()):
        return "Chiqasizmi?"
    return ""


def _agreement_suggestion(entry: Entry) -> str:
    if not breaks_agreement(entry.target, entry.locale):
        return ""
    if entry.locale == "kk":
        if entry.context in {"toast", "dialog"}:
            return re.sub(
                r"(?iu)(?<![\w])сіз(?![\w])",
                lambda match: "Сен" if match.group(0)[:1].isupper() else "сен",
                entry.target,
            )
        return _formalize_kk(entry.target)
    if entry.locale == "uz" and entry.context in {"toast", "dialog"}:
        return re.sub(
            r"(?i)(?<![\w])siz(?![\w])",
            lambda match: "Sen" if match.group(0)[:1].isupper() else "sen",
            entry.target,
        )
    return ""


def _formalize_kk(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        word = match.group(0)
        folded = word.casefold()
        pairs = (
            ("дыңыз", None),
            ("діңіз", None),
            ("тың", "тыңыз"),
            ("тің", "тіңіз"),
            ("дың", "дыңыз"),
            ("дің", "діңіз"),
            ("сың", "сыз"),
            ("сің", "сіз"),
        )
        for suffix, replacement in pairs:
            if replacement is None:
                continue
            if folded.endswith(suffix) and not folded.endswith(replacement):
                return word[: -len(suffix)] + replacement
        return word

    return _KK_WORD.sub(repl, text)


_KK_WORD = re.compile(r"(?iu)[а-яёәғқңөұүіһ]+")


def _informal_agrees(entry: Entry) -> bool:
    if breaks_agreement(entry.target, entry.locale):
        return False
    if entry.locale == "kk":
        return re.search(r"(?iu)(?<![\w])сен(?![\w])", entry.target) is not None
    if entry.locale == "uz":
        return re.search(r"(?i)(?<![\w])sen(?![\w])", entry.target) is not None
    return False


def _ai(entry: Entry, code: str, message: str, suggestion: str) -> Finding:
    return Finding(
        file=entry.file,
        key=entry.key,
        locale=entry.locale,
        context=entry.context,
        severity="high",
        engine="ai",
        code=code,
        message=message,
        source=entry.source,
        target=entry.target,
        suggestion=suggestion,
    )
