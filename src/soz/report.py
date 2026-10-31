"""JSON- и HTML-отчёт для просмотра находок без отдельного сервера."""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

from soz.models import RunResult

_SEVERITY_LABEL = {
    "critical": "критично",
    "high": "важно",
    "medium": "средне",
    "info": "заметка",
}


def write_reports(result: RunResult, directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "report.json"
    html_path = directory / "report.html"
    json_path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    html_path.write_text(render_html(result), encoding="utf-8")
    return json_path, html_path


def render_html(result: RunResult) -> str:
    counts = Counter(item.severity for item in result.findings)
    engines = Counter(item.engine for item in result.findings)
    rows = "\n".join(_row(item) for item in result.findings) or (
        "<tr><td colspan='7'>Находок нет.</td></tr>"
    )
    unresolved = ", ".join(html.escape(item) for item in result.ai.unresolved) or "—"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Sóz — отчёт локализации</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1c1915;
      --muted: #5c564e;
      --line: #e4ddd2;
      --paper: #faf7f2;
      --card: #fffdf8;
      --critical: #9f2d2d;
      --high: #9a5b12;
      --medium: #3d5a80;
      --info: #5c564e;
    }}
    body {{
      margin: 0;
      font: 16px/1.5 "Iowan Old Style", Palatino, "Palatino Linotype", serif;
      color: var(--ink);
      background: var(--paper);
    }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1 {{ font-size: 2rem; margin: 0 0 8px; }}
    h2 {{ font-size: 1.25rem; margin: 28px 0 8px; }}
    p {{ margin: 0 0 12px; }}
    .muted {{ color: var(--muted); }}
    .stats {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0; }}
    .stat {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      min-width: 120px;
    }}
    .stat b {{ display: block; font-size: 1.4rem; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card); }}
    th, td {{
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      padding: 8px 10px;
      font-size: 0.95rem;
    }}
    th {{ font: 600 0.78rem/1.3 sans-serif; letter-spacing: 0.04em; text-transform: uppercase; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.86rem; }}
    .critical {{ color: var(--critical); }}
    .high {{ color: var(--high); }}
    .medium {{ color: var(--medium); }}
    .info {{ color: var(--info); }}
  </style>
</head>
<body>
<main>
  <h1>Sóz · Алтын Жол</h1>
  <p class="muted">Техническая проверка, глоссарий и смысловой слой. Промпт {html.escape(result.ai.prompt_version)}, режим {html.escape(result.ai.mode)}{(", модель " + html.escape(result.ai.model)) if result.ai.model else ""}.</p>
  <section class="stats">
    <div class="stat"><b>{len(result.entries)}</b>строк</div>
    <div class="stat"><b>{len(result.findings)}</b>находок</div>
    <div class="stat"><b>{counts.get("critical", 0)}</b>критичных</div>
    <div class="stat"><b>{engines.get("ai", 0)}</b>смысловых</div>
    <div class="stat"><b>{engines.get("glossary", 0)}</b>по глоссарию</div>
    <div class="stat"><b>{result.ai.guardrail_dropped}</b>отсеяно ограждениями</div>
  </section>
  <h2>Как устроен смысловой слой</h2>
  <p>Плейсхолдеры, теги и үндестік модель не перепроверяет. В запрос уходит контекст строки, срез глоссария и токены ⟦n⟧ вместо %s и {{name}}. Ответ без правки — пустой список. Подсказка с «Сіз сыйлық алдың», со сломанным токеном или с запрещённым термином в отчёт не попадает.</p>
  <p class="muted">Вызовов модели: {result.ai.llm_called}. Смысловой слой сознательно промолчал: {result.ai.silent_skipped}. Без готовой правки: {unresolved}.</p>
  <h2>Находки</h2>
  <table>
    <thead>
      <tr>
        <th>Важность</th><th>Слой</th><th>Код</th><th>Ключ</th><th>Сейчас</th><th>Правка</th><th>Почему</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</main>
</body>
</html>
"""


def _row(item: object) -> str:
    severity = html.escape(item.severity)
    suggestion = html.escape(item.suggestion) if item.suggestion else "—"
    return (
        "<tr>"
        f"<td class='{severity}'>{_SEVERITY_LABEL.get(item.severity, severity)}</td>"
        f"<td>{html.escape(item.engine)}</td>"
        f"<td><code>{html.escape(item.code)}</code></td>"
        f"<td><code>{html.escape(item.key)}</code><br><span class='muted'>{html.escape(item.locale)} · {html.escape(item.context)}</span></td>"
        f"<td>{html.escape(item.target)}</td>"
        f"<td>{suggestion}</td>"
        f"<td>{html.escape(item.message)}</td>"
        "</tr>"
    )
