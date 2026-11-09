# University educational-process dataset

Structured dataset for Practice Work 1–2: students, groups, teachers, departments, courses, classrooms, schedules, and grades.

The sample is fictional. It has 8 tables and 120 rows (15 in each table). Phone numbers that were split across lines in the source table are stored as one value, for example `+7-707-2000000`.

## Layout

| Path | Contents |
| --- | --- |
| `university-db/sql/schema.sql` | Tables, keys, checks, and the classroom-overlap rule |
| `university-db/sql/seed.sql` | The 120 sample rows |
| `university-db/sql/queries.sql` | The 15 questions, each with one worked example |
| `university-db/data/*.csv` | The same rows, one file per table |
| `university-db/docs/subject-area.md` | Entities, relationships, constraints, and access |
| `university-db/docs/query-results.md` | Answers produced from the sample |

## Build and check

Python 3 and SQLite are enough. No packages are installed.

```bash
python3 university-db/scripts/build_and_verify.py
```

The script writes `university-db/university.db`, checks that the CSV files match the SQL seed, rejects rows that break the constraints, and runs all 15 queries.

Open the file with SQLite:

```bash
sqlite3 university-db/university.db
```

Foreign keys are declared in the schema. Turn them on for a manual session:

```sql
PRAGMA foreign_keys = ON;
```

## Worked examples

With this sample, each group has one student and one class.

- Group IT-21 is Aruzhan Aliyeva. She studies Database Systems with Ayan Saparov, Mondays 08:00–09:50 in room 101, Building 1, and her grade is 67.
- The highest average is 96, Kamila Zhakupova.
- Grades below 70 belong to Alikhan Tursyn (61), Sanzhar Abilov (62), Aruzhan Aliyeva (67), Dana Mukhanova (68), and Zarina Kaliyeva (69).
- On Monday 08:00–09:50, room 101 is taken and the other 14 rooms are free.
