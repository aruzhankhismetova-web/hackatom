"""Самодостаточная презентация для защиты. Листается стрелками."""

from __future__ import annotations

import html
from pathlib import Path


def write_slides(path: Path, *, before: dict, after: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    before_kk = before["by_language"].get("kk", 0)
    before_uz = before["by_language"].get("uz", 0)
    after_kk = after["by_language"].get("kk", 0)
    after_uz = after["by_language"].get("uz", 0)
    critical_before = before["by_severity"].get("critical", 0)
    critical_after = after["by_severity"].get("critical", 0)
    slides = [
        _slide(
            "01",
            "TilTekser",
            "Контроль качества казахской и узбекской локализации для Grand Mobile.",
            "<p class='lead'>Игрок в Алматы и Ташкенте не должен видеть сломанный плейсхолдер, русскую кальку и «Үйлар» вместо «Үйлер».</p>",
        ),
        _slide(
            "02",
            "Две задачи трека",
            "Инструмент ищет ошибки. Эталон казахского уже лежит в репозитории.",
            """
            <div class="grid">
              <article><h3>1. Автопоиск</h3><p>kk и uz: плейсхолдеры, теги, кодировка, пустые строки, сингармонизм, глоссарий, калька.</p></article>
              <article><h3>2. Выверенный kk</h3><p>Отдельный файл перевода, ревью каждой правки и место для подписи носителя.</p></article>
            </div>
            """,
        ),
        _slide(
            "03",
            "Что ломается в мобильном UI",
            "Ошибка локализации — это не только «некрасивое слово».",
            """
            <ul>
              <li><b>%s</b> и <b>{name}</b> нельзя терять: клиент падает или показывает чужое имя.</li>
              <li>Незакрытый <b>&lt;color&gt;</b> закрашивает весь экран.</li>
              <li>Ð¡Ð°ÑÑÐ¿ — битая кодировка, строка нечитаема.</li>
              <li>«Квест», «донат», «инвентарь» разъезжаются между экранами.</li>
              <li>Длинная кнопка обрезается на узком телефоне.</li>
            </ul>
            """,
        ),
        _slide(
            "04",
            "Как устроен прогон",
            "Сначала техника, потом язык, потом человек.",
            """
            <ol>
              <li>Парсер читает JSON, CSV, Excel или PO и склеивает en / ru / kk / uz по ключу.</li>
              <li>Технические чекеры сравнивают плейсхолдеры, теги и переводы строк с английским.</li>
              <li>Казахский чекер смотрит сингармонизм, чужие буквы и русские слова.</li>
              <li>Узбекский чекер ждёт латиницу и апостроф oʻ / gʻ.</li>
              <li>Глоссарий держит один термин на всю игру.</li>
              <li>Модель подключается только если есть API-ключ и не подменяет эти правила.</li>
            </ol>
            """,
        ),
        _slide(
            "05",
            "Цифры учебного корпуса",
            "Один и тот же прогон до правки и после эталона kk.",
            f"""
            <div class="grid">
              <article><h3>{before['total']}</h3><p>находок до правки, оценка {before['score']}/100. Из них critical: {critical_before}. kk: {before_kk}, uz: {before_uz}.</p></article>
              <article><h3>{after_kk} kk</h3><p>находок в казахском после эталона. В uz осталось {after_uz}, из них critical {critical_after}: это ещё работа носителя узбекского.</p></article>
            </div>
            <p class="lead">Казахский эталон проходит те же чекеры, которыми мы ловим баги. Серьёзных kk-находок после правки нет.</p>
            """,
        ),
        _slide(
            "06",
            "Казахский, которым можно играть",
            "Не подстрочник, а язык интерфейса.",
            """
            <ul>
              <li>Играть → <b>Ойнау</b>, настройки → <b>Баптаулар</b>, отмена → <b>Бас тарту</b>.</li>
              <li>Квест → <b>тапсырма</b>, инвентарь → <b>заттар</b>, донат → <b>алтын</b>, кейс → <b>сандық</b>.</li>
              <li>Үйлер, үйге, достар — ряд и согласный окончания проверяются правилом, не «на глаз».</li>
              <li>Гараж, сервер и полиция оставлены: так эти слова уже живут в игре.</li>
              <li>Каждая правка записана в <b>data/corrected/review.csv</b> парой «было → стало».</li>
            </ul>
            """,
        ),
        _slide(
            "07",
            "Запуск за одну команду",
            "Зависимостей для отчёта нет: хватает Python 3.10+.",
            """
            <pre>python -m qazaq_loc_qa demo
python -m qazaq_loc_qa check data/sample/strings.json
pip install -r requirements.txt
streamlit run app.py</pre>
            <p class="lead">Веб-интерфейс принимает свой JSON, CSV, XLSX или PO и отдаёт HTML-отчёт и исправленный kk.</p>
            """,
        ),
        _slide(
            "08",
            "Граница инструмента",
            "Чекер не заменяет редактора. Он не даёт багу доехать до билда.",
            """
            <ul>
              <li>Смысловые тонкости модель смотрит только по запросу и только как второй слой.</li>
              <li>Узбекский эталон в репозитории — рекомендация. Подпись носителя uz в треке не требуется, для kk место подписи есть.</li>
              <li>Учебный корпус повторяет форматы и баги мобильной локализации. Это не выгрузка из клиента Grand Mobile.</li>
              <li>Студии инструмент нужен в CI: critical по плейсхолдерам и тегам блокирует сборку.</li>
            </ul>
            """,
        ),
    ]
    path.write_text(_document(slides), encoding="utf-8")


def _slide(index: str, title: str, subtitle: str, body: str) -> str:
    return f"""
    <section class="slide">
      <p class="idx">{html.escape(index)}</p>
      <h2>{html.escape(title)}</h2>
      <p class="sub">{html.escape(subtitle)}</p>
      {body}
    </section>
    """


def _document(slides: list[str]) -> str:
    joined = "\n".join(slides)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TilTekser — защита</title>
<style>
:root {{ --bg:#10151c; --ink:#f4f7fb; --muted:#9aa8b8; --gold:#e6c07b; --panel:#1b2430; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:18px/1.45 "Segoe UI", sans-serif; }}
.deck {{ height:100vh; }}
.slide {{ display:none; min-height:100vh; padding:64px 72px; }}
.slide.active {{ display:block; }}
.idx {{ color:var(--gold); letter-spacing:.18em; font-size:13px; margin:0; }}
h2 {{ font-size:52px; line-height:1.05; margin:8px 0 12px; letter-spacing:-.04em; }}
.sub {{ color:var(--muted); font-size:22px; max-width:860px; }}
.lead {{ max-width:820px; }}
ul, ol {{ max-width:860px; padding-left:22px; }}
li {{ margin:8px 0; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; max-width:920px; }}
article {{ background:var(--panel); border-radius:16px; padding:18px 20px; }}
article h3 {{ margin:0 0 8px; font-size:40px; color:var(--gold); }}
pre {{ background:#0c1016; padding:16px 18px; border-radius:12px; overflow:auto; max-width:860px; }}
.nav {{ position:fixed; right:24px; bottom:20px; color:var(--muted); font-size:14px; }}
@media (max-width:800px) {{
  .slide {{ padding:32px 20px; }}
  h2 {{ font-size:34px; }}
  .grid {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<div class="deck">
{joined}
</div>
<div class="nav"><span id="pos"></span> · стрелки</div>
<script>
const slides = Array.from(document.querySelectorAll(".slide"));
let index = 0;
function show(next) {{
  index = Math.max(0, Math.min(slides.length - 1, next));
  slides.forEach((slide, i) => slide.classList.toggle("active", i === index));
  document.getElementById("pos").textContent = (index + 1) + " / " + slides.length;
}}
document.addEventListener("keydown", (event) => {{
  if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " ") show(index + 1);
  if (event.key === "ArrowLeft" || event.key === "PageUp") show(index - 1);
}});
show(0);
</script>
</body>
</html>
"""
