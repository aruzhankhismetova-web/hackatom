"""Командная строка TilTekser.

Примеры:
  python -m qazaq_loc_qa demo
  python -m qazaq_loc_qa check data/sample/strings.json --out reports/before
  python -m qazaq_loc_qa fix data/sample/strings.json --out reports/after
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qazaq_loc_qa import __version__
from qazaq_loc_qa.catalog import suggestion_map
from qazaq_loc_qa.dataset import write_dataset
from qazaq_loc_qa.llm import (
    LLMConfig,
    build_user_prompt,
    findings_from_issues,
    glossary_lines,
    parse_llm_payload,
    request_review,
)
from qazaq_loc_qa.models import CheckConfig
from qazaq_loc_qa.parsers import load_path
from qazaq_loc_qa.pipeline import apply_verified, run_checks
from qazaq_loc_qa.report import render_text, summarize, write_reports
from qazaq_loc_qa.slides import write_slides

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qazaq_loc_qa", description="TilTekser — QA локализации kk/uz")
    parser.add_argument("--version", action="version", version=f"TilTekser {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Прогнать учебный корпус Grand Mobile и собрать отчёты")
    demo.add_argument("--root", default=str(ROOT))

    check = sub.add_parser("check", help="Проверить JSON, CSV, XLSX, PO или папку")
    check.add_argument("path")
    check.add_argument("--out", default="reports")
    check.add_argument("--source", default="en")
    check.add_argument("--targets", default="kk,uz")
    check.add_argument("--llm", action="store_true", help="Добавить смысловые замечания модели, если задан API-ключ")

    fix = sub.add_parser("fix", help="Подставить выверенный kk и заново проверить")
    fix.add_argument("path")
    fix.add_argument("--out", default="reports/fixed")
    fix.add_argument("--corrections", default="", help="JSON-объект key → казахский текст. По умолчанию data/corrected/kk.json")
    fix.add_argument("--normalize-uz", action="store_true", help="Механически заменить o'/g' на oʻ/gʻ")

    args = parser.parse_args(argv)
    if args.command == "demo":
        return _demo(Path(args.root))
    if args.command == "check":
        return _check(args)
    if args.command == "fix":
        return _fix(args)
    return 2


def _demo(root: Path) -> int:
    write_dataset(root)
    bundle = load_path(root / "data" / "sample" / "strings.json")
    config = CheckConfig(suggestions=suggestion_map())
    before = run_checks(bundle, config)
    before_dir = root / "reports" / "before"
    write_reports(before, before_dir, title="TilTekser — ошибки в учебном корпусе", bundle=bundle)

    fixed = apply_verified(bundle, suggestion_map(), languages=("kk",), normalize_uz=True)
    after_config = CheckConfig(suggestions=suggestion_map())
    after = run_checks(fixed, after_config)
    after_dir = root / "reports" / "after"
    write_reports(after, after_dir, title="TilTekser — после выверенного казахского", bundle=fixed)
    (root / "data" / "corrected" / "kk_bundle.json").write_text(
        (after_dir / "bundle.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_slides(root / "slides" / "index.html", before=summarize(before), after=summarize(after))

    print(render_text(before, "До правки"))
    print()
    print(render_text(after, "После подстановки выверенного kk и апострофов uz"))
    print()
    print(f"HTML до:     {before_dir / 'report.html'}")
    print(f"HTML после:  {after_dir / 'report.html'}")
    print(f"Казахский:   {root / 'data' / 'corrected' / 'kk.json'}")
    print(f"Слайды:      {root / 'slides' / 'index.html'}")

    kk_left = [item for item in after if item.language == "kk" and item.severity in {"critical", "high"}]
    if kk_left:
        print(f"Казахский эталон всё ещё содержит {len(kk_left)} серьёзных находок.", file=sys.stderr)
        return 1
    return 0


def _check(args: argparse.Namespace) -> int:
    bundle = load_path(args.path)
    config = CheckConfig(
        source_language=args.source,
        targets=tuple(part.strip() for part in args.targets.split(",") if part.strip()),
        suggestions=_load_suggestion_file(),
    )
    findings = run_checks(bundle, config)
    if args.llm:
        findings.extend(_llm_findings(bundle))
        findings = sorted(findings, key=lambda item: (item.severity, item.language, item.key))
    out = Path(args.out)
    written = write_reports(findings, out, title="TilTekser — отчёт проверки", bundle=bundle)
    print(render_text(findings, "Проверка"))
    print(f"\nОтчёт: {written['html']}")
    return 0


def _fix(args: argparse.Namespace) -> int:
    bundle = load_path(args.path)
    suggestions = _load_suggestion_file(args.corrections)
    fixed = apply_verified(
        bundle,
        suggestions,
        languages=("kk",),
        normalize_uz=args.normalize_uz,
    )
    findings = run_checks(fixed, CheckConfig(suggestions=suggestions))
    out = Path(args.out)
    written = write_reports(findings, out, title="TilTekser — после правки kk", bundle=fixed)
    print(render_text(findings, "После правки"))
    print(f"\nИсправленный бандл: {written['bundle']}")
    print(f"Отчёт: {written['html']}")
    return 0


def _load_suggestion_file(path: str = "") -> dict[tuple[str, str], str]:
    candidate = Path(path) if path else ROOT / "data" / "corrected" / "kk.json"
    if not candidate.exists():
        return suggestion_map()
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "kk" not in payload and all(isinstance(value, str) for value in payload.values()):
        mapped = {("kk", key): value for key, value in payload.items()}
        uz_path = candidate.parent / "uz_suggestions.json"
        if uz_path.exists():
            uz_payload = json.loads(uz_path.read_text(encoding="utf-8"))
            mapped.update({("uz", key): value for key, value in uz_payload.items()})
        return mapped
    return suggestion_map()


def _llm_findings(bundle):
    config = LLMConfig.from_env()
    if config is None:
        print("LLM пропущен: нет OPENAI_API_KEY или QAZAQ_LLM_API_KEY.", file=sys.stderr)
        return []
    interesting = [
        segment
        for segment in bundle.segments
        if segment.texts.get("kk") or segment.texts.get("uz")
    ][:20]
    raw = request_review(config, build_user_prompt(interesting, glossary_lines()))
    issues = parse_llm_payload(raw)
    return findings_from_issues(issues, {segment.key: segment for segment in bundle.segments})


if __name__ == "__main__":
    raise SystemExit(main())
