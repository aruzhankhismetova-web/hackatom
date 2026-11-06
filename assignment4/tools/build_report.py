#!/usr/bin/env python3
"""Build the Assignment 4 Word report from the captured screenshots."""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor, Twips

ROOT = Path("/workspace/assignment4")
SHOTS = ROOT / "screenshots"
OUT = ROOT / "Assignment4_Sakhtasheva_Raikhan.docx"
NAVY = "1F4E79"


def set_run_font(run, size=12, bold=False, color=None, italic=False):
    run.font.name = "Times New Roman"
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), "Times New Roman")


def add_para(doc, text, size=12, bold=False, color=None, space_before=0, space_after=8, style=None, center=False):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.08
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    return p


def add_heading_text(doc, text, level):
    size = 16 if level == 1 else 13
    before = 16 if level == 1 else 12
    p = add_para(doc, text, size=size, bold=True, color=NAVY, space_before=before, space_after=6, style=f"Heading {level}")
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(item)
        set_run_font(run, size=12)


def add_figure(doc, filename, caption):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(SHOTS / filename), width=Inches(6.35))
    cap = add_para(doc, caption, size=10, bold=True, space_before=0, space_after=10)


def shade_cell(cell, fill):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_text(cell, text, bold=False, size=9, color=None, center=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)


def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), NAVY)
        borders.append(el)
    tblPr.append(borders)


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        shade_cell(cell, NAVY)
        set_cell_text(cell, header, bold=True, size=10, color="FFFFFF", center=True)
    for r, row in enumerate(rows, start=1):
        for c, text in enumerate(row):
            set_cell_text(table.rows[r].cells[c], text, size=9)
    for row in table.rows:
        for i, width in enumerate(widths):
            row.cells[i].width = Inches(width)
    # keep header row with the table
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    trPr.append(tblHeader)
    doc.add_paragraph()
    return table


def main():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.6)
    section.right_margin = Cm(1.6)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), "Times New Roman")

    add_para(doc, "Assignment 4. Software Maintenance, Security and Recovery", size=18, bold=True, color=NAVY, space_after=4)
    add_para(doc, "Темы 1.35, 1.37, 1.38, 1.39", size=13, space_after=2)
    add_para(doc, "Студент: Сахташева Райхан", size=12, space_after=2)
    add_para(doc, "Дата: 6 ноября 2026", size=12, space_after=2)
    add_para(doc, "Операционная система: Ubuntu 24.04.5 LTS, x86_64", size=12, space_after=8)
    add_para(
        doc,
        "Цель работы: потренироваться сопровождать установленные программы, проверять и ставить обновления, "
        "сохранять данные в резервную копию и восстанавливать их, разбирать типичные проблемы установки "
        "и настраивать параметры безопасности и конфиденциальности. Все версии, сообщения и снимки ниже "
        "сняты с этого компьютера. Подписи меню оставлены так, как они показаны на экране.",
    )

    add_heading_text(doc, "1. Сводная таблица приложений и инструментов", 1)
    add_para(
        doc,
        "В таблице собраны программы, с которыми выполнялась работа. Версии записаны по выводу команд "
        "google-chrome --version, dpkg-query, sqlite3 --version, htop --version, apt --version и по окну About.",
    )
    add_table(
        doc,
        ["Application", "Version", "Purpose", "Configuration performed", "Result"],
        [
            [
                "Google Chrome",
                "156.0.8078.47, затем 157.0.8103.38",
                "Просмотр страниц. Для задания выбран как программа, у которой проверяются обновление и настройки конфиденциальности.",
                "Пакет google-chrome-stable обновлён через apt. В отдельном профиле /home/ubuntu/.config/chrome-assignment4 закрыты камера, микрофон, геолокация, уведомления и правка файлов. Включена блокировка сторонних cookie и Do Not Track. Выключен пункт Improve search suggestions. Вход в аккаунт не выполнялся.",
                "apt завершился с кодом 0. На странице chrome://settings/help видна Version 157.0.8103.38 (Official Build) (x86_64). Репозиторий обновлений оставлен включённым.",
            ],
            [
                "DB Browser for SQLite",
                "3.12.2, пакет 3.12.2-3build2",
                "Графический просмотр базы SQLite.",
                "Версия проверена в окне About и в apt-cache policy. Обновление не ставилось: Candidate совпадает с Installed. Открыт восстановленный файл базы.",
                "На вкладке Browse Data видна таблица maintenance, 7 строк, в строке student имя Сахташева Райхан.",
            ],
            [
                "sqlite3",
                "3.45.1, пакет 3.45.1-1ubuntu2.8",
                "Командная оболочка базы. Через неё сделаны копия и восстановление.",
                "Создан файл data/maintenance.db. Команда .backup записала копию, .restore собрала базу заново в другом каталоге. Кандидат пакета 3.45.1-1ubuntu2.9 просмотрен в changelog и оставлен без установки.",
                "PRAGMA integrity_check вернул ok. SHA256 копии и восстановленного файла совпадают. SELECT вернул 7 строк.",
            ],
            [
                "htop",
                "3.3.0, пакет 3.3.0-4build1",
                "Просмотр процессов. Выбран как лишняя для этой работы программа, чтобы разобрать удаление.",
                "Выполнен только пробный запуск sudo apt-get -s remove htop. Само удаление не запускалось.",
                "Пакет остался установленным: htop 3.3.0-4build1. Обратных зависимостей нет.",
            ],
            [
                "python3-psutil",
                "5.9.8-2build2",
                "Недостающий модуль для скрипта проверки диска.",
                "Сначала скрипт tools/disk_report.py падал с ModuleNotFoundError. Пакет поставлен из репозитория Ubuntu командой sudo apt-get install python3-psutil.",
                "Повторный запуск завершился с кодом 0 и строкой RESULT space_ok. Модуль сообщает psutil 5.9.8.",
            ],
            [
                "apt",
                "2.8.3",
                "Установка и проверка пакетов.",
                "Через apt сняты версии, обновлён только google-chrome-stable и установлен python3-psutil.",
                "После обновления Chrome в списке кандидата стоит та же версия 157.0.8103.38-1. Остальные доступные обновления не ставились.",
            ],
        ],
        [1.25, 1.25, 1.45, 1.85, 1.55],
    )

    add_heading_text(doc, "2. Задание 1. Обновление программ и разбор удаления", 1)
    add_heading_text(doc, "2.1. Две программы и их версии", 2)
    add_para(
        doc,
        "Для проверки выбраны две уже установленные программы: Google Chrome и DB Browser for SQLite. "
        "Рядом сняты версии sqlite3, htop и apt, потому что они дальше используются для копии, разбора удаления и установки пакетов.",
    )
    add_bullets(
        doc,
        [
            "Команда google-chrome --version: Google Chrome 156.0.8078.47.",
            "apt-cache policy google-chrome-stable: Installed 156.0.8078.47-1, Candidate 157.0.8103.38-1.",
            "Пакет sqlitebrowser: 3.12.2-3build2. Окно About DB Browser for SQLite пишет Version 3.12.2, Qt Version 5.15.12, SQLite Version 3.45.1, архитектура x86_64.",
            "Команда sqlite3 --version: 3.45.1 2024-01-30 16:01:20 (64-bit). Пакеты sqlite3 и libsqlite3-0: 3.45.1-1ubuntu2.8.",
            "htop --version: htop 3.3.0. Пакет htop 3.3.0-4build1.",
            "apt --version: apt 2.8.3 (amd64).",
        ],
    )
    add_figure(doc, "01_versions_before.png", "Рисунок 1. Версии до обновления: Chrome 156.0.8078.47, sqlitebrowser 3.12.2-3build2, sqlite3 3.45.1, htop 3.3.0, apt 2.8.3.")
    add_figure(doc, "02_sqlitebrowser_about.png", "Рисунок 2. About DB Browser for SQLite: версия 3.12.2, SQLite Version 3.45.1, сборка для x86_64.")

    add_heading_text(doc, "2.2. Есть ли обновления", 2)
    add_para(
        doc,
        "Список apt list --upgradable на момент проверки содержал 24 обновляемых пакета, не считая строки заголовка. "
        "Среди них был google-chrome-stable. У DB Browser for SQLite обновления нет: в apt-cache policy поля Installed и Candidate оба равны 3.12.2-3build2, источник http://archive.ubuntu.com/ubuntu noble/universe.",
    )
    add_para(
        doc,
        "У пакета sqlite3 кандидат новее установленного: Installed 3.45.1-1ubuntu2.8, Candidate 3.45.1-1ubuntu2.9 (phased 60%). "
        "Строка версии самой библиотеки при этом остаётся 3.45.1. Этот пакет в работе не обновлялся: по заданию обновляется одно приложение, и им выбран Google Chrome. "
        "Текст changelog для кандидата sqlite3 прочитан командой apt-get changelog sqlite3. Первая запись, sqlite3 (3.45.1-1ubuntu2.9), описывает исправление сбоя в sqlite3MatchEName() при вложенных соединениях, LP #2087772.",
    )
    add_figure(doc, "03_chrome_package_info.png", "Рисунок 3. Сведения пакета-кандидата Google Chrome 157.0.8103.38-1 и строка, что у sqlitebrowser обновления нет.")
    add_figure(doc, "03b_sqlite_update_review.png", "Рисунок 4. У sqlitebrowser Installed совпадает с Candidate. Ниже changelog кандидата sqlite3 3.45.1-1ubuntu2.9.")

    add_heading_text(doc, "2.3. Что известно об обновлении Chrome", 2)
    add_para(doc, "Команда apt-cache show google-chrome-stable для кандидата показала такие поля:")
    add_bullets(
        doc,
        [
            "Package: google-chrome-stable, Version: 157.0.8103.38-1, Architecture: amd64.",
            "Installed-Size: 462822.",
            "Filename: pool/main/g/google-chrome-stable/google-chrome-stable_157.0.8103.38-1_amd64.deb.",
            "Size: 147633324.",
            "SHA256: a62b277dc03da2cff50cc04589deb66f6875be339c066d46adb49b49eedb629d.",
            "Description: The web browser from Google.",
            "Источник пакета: https://dl.google.com/linux/chrome-stable/deb stable/main.",
        ],
    )
    add_para(
        doc,
        "Установленный пакет на тот момент был google-chrome-stable 156.0.8078.47-1. "
        "Страница chrome://settings/help в запущенном браузере показывала Version 156.0.8078.47 (Official Build) (x86_64). "
        "Профиль для этой работы отдельный: /home/ubuntu/.config/chrome-assignment4. Профиль другой учебной работы не менялся.",
    )
    add_figure(doc, "07_chrome_help_before.png", "Рисунок 5. chrome://settings/help до обновления: Version 156.0.8078.47 (Official Build) (x86_64).")

    add_heading_text(doc, "2.4. Обновление Google Chrome", 2)
    add_para(
        doc,
        "Обновление выполнено командой sudo apt-get install -y --only-upgrade google-chrome-stable. "
        "Полный вывод сохранён в /workspace/assignment4/logs/chrome-upgrade.log.",
    )
    add_bullets(
        doc,
        [
            "apt написал: 1 upgraded, 0 newly installed, 0 to remove and 23 not upgraded.",
            "Need to get 148 MB of archives.",
            "After this operation, 7,903 kB of additional disk space will be used.",
            "Пакет скачан с https://dl.google.com/linux/chrome-stable/deb, 148 MB за 1 s.",
            "Unpacking google-chrome-stable (157.0.8103.38-1) over (156.0.8078.47-1).",
            "Setting up google-chrome-stable (157.0.8103.38-1). Код выхода apt: 0.",
            "В журнале есть строка debconf: delaying package configuration, since apt-utils is not installed. После неё пакет всё равно дошёл до Setting up, код выхода 0.",
            "После установки google-chrome --version печатает Google Chrome 157.0.8103.38, dpkg-query печатает google-chrome-stable 157.0.8103.38-1.",
            "ldd /opt/google/chrome/chrome не нашёл недостающих библиотек.",
        ],
    )
    add_para(
        doc,
        "Браузер запущен заново с тем же профилем. Страница chrome://settings/help показывает Version 157.0.8103.38 (Official Build) (x86_64). "
        "Повторный apt-cache policy google-chrome-stable: Installed и Candidate оба равны 157.0.8103.38-1. "
        "Файл репозитория /etc/apt/sources.list.d/google-chrome.sources оставлен на месте, адрес https://dl.google.com/linux/chrome-stable/deb/. "
        "Отдельного переключателя, который выключает обновления, на странице About Chrome нет, и этот источник не удалялся: обновления остаются доступными.",
    )
    add_figure(doc, "08_chrome_upgrade.png", "Рисунок 6. apt обновил google-chrome-stable с 156.0.8078.47-1 до 157.0.8103.38-1, код выхода 0.")
    add_figure(doc, "09_chrome_help_after.png", "Рисунок 7. chrome://settings/help после перезапуска: Version 157.0.8103.38 (Official Build) (x86_64).")

    add_heading_text(doc, "2.5. Разбор удаления htop", 2)
    add_para(
        doc,
        "Для разбора удаления взята программа htop 3.3.0. Это просмотрщик процессов. Для заданий этой работы он не нужен, "
        "системной частью рабочего стола он не является. Удаление не выполнялось. Запущена только проба sudo apt-get -s remove htop.",
    )
    add_bullets(
        doc,
        [
            "apt-cache rdepends --installed htop: список Reverse Depends пуст, от htop не зависит ни один установленный пакет.",
            "Каталога настроек /home/ubuntu/.config/htop нет, пользовательских настроек, которые потерялись бы при удалении, не найдено.",
            "Проба сообщает: The following packages will be REMOVED: htop. Итог: 0 upgraded, 0 newly installed, 1 to remove and 24 not upgraded. Remv htop [3.3.0-4build1].",
            "Там же apt пишет, что после удаления htop не понадобятся libnl-3-200 и libnl-genl-3-200, и предлагает sudo apt autoremove. Эта команда не запускалась.",
            "После пробы dpkg-query снова показывает htop 3.3.0-4build1.",
        ],
    )
    add_figure(doc, "04_htop_removal_sim.png", "Рисунок 8. Проба удаления htop. В конце пакет по-прежнему установлен: htop 3.3.0-4build1.")

    add_heading_text(doc, "2.6. Что проверять перед удалением", 2)
    add_para(doc, "Перед тем как снимать программу, по этой пробе видно четыре проверки.")
    add_bullets(
        doc,
        [
            "Нужна ли программа для учёбы или для системы. htop для этой работы не нужен, поэтому он годится для разбора. Редактор, браузер и средства рабочего стола для такого разбора не выбирались.",
            "Кто зависит от пакета. Это показывает apt-cache rdepends --installed. У htop зависимостей нет.",
            "Что именно снимет apt. Пробный ключ -s показывает пакет и предупреждает про autoremove. Пока список не прочитан, autoremove запускать не стоит: вместе с ненужным пакетом могут уйти библиотеки.",
            "Есть ли свои данные. У htop каталога настроек не было. Если каталог есть, его копируют до удаления. Ключ purge стирает и файлы настройки, поэтому его не использовали.",
        ],
    )
    add_para(doc, "htop оставлен установленным. Системные пакеты и программы, нужные для учёбы, не снимались.")

    add_heading_text(doc, "3. Задание 2. Резервная копия и восстановление", 1)
    add_heading_text(doc, "3.1. Что сохраняется", 2)
    add_para(
        doc,
        "Для копии выбран sqlite3: база хранится в одном файле, а команды .backup и .restore как раз записывают и возвращают этот файл. "
        "Живая база: /workspace/assignment4/data/maintenance.db. В ней одна таблица maintenance с полями id, item и detail. "
        "В строках записаны имя студента, дата, система, версии Chrome до и после обновления, версия DB Browser и пометка, что копия сделана командой .backup. "
        "Текст команд сохранён в /workspace/assignment4/tools/backup_restore.sh. Журнал первого прогона: /workspace/assignment4/logs/backup-restore.log.",
    )

    add_heading_text(doc, "3.2. Где лежит копия", 2)
    add_para(doc, "Копия записана отдельно от живой базы.")
    add_bullets(
        doc,
        [
            "Команда sqlite3 data/maintenance.db \".backup backups/maintenance_2026-11-06.db\".",
            "Рядом лежит текстовый экспорт /workspace/assignment4/backups/maintenance_2026-11-06.sql, полученный через .dump. В нём семь команд INSERT, первая строка — Сахташева Райхан.",
            "Суммы SHA256 записаны в /workspace/assignment4/backups/SHA256SUMS.",
            "Размер файла базы и файла копии — 8192 байта, SQL-файл — 637 байт.",
        ],
    )

    add_heading_text(doc, "3.3. Как восстановить и что проверено", 2)
    add_para(
        doc,
        "Восстановление сделано в отдельный файл, живая база не затиралась. "
        "Команда: sqlite3 /workspace/assignment4/recovery/maintenance_restored.db \".restore /workspace/assignment4/backups/maintenance_2026-11-06.db\". "
        "Если понадобится вернуть исходный файл, ту же команду .restore запускают уже для data/maintenance.db, предварительно закрыв программу, которая держит базу открытой. "
        "Текстовый .sql можно вернуть командой sqlite3 новый_файл < maintenance_2026-11-06.sql.",
    )
    add_para(doc, "Проверка на этой машине:")
    add_bullets(
        doc,
        [
            "PRAGMA integrity_check для копии и для восстановленного файла вернул ok.",
            "SHA256 копии и восстановленного файла совпадают: 3e9b580cf16d261b138d410f976456847f13db33d2bbadef277be0aa2fc1fbc3.",
            "SHA256 живой базы другой: fc272634d09cad1c7f93addd728e18b84b236f2c315ae164b4b9fc05cda968fb. Так бывает у .backup: содержимое строк то же, а служебные страницы файла отличаются. Сравнивались строки, а не только байты живого файла.",
            "SELECT id, item, detail FROM maintenance по восстановленной базе вернул 7 строк. Строка student содержит Сахташева Райхан, chrome_after содержит 157.0.8103.38.",
            "DB Browser for SQLite открыл /workspace/assignment4/recovery/maintenance_restored.db. На вкладке Browse Data таблица maintenance, счётчик 1-7 of 7.",
        ],
    )
    add_figure(doc, "21_backup_restore.png", "Рисунок 9. Копия, совпадающие SHA256 и SELECT из восстановленной базы: 7 строк, имя Сахташева Райхан.")
    add_figure(doc, "22_sqlitebrowser_restored.png", "Рисунок 10. DB Browser for SQLite, вкладка Browse Data: восстановленная таблица maintenance, 7 строк.")

    add_heading_text(doc, "4. Задание 3. Два сценария неполадок при установке", 1)
    add_para(doc, "Выбраны сценарий B (не хватает места на диске) и сценарий D (не хватает компонента). Оба разобраны командами на этой машине.")

    add_heading_text(doc, "4.1. Сценарий B. Недостаточно места на диске", 2)
    add_para(
        doc,
        "Проблема в этом сценарии: установщик отказывается продолжать, потому что на разделе мало свободного места. "
        "На этом компьютере такой ошибки не возникло. Проверка как раз показывает, почему установка прошла.",
    )
    add_para(doc, "Как найти причину. Команда df -hT / показала раздел /dev/vdc, тип ext4, Size 254G, Used 8.2G, Avail 246G, Use 4%, точка монтирования /. "
             "Команда du -xh -d 1 / показала крупные каталоги: /usr 4.6G, /home 2.4G, /opt 703M. "
             "Скрипт shutil.disk_usage до обновления Chrome напечатал free_gib=245.07.")
    add_para(
        doc,
        "Сколько места просит установка, видно до её запуска. Проба sudo apt-get -s --only-upgrade install google-chrome-stable "
        "назвала один пакет google-chrome-stable. Настоящая установка затем написала: Need to get 148 MB of archives и "
        "After this operation, 7,903 kB of additional disk space will be used. 148 МБ и 7,9 МБ намного меньше 246 ГБ свободных, поэтому места хватило, и apt завершился с кодом 0.",
    )
    add_para(doc, "Что делать, если df показал бы мало места. Сначала повторить df -hT и du, чтобы увидеть раздел и каталог. Затем освободить место безопасными шагами: sudo apt-get clean для кэша пакетов и удаление только тех программ, которые не нужны учёбе, после пробы apt-get -s remove. Системные каталоги и домашний каталог целиком для этого не стирают. После очистки снова смотрят df и только потом повторяют установку. Результат считается проверенным, когда у команды установки код выхода 0, а df по-прежнему показывает запас на том же разделе.")
    add_figure(doc, "05_disk_space.png", "Рисунок 11. df: свободно 246G из 254G. Проба обновления Chrome меняет один пакет.")

    add_heading_text(doc, "4.2. Сценарий D. Не хватает компонента", 2)
    add_para(
        doc,
        "Проблема: программе нужен дополнительный модуль, без него она не запускается. "
        "Для проверки использован скрипт /workspace/assignment4/tools/disk_report.py. Он читает занятость диска через стандартную библиотеку и память через модуль psutil.",
    )
    add_para(doc, "Как проявляется ошибка. Первый запуск напечатал:")
    add_bullets(
        doc,
        [
            "File \"/workspace/assignment4/tools/disk_report.py\", line 5, in <module>",
            "import psutil",
            "ModuleNotFoundError: No module named 'psutil'",
            "Код выхода: 1.",
        ],
    )
    add_para(
        doc,
        "Возможные причины такой ошибки: пакет не установлен, установлено другое имя пакета, либо не хватает библиотеки, от которой пакет зависит. "
        "Здесь apt-cache policy python3-psutil показал Installed: (none) и Candidate: 5.9.8-2build2 из http://archive.ubuntu.com/ubuntu noble/main. "
        "apt-cache depends python3-psutil перечислил зависимости python3 и libc6. Обе уже есть в системе, отдельную библиотеку докачивать было не нужно. "
        "Модуль искался в репозитории Ubuntu, а не скачивался произвольным файлом.",
    )
    add_para(
        doc,
        "Решение: sudo apt-get install -y python3-psutil. apt написал: The following NEW packages will be installed: python3-psutil. "
        "Need to get 195 kB of archives. After this operation, 1,166 kB of additional disk space will be used. "
        "Setting up python3-psutil (5.9.8-2build2). Код выхода apt: 0. В журнале снова есть строка про отсутствие apt-utils, и пакет после неё установлен.",
    )
    add_para(
        doc,
        "Проверка результата. Повторный запуск disk_report.py завершился с кодом 0. Он напечатал psutil 5.9.8, "
        "free_bytes 262668931072, free_gib 244.63, memory_total_bytes 16780623872 и RESULT space_ok. "
        "Отдельно после обновления Chrome команда ldd /opt/google/chrome/chrome не показала строк not found: у самого браузера недостающих библиотек нет.",
    )
    add_figure(doc, "06_missing_psutil.png", "Рисунок 12. До установки: ModuleNotFoundError: No module named 'psutil'. Пакет python3-psutil ещё не установлен.")
    add_figure(doc, "10_psutil_installed.png", "Рисунок 13. После установки python3-psutil 5.9.8-2build2 скрипт disk_report.py завершился с RESULT space_ok.")

    add_heading_text(doc, "5. Задание 4. Безопасность и конфиденциальность", 1)
    add_para(
        doc,
        "Разобран Google Chrome 157.0.8103.38. Настройки менялись в профиле /home/ubuntu/.config/chrome-assignment4. "
        "Вход в учётную запись Google не выполнялся. Страница You and Google показывает кнопку Sign in to Chrome и текст "
        "To get your passwords, bookmarks, and more on all your devices, sign in to Chrome.",
    )

    add_heading_text(doc, "5.1. Какие разрешения были", 2)
    add_para(
        doc,
        "Страница chrome://settings/content до изменений показывала в разделе Permissions:",
    )
    add_bullets(
        doc,
        [
            "Location — Sites can ask for your location.",
            "Camera — Sites can ask to use your camera.",
            "Microphone — Sites can ask to use your microphone.",
            "Notifications — Collapse unwanted requests (recommended). Это подпись способа показа запросов.",
            "Embedded content — Sites can ask to use information they've saved about you.",
        ],
    )
    add_para(
        doc,
        "Отдельные страницы дают более точные переключатели. Для камеры, микрофона, геолокации, уведомлений и правки файлов "
        "верхний пункт был Sites can ask…, нижний — Don't allow…. Для учёбы на этом компьютере камера, микрофон, координаты, "
        "уведомления сайтов и правка файлов сайтом не нужны, поэтому оставлен нижний пункт. "
        "Встроенное содержимое и доступ к USB, MIDI и похожим устройствам не менялись: они не требовались для задания и не открывались сайтам заранее.",
    )
    add_figure(doc, "11_site_settings_before.png", "Рисунок 14. Site settings до изменений: Location, Camera и Microphone в режиме Sites can ask.")

    add_heading_text(doc, "5.2. Что выключено", 2)
    add_para(doc, "После смены страницы выглядят так.")
    add_bullets(
        doc,
        [
            "Camera, chrome://settings/content/camera: выбран Don't allow sites to use your camera. Подпись на экране: Features that need a camera won't work. Списки Allowed и Not allowed пустые, No sites added.",
            "Microphone, chrome://settings/content/microphone: выбран Don't allow sites to use your microphone.",
            "Location, chrome://settings/content/location: выбран Don't allow sites to see your location.",
            "Notifications, chrome://settings/content/notifications: выбран Don't allow sites to send notifications. Пункт Sites can ask to send notifications не выбран.",
            "File editing, chrome://settings/content/filesystem: выбран Don't allow sites to edit files or folders on your device.",
        ],
    )
    add_para(
        doc,
        "Файл профиля Default/Preferences после этого содержит default_content_setting_values: "
        "media_stream_camera 2, media_stream_mic 2, geolocation 2, notifications 2, file_system_write_guard 2. "
        "Значение 2 у этих пунктов совпадает с выбранным на экране режимом Don't allow.",
    )
    add_para(
        doc,
        "На общем списке Site settings строки Location, Camera и Microphone сменились на Don't allow…. "
        "Строка Notifications по-прежнему говорит Collapse unwanted requests (recommended). Это другой параметр, How to show requests, "
        "он на странице уведомлений расположен ниже блока Default behavior и не переключался. Сам Default behavior уведомлений — Don't allow. "
        "В разделе Content того же списка появилась строка Third-party cookies — Third-party cookies are blocked.",
    )
    add_figure(doc, "12_camera.png", "Рисунок 15. Camera: выбран Don't allow sites to use your camera.")
    add_figure(doc, "13_microphone.png", "Рисунок 16. Microphone: выбран Don't allow sites to use your microphone.")
    add_figure(doc, "14_location.png", "Рисунок 17. Location: выбран Don't allow sites to see your location.")
    add_figure(doc, "15_notifications.png", "Рисунок 18. Notifications: выбран Don't allow sites to send notifications.")
    add_figure(doc, "16_file_editing.png", "Рисунок 19. File editing: выбран Don't allow sites to edit files or folders on your device.")
    add_figure(doc, "18_site_settings_after.png", "Рисунок 20. Site settings после изменений: Location, Camera и Microphone в режиме Don't allow, Third-party cookies are blocked.")

    add_heading_text(doc, "5.3. Конфиденциальность, учётная запись и обновления", 2)
    add_para(
        doc,
        "Страница chrome://settings/cookies. Был выбран пункт Allow third-party cookies. Стал выбран Block third-party cookies. "
        "На экране под ним написано: Sites can't use third-party cookies to personalize content and ads, and learn about actions you take on other sites. "
        "Там же сказано, что сайт по-прежнему может использовать свои cookie, а часть функций, которым нужны сторонние cookie, может не работать. "
        "В файле профиля profile.cookie_controls_mode равен 1, что соответствует выбранному на экране Block third-party cookies.",
    )
    add_para(
        doc,
        "Переключатель Send a \"Do Not Track\" request with your browsing traffic сначала был выключен. "
        "При включении Chrome открыл окно Do Not Track и попросил Confirm. В тексте окна сказано, что с трафиком уйдёт запрос, "
        "а подействует ли он, зависит от сайта. После кнопки Confirm переключатель стал синим, включённым. "
        "В файле профиля enable_do_not_track равен true. Подпись под переключателем остаётся: Sites use their discretion when responding to this request.",
    )
    add_figure(doc, "17_cookies.png", "Рисунок 21. Third-party cookies: выбран Block third-party cookies, переключатель Do Not Track включён.")
    add_para(
        doc,
        "Учётная запись. Страница chrome://settings/people называется You and Google. На ней нет имени пользователя, есть кнопка Sign in to Chrome. "
        "Логин и пароль не вводились. Пункт Allow Chrome sign-in на странице Google services оставлен включённым: он только разрешает показать предложение входа, сам вход не создаёт.",
    )
    add_figure(doc, "19_account.png", "Рисунок 22. You and Google: учётка не подключена, на экране кнопка Sign in to Chrome.")
    add_para(
        doc,
        "Сбор данных, страница chrome://settings/googleServices:",
    )
    add_bullets(
        doc,
        [
            "Help improve Chrome's features and performance — выключен. Подпись: Automatically sends usage statistics and crash reports to Google. Так и было до правки, переключатель оставлен выключенным.",
            "Make searches and browsing better — выключен. Подпись: Sends URLs of pages you visit to Google. Тоже уже был выключен.",
            "Enhanced spell check — выключен. Подпись: To fix spelling errors, Chrome sends the text you type in the browser to Google. Уже был выключен.",
            "Improve search suggestions — был включён, стал выключен. Подпись: When you type in the address bar or search box, Chrome sends what you type to your default search engine to get better suggestions. This is off in Incognito. В файле профиля search.suggest_enabled равен false.",
        ],
    )
    add_para(
        doc,
        "Защита от опасных сайтов не выключалась. Автоматические обновления не выключались: источник Google Chrome в /etc/apt/sources.list.d/google-chrome.sources на месте, "
        "и после установки кандидат apt совпадает с версией 157.0.8103.38-1. Выключение обновлений ослабило бы браузер, поэтому его не делали.",
    )
    add_figure(doc, "20_data_collection.png", "Рисунок 23. Google services: статистика, отправка адресов, проверка орфографии и поисковые подсказки выключены. Allow Chrome sign-in оставлен включённым.")
    add_para(
        doc,
        "Зачем так настроено. Сайт не получает камеру, микрофон, координаты, право слать уведомления и право править файлы. "
        "Сторонние cookie не связывают визиты между сайтами. Do Not Track добавляет просьбу не отслеживать, при этом сам Chrome пишет, что сайт может её проигнорировать. "
        "Выключенные переключатели Google services не отправляют статистику, адреса страниц, набираемый текст и строку поиска. "
        "Учётная запись не подключена, поэтому пароли и история не уходят в синхронизацию.",
    )

    add_heading_text(doc, "6. Что изменено и зачем", 1)
    add_para(doc, "Ниже только те значения, которые реально смотрелись. Для каждого указано прежнее состояние, новое и причина.")
    add_table(
        doc,
        ["Параметр", "Было", "Стало", "Зачем"],
        [
            [
                "Google Chrome",
                "156.0.8078.47 (пакет 156.0.8078.47-1)",
                "157.0.8103.38 (пакет 157.0.8103.38-1)",
                "В репозитории Google была более новая сборка. apt поставил её, код выхода 0. На странице About Chrome видна новая версия.",
            ],
            [
                "Camera",
                "Sites can ask to use your camera",
                "Don't allow sites to use your camera",
                "Для этой работы камера не нужна. Сайт не может её включить.",
            ],
            [
                "Microphone",
                "Sites can ask to use your microphone",
                "Don't allow sites to use your microphone",
                "Микрофон сайту не нужен. Запрос на него больше не показывается.",
            ],
            [
                "Location",
                "Sites can ask for your location",
                "Don't allow sites to see your location",
                "Координаты компьютера сайтам не отдаются.",
            ],
            [
                "Notifications",
                "Sites can ask to send notifications",
                "Don't allow sites to send notifications",
                "Сайты не запрашивают уведомления. Строка Collapse unwanted requests на общем списке относится к другому пункту и не менялась.",
            ],
            [
                "File editing",
                "Sites can ask to edit files and folders on your device",
                "Don't allow sites to edit files or folders on your device",
                "Сайт не получает право изменять файлы на диске.",
            ],
            [
                "Third-party cookies",
                "Allow third-party cookies",
                "Block third-party cookies",
                "Сторонние cookie не используются, чтобы связывать действия на разных сайтах. На списке Site settings написано Third-party cookies are blocked.",
            ],
            [
                "Do Not Track",
                "Переключатель выключен",
                "Переключатель включён после кнопки Confirm",
                "С запросами уходит просьба не отслеживать. Окно Chrome прямо говорит, что сайт может на неё не ответить.",
            ],
            [
                "Improve search suggestions",
                "Включён",
                "Выключен",
                "Текст из адресной строки не отправляется поисковой системе ради подсказок. В профиле search.suggest_enabled = false.",
            ],
            [
                "Help improve Chrome's features and performance; Make searches and browsing better; Enhanced spell check",
                "Все три уже выключены",
                "Оставлены выключенными",
                "Статистика, адреса открытых страниц и текст для проверки орфографии в Google не отправляются.",
            ],
            [
                "Вход в Chrome",
                "Учётная запись не подключена, кнопка Sign in to Chrome",
                "Вход не выполнялся. Allow Chrome sign-in оставлен включённым",
                "Пароли и история не синхронизируются. Переключатель только оставляет возможность входа, сам аккаунт не создаёт.",
            ],
            [
                "htop",
                "Установлен, 3.3.0-4build1",
                "Остался установленным",
                "Проба apt-get -s remove показала, что снялся бы только htop. Удаление не запускалось.",
            ],
            [
                "Репозиторий обновлений Chrome",
                "Файл google-chrome.sources указывает на dl.google.com",
                "Файл не удалялся и не отключался",
                "Обновления браузера остаются доступными. Выключать их значило бы дольше оставаться на старой сборке.",
            ],
        ],
        [1.55, 1.7, 1.85, 2.25],
    )

    add_heading_text(doc, "7. Заключение", 1)
    add_para(
        doc,
        "На Ubuntu 24.04.5 LTS проверены сопровождение программ, копия данных, два сценария установки и настройки конфиденциальности Chrome. "
        "Google Chrome обновлён с 156.0.8078.47 до 157.0.8103.38, пакет google-chrome-stable 157.0.8103.38-1, код выхода apt равен 0. "
        "У DB Browser for SQLite 3.12.2 обновления в репозитории нет. Кандидат sqlite3 3.45.1-1ubuntu2.9 просмотрен в changelog и не устанавливался.",
    )
    add_para(
        doc,
        "Удаление htop разобрано пробной командой sudo apt-get -s remove htop и не выполнено: пакет по-прежнему 3.3.0-4build1, обратных зависимостей нет, каталога настроек нет. "
        "Перед удалением любой программы нужно проверить, нужна ли она, кто от неё зависит, что покажет проба apt и есть ли пользовательские файлы.",
    )
    add_para(
        doc,
        "Резервная копия базы sqlite3 лежит в /workspace/assignment4/backups/maintenance_2026-11-06.db, текстовый экспорт — в maintenance_2026-11-06.sql. "
        "Восстановленный файл /workspace/assignment4/recovery/maintenance_restored.db имеет ту же сумму SHA256, integrity_check равен ok, SELECT возвращает 7 строк с именем Сахташева Райхан. "
        "Те же строки видны в DB Browser for SQLite.",
    )
    add_para(
        doc,
        "Свободное место на / — 246 ГБ из 254 ГБ. Обновлению Chrome хватило 148 МБ загрузки и 7,9 МБ на диске. "
        "Скрипт disk_report.py сначала не запускался: не было модуля psutil. Пакет python3-psutil 5.9.8-2build2 поставлен из репозитория Ubuntu, повторный запуск дал код 0 и RESULT space_ok.",
    )
    add_para(
        doc,
        "В Chrome для этого профиля закрыты камера, микрофон, геолокация, уведомления и правка файлов, заблокированы сторонние cookie, включён Do Not Track, "
        "выключены поисковые подсказки. Переключатели отправки статистики, адресов страниц и текста для орфографии уже были выключены и такими оставлены. "
        "Вход в аккаунт не делался. Источник обновлений Chrome не отключался.",
    )
    add_para(doc, "Студент: Сахташева Райхан")

    doc.save(OUT)
    print(OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
