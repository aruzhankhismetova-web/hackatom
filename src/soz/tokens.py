"""Плейсхолдеры и теги, которые перевод не имеет права менять."""

from __future__ import annotations

import re
from collections import Counter

# Порядок важен: {{name}} раньше {name}, %1$s раньше голого %.
TOKEN_RE = re.compile(
    r"%(?:\d+\$)?[sdif]"
    r"|\{\{[^{}]+\}\}"
    r"|\{[^{}]+\}"
    r"|</?[A-Za-z][^>]*>"
    r"|\\[ntr]"
)

_TAG_RE = re.compile(r"<(/?)([A-Za-z][\w:-]*)([^>]*)>")
_VOID = {"br", "img", "hr", "meta", "input"}


def find_tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text or "")


def token_counter(text: str) -> Counter[str]:
    return Counter(find_tokens(text))


def mask_tokens(text: str) -> str:
    """Убирает плейсхолдеры и теги, чтобы морфология не видела обрывки вроде «s» из %s."""
    return TOKEN_RE.sub(" ", text or "")


def tags_balanced(text: str) -> bool:
    stack: list[str] = []
    for slash, name, rest in _TAG_RE.findall(text or ""):
        name = name.lower()
        if name in _VOID or rest.rstrip().endswith("/"):
            continue
        if not slash:
            stack.append(name)
        elif not stack or stack[-1] != name:
            return False
        else:
            stack.pop()
    return not stack


def shield(text: str) -> tuple[str, list[str]]:
    """Меняет плейсхолдеры на стабильные токены ⟦n⟧, которые модель не переводит."""
    tokens = find_tokens(text)
    shielded = text
    for index, token in enumerate(tokens):
        shielded = shielded.replace(token, f"⟦{index}⟧", 1)
    return shielded, tokens


def unshield(text: str, tokens: list[str]) -> str:
    restored = text
    for index, token in enumerate(tokens):
        restored = restored.replace(f"⟦{index}⟧", token)
    return restored
