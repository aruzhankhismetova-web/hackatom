"""Сверка прогона с samples/gold.json."""

from __future__ import annotations

import json
from pathlib import Path

from soz.glossary import load_glossary
from soz.models import RunResult
from soz.parse import load_many
from soz.paths import repo_root
from soz.pipeline import run


def evaluate(root: Path | None = None) -> list[str]:
    root = root or repo_root()
    gold = json.loads((root / "samples" / "gold.json").read_text(encoding="utf-8"))
    sample_dir = root / "samples"
    books = load_glossary(root / "glossary")
    result = run(load_many([sample_dir]), books, ai_mode="local")
    failures: list[str] = []

    for filename in gold.get("clean_files", []):
        names = {Path(entry.file).name for entry in result.entries}
        if filename not in names:
            failures.append(f"{filename}: файл не прочитан")
            continue
        for entry in result.entries:
            if Path(entry.file).name != filename:
                continue
            actual = _codes(result, filename, entry.key)
            if actual:
                failures.append(f"{filename}:{entry.key}: ожидалась чистая строка, найдено {actual}")

    listed = {(str(case["file"]), str(case["key"])) for case in gold.get("cases", [])}
    clean_names = set(gold.get("clean_files", []))
    for entry in result.entries:
        name = Path(entry.file).name
        if name in clean_names:
            continue
        if (name, entry.key) not in listed:
            failures.append(f"{name}:{entry.key}: нет в gold.json")

    for case in gold.get("cases", []):
        filename = str(case["file"])
        key = str(case["key"])
        expected = sorted(case.get("codes", []))
        actual = _codes(result, filename, key)
        if actual != expected:
            failures.append(f"{filename}:{key}: коды {actual}, ожидалось {expected}")
            continue
        suggestion = case.get("suggestion")
        if suggestion:
            got = _suggestions(result, filename, key)
            if suggestion not in got:
                failures.append(
                    f"{filename}:{key}: нет правки «{suggestion}», есть {got or '—'}"
                )
    return failures


def _codes(result: RunResult, filename: str, key: str) -> list[str]:
    return sorted(
        {
            finding.code
            for finding in result.findings
            if Path(finding.file).name == filename and finding.key == key
        }
    )


def _suggestions(result: RunResult, filename: str, key: str) -> list[str]:
    return [
        finding.suggestion
        for finding in result.findings
        if Path(finding.file).name == filename and finding.key == key and finding.suggestion
    ]
