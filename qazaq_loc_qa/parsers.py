"""Чтение JSON, CSV, Excel и PO в один бандл строк."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from qazaq_loc_qa.models import Bundle, Segment

LANGS = ("en", "ru", "kk", "uz")
LANG_FROM_NAME = {
    "en": "en",
    "eng": "en",
    "english": "en",
    "ru": "ru",
    "rus": "ru",
    "russian": "ru",
    "kk": "kk",
    "kz": "kk",
    "kaz": "kk",
    "kazakh": "kk",
    "uz": "uz",
    "uzb": "uz",
    "uzbek": "uz",
}


def load_path(path: str | Path) -> Bundle:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Нет файла или папки: {source}")
    if source.is_dir():
        return _load_dir(source)
    return _load_file(source)


def _load_dir(directory: Path) -> Bundle:
    bundle = Bundle(origin=str(directory))
    table_names = ("strings.json", "strings.csv", "strings.xlsx", "localization.json")
    for name in table_names:
        candidate = directory / name
        if candidate.exists():
            bundle = _merge(bundle, _load_file(candidate))
    for file in sorted(directory.iterdir()):
        if not file.is_file() or file.name.startswith("."):
            continue
        if file.name in table_names:
            continue
        language = _language_from_filename(file.stem)
        if language is None and file.suffix.lower() != ".po":
            continue
        incoming = _load_file(file)
        if language and file.suffix.lower() != ".po":
            incoming = _force_language(incoming, language)
        bundle = _merge(bundle, incoming)
    if not bundle.segments:
        raise ValueError(f"В {directory} не нашлось файлов локализации")
    return bundle


def _load_file(path: Path) -> Bundle:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json(path)
    if suffix == ".csv":
        return _load_csv(path)
    if suffix in {".xlsx", ".xlsm"}:
        return _load_xlsx(path)
    if suffix == ".po":
        return _load_po(path)
    raise ValueError(f"Формат не поддерживается: {path.name}. Нужны JSON, CSV, XLSX или PO.")


def _load_json(path: Path) -> Bundle:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    segments: list[Segment] = []
    if isinstance(payload, list):
        for index, row in enumerate(payload, start=1):
            if not isinstance(row, dict):
                continue
            segments.append(_segment_from_mapping(row, fallback_key=f"row_{index}", source=path.name))
    elif isinstance(payload, dict):
        if _looks_like_row(payload):
            segments.append(_segment_from_mapping(payload, source=path.name))
        else:
            for key, value in payload.items():
                if isinstance(value, str):
                    language = _language_from_filename(path.stem) or "en"
                    segments.append(
                        Segment(key=str(key), texts={language: value}, source_file=path.name)
                    )
                elif isinstance(value, dict):
                    if any(lang in value for lang in LANGS):
                        texts = {lang: str(value[lang]) for lang in LANGS if lang in value}
                        segments.append(
                            Segment(
                                key=str(key),
                                texts=texts,
                                context=str(value.get("context") or ""),
                                source_file=path.name,
                            )
                        )
                    else:
                        flat = _flatten(value)
                        language = _language_from_filename(path.stem) or "en"
                        for flat_key, text in flat.items():
                            full_key = f"{key}.{flat_key}" if flat_key else str(key)
                            segments.append(
                                Segment(key=full_key, texts={language: text}, source_file=path.name)
                            )
                else:
                    continue
    else:
        raise ValueError(f"JSON должен быть объектом или списком: {path}")
    return Bundle(segments=segments, origin=str(path))


def _flatten(value: dict, prefix: str = "") -> dict[str, str]:
    flat: dict[str, str] = {}
    for key, item in value.items():
        next_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, str):
            flat[next_key] = item
        elif isinstance(item, dict):
            flat.update(_flatten(item, next_key))
    return flat


def _looks_like_row(row: dict) -> bool:
    return any(lang in row for lang in LANGS) and ("key" in row or "id" in row)


def _segment_from_mapping(row: dict, fallback_key: str = "", source: str = "") -> Segment:
    key = str(row.get("key") or row.get("id") or row.get("msgctxt") or fallback_key)
    texts = {}
    for lang in LANGS:
        if lang in row and row[lang] is not None:
            texts[lang] = str(row[lang])
    if not texts and "value" in row:
        language = str(row.get("lang") or row.get("language") or "en")
        texts[language] = str(row["value"])
    return Segment(
        key=key,
        texts=texts,
        context=str(row.get("context") or row.get("comment") or ""),
        source_file=source,
    )


def _load_csv(path: Path) -> Bundle:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        segments = []
        for index, row in enumerate(reader, start=1):
            normalized = {(key or "").strip().lower(): value for key, value in row.items()}
            segments.append(
                _segment_from_mapping(normalized, fallback_key=f"row_{index}", source=path.name)
            )
    return Bundle(segments=segments, origin=str(path))


def _load_xlsx(path: Path) -> Bundle:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("Для Excel установите пакет openpyxl") from exc
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    try:
        header = [str(cell or "").strip().lower() for cell in next(rows)]
    except StopIteration as exc:
        raise ValueError(f"Пустой Excel: {path}") from exc
    segments = []
    for index, row in enumerate(rows, start=1):
        mapping = {header[pos]: "" if cell is None else str(cell) for pos, cell in enumerate(row)}
        if not any(mapping.values()):
            continue
        segments.append(_segment_from_mapping(mapping, fallback_key=f"row_{index}", source=path.name))
    workbook.close()
    return Bundle(segments=segments, origin=str(path))


def _load_po(path: Path) -> Bundle:
    language = _language_from_po(path) or _language_from_filename(path.stem) or "kk"
    segments: list[Segment] = []
    block: dict[str, str] = {}

    def flush() -> None:
        if "msgstr" not in block and "msgid" not in block:
            return
        key = block.get("msgctxt") or block.get("msgid") or ""
        if not key:
            return
        texts: dict[str, str] = {language: block.get("msgstr", "")}
        msgid = block.get("msgid", "")
        if msgid and msgid != key and "en" not in texts:
            texts["en"] = msgid
        segments.append(Segment(key=key, texts=texts, source_file=path.name))

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if not stripped:
                flush()
                block = {}
            continue
        matched = re.match(r'(msgctxt|msgid|msgstr)\s+"(.*)"\s*$', stripped)
        if not matched:
            continue
        kind, value = matched.group(1), _unescape_po(matched.group(2))
        block[kind] = block.get(kind, "") + value
    flush()
    return Bundle(segments=segments, origin=str(path))


def _language_from_po(path: Path) -> str | None:
    header = path.read_text(encoding="utf-8-sig")
    matched = re.search(r'"Language:\s*([A-Za-z_-]+)', header)
    if not matched:
        return None
    return _language_from_filename(matched.group(1).split("_")[0].split("-")[0])


def _unescape_po(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def _language_from_filename(stem: str) -> str | None:
    token = stem.lower().split(".")[0].split("_")[0].split("-")[0]
    return LANG_FROM_NAME.get(token)


def _force_language(bundle: Bundle, language: str) -> Bundle:
    """Файл вида kk.json хранит тексты одного языка, даже если ключ похож на фразу."""
    forced: list[Segment] = []
    for segment in bundle.segments:
        text = segment.texts.get(language)
        if text is None and len(segment.texts) == 1:
            text = next(iter(segment.texts.values()))
        if text is None:
            continue
        forced.append(
            Segment(
                key=segment.key,
                texts={language: text},
                context=segment.context,
                source_file=segment.source_file,
            )
        )
    return Bundle(segments=forced, origin=bundle.origin)


def _merge(base: Bundle, incoming: Bundle) -> Bundle:
    index = {segment.key: segment for segment in base.segments}
    for segment in incoming.segments:
        current = index.get(segment.key)
        if current is None:
            index[segment.key] = Segment(
                key=segment.key,
                texts=dict(segment.texts),
                context=segment.context,
                source_file=segment.source_file,
            )
            continue
        for language, text in segment.texts.items():
            current.texts.setdefault(language, text)
        if not current.context:
            current.context = segment.context
    return Bundle(segments=list(index.values()), origin=base.origin or incoming.origin)
