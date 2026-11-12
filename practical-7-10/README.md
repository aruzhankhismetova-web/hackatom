# Practical Work 7–10

Sorting, filtering, SQL queries and joins for the university database from Practice Work 2.

The task sheet says **Subjects** and **grade**. In this database the subject table is **Courses**, and the mark is **grade_value** (0–100).

## What to hand in

- `University_Database.xlsx`
- `sql/practical_work_7_10.sql`
- `report/Practical_Work_7-10.docx` (the same report is also a PDF and an HTML page)
- `screenshots/` (the figures are already inside the Word report)

The database file is `db/university.sqlite`.

## How to change the examples

The saved results use group **1 (IT-21)**, last name **Nazerke**, student id **1001**, and the two-condition filter **gender F and group_id <= 5**. Student 1001 is Akhmet Nazerke.

### In Excel or Google Sheets

Open `University_Database.xlsx`.

- Sort and filter with the header arrows on **Students**. That is the Topic 7 method.
- Or change the yellow cells on **Settings**. The orange **Live_** sheets use `SORT` and `FILTER` and update in Excel 365 and Google Sheets. If a Live sheet shows `#NAME?`, use the green saved sheets instead.
- Type your group in the yellow **Your group** cell before you submit.

### In SQLite

Open `db/university.sqlite` in SQLiteStudio or DB Browser, then open `sql/practical_work_7_10.sql`.

1. Edit the `INSERT INTO settings` block (it is marked **ADJUST THIS INSERT**).
2. Run the section **Queries that read the settings table**.
3. The extra questions from Practice Work 1 are at the end of the same file. They use the same settings row.

From a terminal, inside this folder:

```bash
sqlite3 db/university.sqlite
```

### Rebuild the workbook, screenshots and report together

Edit the **ADJUST** block at the top of `adjust_here.py` (group, search name, student id, gender, and your own group). Names, courses and grades are in the same file. Then run:

```bash
python3 build.py
```

`build.py` overwrites the workbook, the SQL script, the screenshots and the report. Change the Word report only after the last rebuild.

Packages used by the rebuild: `openpyxl`, `pillow`, `python-docx` (`requirements.txt`).
