"""Запись учебного корпуса, глоссария и выверенного казахского на диск."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from qazaq_loc_qa.catalog import STRINGS
from qazaq_loc_qa.glossary_data import TERMS


def write_dataset(root: Path) -> None:
    sample = root / "data" / "sample"
    glossary = root / "data" / "glossary"
    corrected = root / "data" / "corrected"
    for directory in (sample, glossary, corrected):
        directory.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "key": row["key"],
            "context": row["context"],
            "en": row["en"],
            "ru": row["ru"],
            "kk": row["kk"],
            "uz": row["uz"],
        }
        for row in STRINGS
    ]
    (sample / "strings.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with (sample / "strings.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["key", "context", "en", "ru", "kk", "uz"])
        writer.writeheader()
        writer.writerows(rows)
    (sample / "kk.po").write_text(_render_po("kk"), encoding="utf-8")
    _write_xlsx(sample / "strings.xlsx", rows)

    (glossary / "terms.json").write_text(
        json.dumps(TERMS, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    kk_fixed = {row["key"]: row["kk_fixed"] for row in STRINGS}
    uz_fixed = {row["key"]: row["uz_fixed"] for row in STRINGS}
    (corrected / "kk.json").write_text(
        json.dumps(kk_fixed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (corrected / "uz_suggestions.json").write_text(
        json.dumps(uz_fixed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with (corrected / "review.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["key", "context", "kk_before", "kk_after", "uz_before", "uz_after", "why"],
        )
        writer.writeheader()
        for row in STRINGS:
            writer.writerow(
                {
                    "key": row["key"],
                    "context": row["context"],
                    "kk_before": row["kk"],
                    "kk_after": row["kk_fixed"],
                    "uz_before": row["uz"],
                    "uz_after": row["uz_fixed"],
                    "why": row["why"],
                }
            )
    changed = [row for row in STRINGS if row["kk"] != row["kk_fixed"]]
    (corrected / "REVIEW.md").write_text(_review_md(changed), encoding="utf-8")


def _render_po(language: str) -> str:
    lines = [
        'msgid ""',
        'msgstr ""',
        f'"Language: {language}\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        "",
    ]
    for row in STRINGS:
        lines.append(f'msgctxt "{_po(row["key"])}"')
        lines.append(f'msgid "{_po(row["en"])}"')
        lines.append(f'msgstr "{_po(row[language])}"')
        lines.append("")
    return "\n".join(lines)


def _po(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def _write_xlsx(path: Path, rows: list[dict]) -> None:
    try:
        from openpyxl import Workbook
    except ImportError:
        return
    book = Workbook()
    sheet = book.active
    sheet.title = "strings"
    header = ["key", "context", "en", "ru", "kk", "uz"]
    sheet.append(header)
    for row in rows:
        sheet.append([row[column] for column in header])
    book.save(path)


def _review_md(changed: list[dict]) -> str:
    lines = [
        "# Выверенный казахский перевод",
        "",
        "Файл `kk.json` — эталон для тех же ключей, что лежат в `data/sample/strings.json`.",
        "Правки сделаны по нормам литературного казахского (кириллица) и глоссарию игры.",
        "",
        "## Как правили",
        "",
        "- Обращение в системных фразах — на «сіз»: «басыңыз», «таңдаңыз», «көріңіз».",
        "- Кнопки короткие: Ойнау, Баптаулар, Шығу, Жарайды, Бас тарту.",
        "- Сингармонизм: үйлер (не үйлар), үйге (не үйға), достар (не дослар).",
        "- Буквы ё, ъ, щ в казахский текст не переносятся.",
        "- Плейсхолдеры и теги источника сохранены один в один.",
        "- Термины берутся из `data/glossary/terms.json`, а не калькируются с русского.",
        "",
        "Узбекские подсказки лежат в `uz_suggestions.json`. Это рекомендации латиницей",
        "(ў-апостроф U+02BB), их должен принять носитель узбекского. Обязательный",
        "эталон трека — казахский файл.",
        "",
        "## Что изменено",
        "",
        "| Ключ | Было | Стало | Почему |",
        "| --- | --- | --- | --- |",
    ]
    for row in changed:
        before = row["kk"].replace("\n", "↵").replace("|", "\\|")
        after = row["kk_fixed"].replace("\n", "↵").replace("|", "\\|")
        why = row["why"].replace("|", "\\|")
        lines.append(f"| `{row['key']}` | {before} | {after} | {why} |")
    lines.extend(
        [
            "",
            "## Подпись носителя",
            "",
            "Инструмент не подменяет живого редактора. Ниже место для проверки эталона.",
            "",
            "- Имя:",
            "- Дата:",
            "- Вердикт: принимаю / принимаю с правками / не принимаю",
            "- Замечания:",
            "",
        ]
    )
    return "\n".join(lines)
