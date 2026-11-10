# Practical Work №7–10

Data Sorting, Filtering, SQL Queries and Joining Tables

## Contents

| Path | Description |
|------|-------------|
| `data/University_Database.xlsx` | Updated Excel workbook with all tables + Part 1 result sheets |
| `data/university.db` | SQLite database with the same data |
| `sql/university_queries.sql` | Full SQL script (schema, inserts, all queries) |
| `screenshots/` | Screenshots of Excel operations and SQL results |
| `report/Practical_Work_7_10_Report.docx` | Short report, part reports, six answers, conclusion |
| `QUERY_RESULTS.md` | Text reference of every query result |

## How to re-run SQL

```bash
sqlite3 data/university.db < sql/university_queries.sql
```

Or regenerate everything:

```bash
python3 generate_all.py
```
