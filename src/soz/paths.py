"""Корень репозитория: рядом лежат glossary/ и prompts/."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "glossary").is_dir() and (parent / "prompts").is_dir():
            return parent
    return Path.cwd()
