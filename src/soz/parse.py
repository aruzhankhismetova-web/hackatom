"""Чтение JSON, CSV, Excel и PO в единый список строк."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from soz.context import infer_context
from soz.models import Entry

_KEY_ALIASES = ("key", "id", "name", "string_id", "token")
_SOURCE_ALIASES = ("source", "en", "english", "msgid", "original", "base")
_TARGET_ALIASES = ("target", "translation", "msgstr", "text", "value", "kk", "uz")
_CONTEXT_ALIASES = ("context", "comment", "screen", "notes")
_LOCALE_ALIASES = ("locale", "lang", "language")


def locale_from_name(path: Path) -> str:
    name = path.name.casefold()
    if re.search(r"(^|[_\-.])kk([_\-.]|$)", name) or "kazakh" in name:
        return "kk"
    if re.search(r"(^|[_\-.])uz([_\-.]|$)", name) or "uzbek" in name:
        return "uz"
    return ""


def load_path(path: Path, locale: str = "") -> list[Entry]:
    suffix = path.suffix.casefold()
    if suffix == ".json":
        return load_json(path, locale)
    if suffix == ".csv":
        return load_csv(path, locale)
    if suffix in {".xlsx", ".xlsm"}:
        return load_xlsx(path, locale)
    if suffix == ".po":
        return load_po(path, locale)
    raise ValueError(f"Неизвестный формат: {path.name}")


def load_many(paths: list[Path], locale: str = "") -> list[Entry]:
    entries: list[Entry] = []
    for path in _expand(paths):
        entries.extend(load_path(path, locale))
    return entries


def _expand(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.suffix.casefold() in {".json", ".csv", ".xlsx", ".xlsm", ".po"}:
                    if child.name.endswith(".gold.json") or child.name == "gold.json":
                        continue
                    found.append(child)
        elif path.is_file():
            found.append(path)
    return found


def load_json(path: Path, locale: str = "") -> list[Entry]:
    data = json.loads(path.read_text(encoding="utf-8"))
    file_locale = locale or _json_locale(data) or locale_from_name(path)
    rows = _json_rows(data)
    return [_entry_from_row(row, path, file_locale) for row in rows]


def load_csv(path: Path, locale: str = "") -> list[Entry]:
    text = path.read_text(encoding="utf-8-sig")
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    if not reader.fieldnames:
        return []
    file_locale = locale or locale_from_name(path)
    return [
        _entry_from_row({k: v or "" for k, v in row.items()}, path, file_locale)
        for row in reader
        if any((value or "").strip() for value in row.values())
    ]


def load_xlsx(path: Path, locale: str = "") -> list[Entry]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Для Excel нужен пакет openpyxl") from exc

    book = load_workbook(path, read_only=True, data_only=True)
    sheet = book.active
    rows = list(sheet.iter_rows(values_only=True))
    book.close()
    if not rows:
        return []
    header = [str(cell or "").strip() for cell in rows[0]]
    file_locale = locale or locale_from_name(path)
    entries: list[Entry] = []
    for raw in rows[1:]:
        if raw is None or all(cell is None or str(cell).strip() == "" for cell in raw):
            continue
        row = {
            header[index]: "" if cell is None else str(cell)
            for index, cell in enumerate(raw)
            if index < len(header) and header[index]
        }
        entries.append(_entry_from_row(row, path, file_locale))
    return entries


def load_po(path: Path, locale: str = "") -> list[Entry]:
    text = path.read_text(encoding="utf-8-sig")
    file_locale = locale or _po_language(text) or locale_from_name(path)
    entries: list[Entry] = []
    comment = ""
    reference = ""
    context = ""
    msgid: list[str] | None = None
    msgstr: list[str] | None = None
    mode = ""

    def flush() -> None:
        nonlocal comment, reference, context, msgid, msgstr, mode
        if msgid is None or msgstr is None:
            return
        source = _unescape_po("".join(msgid))
        target = _unescape_po("".join(msgstr))
        if not source.strip():
            comment = ""
            reference = ""
            context = ""
            msgid = None
            msgstr = None
            mode = ""
            return
        if source or target:
            key = reference or context or _slug(source)
            entries.append(
                Entry(
                    key=key,
                    source=source,
                    target=target,
                    locale=file_locale,
                    context=infer_context(key, context or _context_from_comment(comment)),
                    file=str(path),
                    notes=comment,
                )
            )
        comment = ""
        reference = ""
        context = ""
        msgid = None
        msgstr = None
        mode = ""

    for line in text.splitlines():
        if line.startswith("#."):
            comment = (comment + " " + line[2:].strip()).strip()
            continue
        if line.startswith("#:"):
            reference = line[2:].strip().split()[0] if line[2:].strip() else reference
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgctxt "):
            flush()
            context = _read_po_string(line[len("msgctxt ") :])
            mode = ""
            continue
        if line.startswith("msgid "):
            flush()
            msgid = [_read_po_string(line[len("msgid ") :])]
            mode = "id"
            continue
        if line.startswith("msgstr "):
            msgstr = [_read_po_string(line[len("msgstr ") :])]
            mode = "str"
            continue
        if line.startswith('"') and mode == "id" and msgid is not None:
            msgid.append(_read_po_string(line))
            continue
        if line.startswith('"') and mode == "str" and msgstr is not None:
            msgstr.append(_read_po_string(line))
            continue
        if not line.strip():
            flush()
    flush()
    return [entry for entry in entries if entry.source or entry.key]


def _json_locale(data: object) -> str:
    if isinstance(data, dict):
        for key in ("locale", "lang", "language"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return _norm_locale(value)
    return ""


def _json_rows(data: object) -> list[dict[str, str]]:
    if isinstance(data, list):
        return [_coerce_row(item) for item in data]
    if isinstance(data, dict):
        for key in ("entries", "strings", "items", "translations"):
            value = data.get(key)
            if isinstance(value, list):
                return [_coerce_row(item) for item in value]
            if isinstance(value, dict):
                return _dict_rows(value)
        if _looks_like_row(data):
            return [_coerce_row(data)]
        return _dict_rows(data)
    return []


def _dict_rows(data: dict[str, object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key, value in data.items():
        if key in {"locale", "lang", "language", "meta"}:
            continue
        if isinstance(value, str):
            rows.append({"key": key, "target": value})
        elif isinstance(value, dict):
            row = _coerce_row(value)
            row.setdefault("key", key)
            rows.append(row)
    return rows


def _coerce_row(item: object) -> dict[str, str]:
    if isinstance(item, str):
        return {"target": item}
    if not isinstance(item, dict):
        return {"target": str(item)}
    return {str(key): "" if value is None else str(value) for key, value in item.items()}


def _looks_like_row(data: dict[str, object]) -> bool:
    keys = {key.casefold() for key in data}
    return bool(keys & set(_TARGET_ALIASES) or keys & set(_SOURCE_ALIASES))


def _entry_from_row(row: dict[str, str], path: Path, file_locale: str) -> Entry:
    folded = {key.casefold(): value for key, value in row.items()}
    key = _first(folded, _KEY_ALIASES) or _slug(_first(folded, _SOURCE_ALIASES) or _first(folded, _TARGET_ALIASES))
    source = _first(folded, _SOURCE_ALIASES)
    target = _first(folded, _TARGET_ALIASES)
    if not target:
        for name, value in folded.items():
            if name not in _KEY_ALIASES and name not in _SOURCE_ALIASES and name not in _CONTEXT_ALIASES and name not in _LOCALE_ALIASES:
                target = value
                break
    context = _first(folded, _CONTEXT_ALIASES)
    locale = _norm_locale(_first(folded, _LOCALE_ALIASES)) or file_locale
    return Entry(
        key=key,
        source=source,
        target=target,
        locale=locale,
        context=infer_context(key, context),
        file=str(path),
        notes=context,
    )


def _first(row: dict[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _norm_locale(value: str) -> str:
    folded = value.strip().casefold().replace("_", "-")
    if folded in {"kk", "kz", "kaz", "kazakh", "kk-kz"}:
        return "kk"
    if folded in {"uz", "uzn", "uzbek", "uz-latn", "uz-cyrl"}:
        return "uz"
    if folded in {"en", "eng", "english"}:
        return "en"
    return folded


def _slug(text: str) -> str:
    cleaned = re.sub(r"\W+", "_", text.strip().casefold(), flags=re.UNICODE).strip("_")
    return cleaned[:48] or "entry"


def _po_language(text: str) -> str:
    match = re.search(r'"Language:\s*([^\\"]+)', text)
    return _norm_locale(match.group(1)) if match else ""


def _context_from_comment(comment: str) -> str:
    match = re.search(r"(?i)context:\s*([\w_]+)", comment)
    return match.group(1) if match else ""


def _read_po_string(chunk: str) -> str:
    chunk = chunk.strip()
    if chunk.startswith('"') and chunk.endswith('"'):
        return chunk[1:-1]
    return chunk


def _unescape_po(value: str) -> str:
    pieces: list[str] = []
    index = 0
    mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
    while index < len(value):
        if value[index] == "\\" and index + 1 < len(value):
            pieces.append(mapping.get(value[index + 1], value[index + 1]))
            index += 2
            continue
        pieces.append(value[index])
        index += 1
    return "".join(pieces)
