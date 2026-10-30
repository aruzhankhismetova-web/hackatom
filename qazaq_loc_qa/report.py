"""Текстовый, CSV, JSON и HTML-отчёт по находкам."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path

from qazaq_loc_qa.models import SEVERITY_RANK, Bundle, Finding, quality_score

CHECKER_TITLES = {
    "missing_translation": "Пустой перевод",
    "mojibake": "Битая кодировка",
    "placeholder_mismatch": "Плейсхолдер",
    "tag_mismatch": "Сломан тег",
    "newline_mismatch": "Перевод строки",
    "whitespace": "Пробелы",
    "punctuation": "Пунктуация",
    "untranslated": "Не переведено",
    "copy_from_ru": "Калька с русского",
    "glossary": "Глоссарий",
    "ru_calque": "Русское слово",
    "kk_vowel_harmony": "Сингармонизм",
    "kk_suffix_consonant": "Окончание",
    "kk_foreign_letter": "Чужая буква",
    "script_mix": "Смешение алфавитов",
    "length_overflow": "Длина в UI",
    "uz_cyrillic": "Кириллица в uz",
    "uz_apostrophe": "Апостроф oʻ/gʻ",
    "uz_english": "Английское слово",
    "llm_review": "Смысловая проверка",
}


def summarize(findings: list[Finding]) -> dict:
    by_severity = Counter(item.severity for item in findings)
    by_language = Counter(item.language for item in findings)
    by_checker = Counter(item.checker for item in findings)
    return {
        "total": len(findings),
        "score": quality_score(findings),
        "by_severity": {name: by_severity.get(name, 0) for name in SEVERITY_RANK},
        "by_language": dict(by_language),
        "by_checker": dict(by_checker),
    }


def write_reports(findings: list[Finding], directory: Path, *, title: str, bundle: Bundle | None = None) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    summary = summarize(findings)
    json_path = directory / "findings.json"
    csv_path = directory / "findings.csv"
    html_path = directory / "report.html"
    summary_path = directory / "summary.json"
    json_path.write_text(
        json.dumps(
            {
                "title": title,
                "summary": summary,
                "findings": [_as_dict(item) for item in findings],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "severity",
                "language",
                "key",
                "checker",
                "message",
                "source",
                "current",
                "suggestion",
                "context",
            ],
        )
        writer.writeheader()
        for item in findings:
            writer.writerow(
                {
                    "severity": item.severity,
                    "language": item.language,
                    "key": item.key,
                    "checker": item.checker,
                    "message": item.message,
                    "source": item.source_text,
                    "current": item.target_text,
                    "suggestion": item.suggestion,
                    "context": item.context,
                }
            )
    html_path.write_text(render_html(findings, title=title, summary=summary), encoding="utf-8")
    written = {"json": json_path, "csv": csv_path, "html": html_path, "summary": summary_path}
    if bundle is not None:
        bundle_path = directory / "bundle.json"
        bundle_path.write_text(_bundle_json(bundle), encoding="utf-8")
        written["bundle"] = bundle_path
    return written


def render_text(findings: list[Finding], title: str) -> str:
    summary = summarize(findings)
    lines = [
        title,
        f"Оценка: {summary['score']}/100 · находок: {summary['total']}",
        "  "
        + "  ".join(f"{name}={summary['by_severity'][name]}" for name in ("critical", "high", "medium", "low")),
        "",
    ]
    for item in findings:
        lines.append(
            f"[{item.severity}] {item.language} {item.key} · {CHECKER_TITLES.get(item.checker, item.checker)}"
        )
        lines.append(f"  {item.message}")
        if item.suggestion:
            lines.append(f"  → {item.suggestion}")
    return "\n".join(lines)


def render_html(findings: list[Finding], *, title: str, summary: dict | None = None) -> str:
    summary = summary or summarize(findings)
    rows = []
    for item in findings:
        rows.append(
            "<tr data-lang='{lang}' data-sev='{sev}'>"
            "<td><span class='sev sev-{sev}'>{sev}</span></td>"
            "<td>{lang}</td>"
            "<td><code>{key}</code><div class='ctx'>{ctx}</div></td>"
            "<td>{checker}</td>"
            "<td>{message}</td>"
            "<td class='mono'>{source}</td>"
            "<td class='mono bad'>{current}</td>"
            "<td class='mono good'>{suggestion}</td>"
            "</tr>".format(
                lang=html.escape(item.language),
                sev=html.escape(item.severity),
                key=html.escape(item.key),
                ctx=html.escape(item.context),
                checker=html.escape(CHECKER_TITLES.get(item.checker, item.checker)),
                message=html.escape(item.message),
                source=_cell(item.source_text),
                current=_cell(item.target_text),
                suggestion=_cell(item.suggestion) or "—",
            )
        )
    cards = []
    for name, label in (
        ("critical", "Критичные"),
        ("high", "Высокие"),
        ("medium", "Средние"),
        ("low", "Низкие"),
    ):
        cards.append(
            f"<div class='card card-{name}'><b>{summary['by_severity'].get(name, 0)}</b><span>{label}</span></div>"
        )
    body = "\n".join(rows) or "<tr><td colspan='8'>Находок нет.</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{
  --bg:#10151c; --panel:#1a222d; --ink:#f4f7fb; --muted:#9aa8b8;
  --gold:#e6c07b; --line:#2c3847; --good:#8fd9b4; --bad:#ffb4a8;
  --critical:#e15b64; --high:#e6a15b; --medium:#d6c15a; --low:#7f93a8;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:15px/1.45 "Segoe UI", sans-serif; background:var(--bg); color:var(--ink); }}
header {{ padding:28px 32px 12px; }}
h1 {{ margin:0 0 6px; font-size:28px; letter-spacing:-0.03em; }}
.sub {{ color:var(--muted); }}
.score {{ color:var(--gold); font-weight:700; }}
.cards {{ display:flex; gap:12px; padding:8px 32px 18px; flex-wrap:wrap; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:14px 16px; min-width:120px; }}
.card b {{ display:block; font-size:26px; }}
.card span {{ color:var(--muted); }}
.card-critical b {{ color:var(--critical); }}
.card-high b {{ color:var(--high); }}
.card-medium b {{ color:var(--medium); }}
.filters {{ padding:0 32px 12px; display:flex; gap:8px; flex-wrap:wrap; }}
button {{ background:#243140; color:var(--ink); border:1px solid var(--line); border-radius:999px; padding:6px 12px; cursor:pointer; }}
button.on {{ border-color:var(--gold); color:var(--gold); }}
.wrap {{ padding:0 32px 40px; overflow:auto; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border-radius:14px; overflow:hidden; }}
th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
code {{ color:var(--gold); }}
.ctx {{ color:var(--muted); font-size:12px; }}
.mono {{ font-family:ui-monospace, monospace; white-space:pre-wrap; word-break:break-word; }}
.bad {{ color:var(--bad); }}
.good {{ color:var(--good); }}
.sev {{ border-radius:999px; padding:2px 8px; font-size:12px; }}
.sev-critical {{ background:#3d1c22; color:#ffb4bc; }}
.sev-high {{ background:#3d2c18; color:#ffd0a8; }}
.sev-medium {{ background:#333018; color:#f3e7a2; }}
.sev-low {{ background:#1d2733; color:#c5d2e0; }}
</style>
</head>
<body>
<header>
  <h1>{html.escape(title)}</h1>
  <div class="sub">TilTekser · оценка <span class="score">{summary["score"]}/100</span> · находок {summary["total"]}</div>
</header>
<section class="cards">{''.join(cards)}</section>
<div class="filters">
  <button class="on" data-filter="all">Все</button>
  <button data-filter="kk">Казахский</button>
  <button data-filter="uz">Узбекский</button>
  <button data-filter="critical">Только critical</button>
</div>
<div class="wrap">
<table>
<thead><tr><th>Уровень</th><th>Язык</th><th>Ключ</th><th>Проверка</th><th>Что не так</th><th>Источник</th><th>Сейчас</th><th>Эталон</th></tr></thead>
<tbody>
{body}
</tbody>
</table>
</div>
<script>
document.querySelectorAll("button[data-filter]").forEach((button) => {{
  button.addEventListener("click", () => {{
    document.querySelectorAll("button[data-filter]").forEach((item) => item.classList.remove("on"));
    button.classList.add("on");
    const filter = button.dataset.filter;
    document.querySelectorAll("tbody tr").forEach((row) => {{
      const visible = filter === "all"
        || row.dataset.lang === filter
        || row.dataset.sev === filter;
      row.style.display = visible ? "" : "none";
    }});
  }});
}});
</script>
</body>
</html>
"""


def _cell(value: str) -> str:
    if value is None:
        return ""
    return html.escape(value)


def _as_dict(item: Finding) -> dict:
    return {
        "id": item.finding_id,
        "checker": item.checker,
        "severity": item.severity,
        "language": item.language,
        "key": item.key,
        "message": item.message,
        "source": item.source_text,
        "current": item.target_text,
        "suggestion": item.suggestion,
        "context": item.context,
    }


def _bundle_json(bundle: Bundle) -> str:
    rows = [
        {
            "key": segment.key,
            "context": segment.context,
            **segment.texts,
        }
        for segment in bundle.segments
    ]
    return json.dumps(rows, ensure_ascii=False, indent=2)
