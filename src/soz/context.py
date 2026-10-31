"""Игровой контекст строки: кнопка, диалог, тост, выход."""

from __future__ import annotations

import re


def infer_context(key: str, explicit: str = "") -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    folded = (key or "").casefold()
    if folded.startswith("dialog"):
        return "dialog"
    if "toast" in folded:
        return "toast"
    if folded.startswith("btn") or folded.startswith("button"):
        return "ui_button"
    if "shop" in folded:
        return "shop"
    if any(part in folded for part in ("exit", "quit", "sure", "confirm")):
        return "confirm"
    return "system"


def mentions_exit(entry_blob: str) -> bool:
    return bool(
        re.search(r"(?i)\b(exit|quit|leave|logout|log out|шық|chiq)\b", entry_blob)
    )


def is_dialog(context: str) -> bool:
    return context == "dialog"


def is_toast(context: str) -> bool:
    return context == "toast"
