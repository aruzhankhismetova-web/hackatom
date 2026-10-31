"""Командная строка Sóz."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from soz.eval import evaluate
from soz.glossary import load_glossary
from soz.parse import load_many
from soz.paths import repo_root
from soz.pipeline import run
from soz.report import write_reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_loc.py",
        description="Проверка локализации «Алтын Жол»: плейсхолдеры, үндестік, глоссарий и калька.",
    )
    parser.add_argument("paths", nargs="*", help="Файлы или каталог JSON, CSV, XLSX, PO")
    parser.add_argument("--glossary", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--locale", default="", help="Принудительная локаль kk или uz")
    parser.add_argument(
        "--ai",
        choices=("auto", "local", "api", "off"),
        default="auto",
        help="auto: модель, если есть OPENAI_API_KEY, иначе калиброванные правила",
    )
    parser.add_argument("--eval", action="store_true", help="Сверить samples с gold.json")
    args = parser.parse_args(argv)

    if args.eval or (args.paths and args.paths[0] == "eval"):
        failures = evaluate()
        if failures:
            print("Калибровка не сошлась:")
            for line in failures:
                print(f"  {line}")
            return 1
        print("Калибровка сошлась: gold.json")
        return 0

    root = repo_root()
    raw_paths = args.paths or [str(root / "samples")]
    paths = [Path(item) for item in raw_paths]
    entries = load_many(paths, args.locale)
    if not entries:
        print("Нет строк для проверки.", file=sys.stderr)
        return 2
    books = load_glossary(args.glossary or (root / "glossary"))
    result = run(entries, books, ai_mode=args.ai)
    out = args.out or (root / "reports")
    json_path, html_path = write_reports(result, out)
    critical = sum(1 for item in result.findings if item.severity == "critical")
    print(
        f"Строк: {len(result.entries)}. Находок: {len(result.findings)} "
        f"(критичных {critical}). Смысловой режим: {result.ai.mode}."
    )
    print(f"JSON: {json_path}")
    print(f"HTML: {html_path}")
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
