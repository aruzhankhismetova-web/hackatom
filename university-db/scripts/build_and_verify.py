#!/usr/bin/env python3
"""Build the university SQLite database and check the practice-work rules.

The script loads sql/schema.sql and sql/seed.sql, checks that data/*.csv
matches the loaded tables, rejects rows that break the stated constraints,
and runs every query in sql/queries.sql.
"""

from __future__ import annotations

import csv
import sqlite3
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "university.db"

TABLES = (
    "groups",
    "departments",
    "classrooms",
    "students",
    "teachers",
    "courses",
    "schedule",
    "grades",
)

QUERY_TITLES = {
    "students_in_group": "1. Students enrolled in group IT-21",
    "group_of_student": "2. Group of student 1001 (Aruzhan Aliyeva)",
    "courses_of_student": "3. Courses studied by student 1001",
    "grades_of_student": "4. Grades received by student 1001",
    "average_grade_of_student": "5. Average grade of student 1001",
    "teachers_of_course": "6. Teacher of Database Systems",
    "courses_of_teacher": "7. Courses taught by teacher 1 (Ayan Saparov)",
    "schedule_of_group": "8. Schedule of group IT-21",
    "schedule_of_teacher": "9. Schedule of teacher Ayan Saparov",
    "classroom_of_class": "10. Classroom for schedule record 1",
    "courses_of_department": "11. Courses offered by Computer Science",
    "students_per_group": "12. Students enrolled in each group",
    "students_with_highest_average": "13. Students with the highest average grade",
    "students_below_grade": "14. Students with a grade below 70",
    "available_classrooms": "15. Classrooms free on Monday 08:00–09:50",
}


class CheckFailure(Exception):
    """A practice-work check did not hold."""


def connect(path: Path | str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def script(conn: sqlite3.Connection, path: Path) -> None:
    conn.executescript(path.read_text(encoding="utf-8"))


def load_database(path: Path) -> sqlite3.Connection:
    if path.exists():
        path.unlink()
    conn = connect(path)
    script(conn, SQL_DIR / "schema.sql")
    script(conn, SQL_DIR / "seed.sql")
    return conn


def parse_queries(path: Path) -> list[tuple[str, str]]:
    queries: list[tuple[str, str]] = []
    name: str | None = None
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("-- name:"):
            if name is not None:
                queries.append((name, "\n".join(lines).strip()))
            name = raw.split(":", 1)[1].strip()
            lines = []
            continue
        if name is not None and not raw.startswith("--"):
            lines.append(raw)
    if name is not None:
        queries.append((name, "\n".join(lines).strip()))
    return queries


def expect_reject(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> None:
    """The statement must fail, and the sample data must stay unchanged."""
    before = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in TABLES
    }
    try:
        conn.execute("BEGIN")
        conn.execute(sql, params)
        conn.execute("ROLLBACK")
    except sqlite3.IntegrityError:
        conn.execute("ROLLBACK")
    else:
        raise CheckFailure(f"Expected the database to reject:\n{sql}")
    after = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in TABLES
    }
    if before != after:
        raise CheckFailure("A rejected change modified the sample data")


def check_row_counts(conn: sqlite3.Connection) -> None:
    total = 0
    for table in TABLES:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count != 15:
            raise CheckFailure(f"{table} has {count} rows, expected 15")
        total += count
    if total != 120:
        raise CheckFailure(f"Dataset has {total} rows, expected 120")


def check_csv_matches_database(conn: sqlite3.Connection) -> None:
    for table in TABLES:
        csv_path = DATA_DIR / f"{table}.csv"
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            csv_rows = [tuple(row[name] for name in fieldnames) for row in reader]
        quoted = ", ".join(fieldnames)
        db_rows = [
            tuple("" if value is None else str(value) for value in row)
            for row in conn.execute(
                f"SELECT {quoted} FROM {table} ORDER BY {fieldnames[0]}"
            )
        ]
        csv_rows.sort()
        db_rows.sort()
        if csv_rows != db_rows:
            raise CheckFailure(f"{csv_path.name} does not match the SQL seed")


def check_constraints(conn: sqlite3.Connection) -> None:
    expect_reject(
        conn,
        """
        INSERT INTO students (
            student_id, last_name, first_name, birth_date, gender, phone, email, group_id
        ) VALUES (2000, 'Test', 'Future', date('now', '+1 day'), 'F', '+7-707-1',
                  'future@student.university.example', 1)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO students (
            student_id, last_name, first_name, birth_date, gender, phone, email, group_id
        ) VALUES (2001, 'Test', 'Missing', '2004-01-01', 'F', '+7-707-2',
                  'missing.group@student.university.example', 999)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO teachers (
            teacher_id, first_name, last_name, academic_degree, phone, email, department_id
        ) VALUES (99, 'Test', 'Teacher', 'MSc', '+7-701-1', 'test.teacher@university.example', 999)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO courses (course_id, course_name, credits, semester, department_id)
        VALUES (99, 'Orphan Course', 3, 1, 999)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO courses (course_id, course_name, credits, semester, department_id)
        VALUES (98, 'Zero Credit Course', 0, 1, 1)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO classrooms (classroom_id, room_number, building, capacity)
        VALUES (99, '199', 'Building 1', 0)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO grades (grade_id, student_id, course_id, grade_value, grade_date)
        VALUES (99, 1001, 2, 101, '2026-06-01')
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO grades (grade_id, student_id, course_id, grade_value, grade_date)
        VALUES (98, 1001, 2, -1, '2026-06-01')
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO schedule (
            schedule_id, course_id, teacher_id, group_id, classroom_id,
            day_of_week, start_time, end_time
        ) VALUES (99, 1, 1, 2, 2, 'Monday', '10:00:00', '09:00:00')
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO students (
            student_id, last_name, first_name, birth_date, gender, phone, email, group_id
        ) VALUES (2002, 'Duplicate', 'Email', '2004-01-01', 'M', '+7-707-3',
                  'aruzhan.aliyeva@student.university.example', 1)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO schedule (
            schedule_id, course_id, teacher_id, group_id, classroom_id,
            day_of_week, start_time, end_time
        ) VALUES (97, 2, 2, 2, 1, 'Monday', '08:30:00', '09:20:00')
        """,
    )
    expect_reject(
        conn,
        """
        UPDATE schedule
        SET classroom_id = 1, day_of_week = 'Monday',
            start_time = '08:30:00', end_time = '09:20:00'
        WHERE schedule_id = 2
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO grades (grade_id, student_id, course_id, grade_value, grade_date)
        VALUES (97, 1001, 1, 80, '2026-05-01')
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO students (
            student_id, last_name, first_name, birth_date, gender, phone, email, group_id
        ) VALUES (2003, '   ', 'Blank', '2004-01-01', 'F', '+7-707-4',
                  'blank.name@student.university.example', 1)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO courses (course_id, course_name, credits, semester, department_id)
        VALUES (96, '', 3, 1, 1)
        """,
    )
    expect_reject(
        conn,
        """
        INSERT INTO groups (group_id, group_name, year_of_study, specialty)
        VALUES (99, '', 1, 'Software Engineering')
        """,
    )
    # A class may start at the moment the previous class in that room ends.
    conn.execute("BEGIN")
    conn.execute(
        """
        INSERT INTO schedule (
            schedule_id, course_id, teacher_id, group_id, classroom_id,
            day_of_week, start_time, end_time
        ) VALUES (96, 2, 2, 2, 1, 'Monday', '09:50:00', '11:20:00')
        """
    )
    conn.execute("ROLLBACK")


def run_queries(conn: sqlite3.Connection) -> list[tuple[str, list[str], list[tuple]]]:
    results = []
    for name, statement in parse_queries(SQL_DIR / "queries.sql"):
        if not statement:
            raise CheckFailure(f"Query {name} is empty")
        cursor = conn.execute(statement)
        columns = [item[0] for item in cursor.description or []]
        rows = [tuple(row) for row in cursor.fetchall()]
        results.append((name, columns, rows))
    if len(results) != 15:
        raise CheckFailure(f"Expected 15 queries, found {len(results)}")
    return results


def check_query_answers(results: dict[str, list[tuple]]) -> None:
    expected = {
        "students_in_group": [(1001, "Aliyeva", "Aruzhan", "IT-21")],
        "group_of_student": [
            (1001, "Aliyeva", "Aruzhan", 1, "IT-21", 1, "Software Engineering")
        ],
        "courses_of_student": [(1001, "Aruzhan Aliyeva", 1, "Database Systems", 5, 1)],
        "grades_of_student": [
            (1001, "Aruzhan Aliyeva", "Database Systems", 67, "2026-05-01")
        ],
        "average_grade_of_student": [(1001, "Aruzhan Aliyeva", 67.0)],
        "teachers_of_course": [(1, "Database Systems", 1, "Ayan Saparov", "MSc")],
        "courses_of_teacher": [(1, "Ayan Saparov", 1, "Database Systems", 5)],
        "schedule_of_group": [
            (
                "IT-21",
                "Monday",
                "08:00:00",
                "09:50:00",
                "Database Systems",
                "Ayan Saparov",
                "101",
                "Building 1",
            )
        ],
        "schedule_of_teacher": [
            (
                "Ayan Saparov",
                "Monday",
                "08:00:00",
                "09:50:00",
                "Database Systems",
                "IT-21",
                "101",
                "Building 1",
            )
        ],
        "classroom_of_class": [
            (
                1,
                "Database Systems",
                "IT-21",
                "Monday",
                "08:00:00",
                "09:50:00",
                1,
                "101",
                "Building 1",
            )
        ],
        "courses_of_department": [(
            "Computer Science",
            1,
            "Database Systems",
            5,
            1,
        )],
        "students_with_highest_average": [(1011, "Zhakupova", "Kamila", 96.0)],
        "students_below_grade": [
            (1006, "Tursyn", "Alikhan", "Object-Oriented Programming", 61, "2026-05-06"),
            (1012, "Abilov", "Sanzhar", "Project Management", 62, "2026-05-12"),
            (1001, "Aliyeva", "Aruzhan", "Database Systems", 67, "2026-05-01"),
            (1007, "Mukhanova", "Dana", "Web Development", 68, "2026-05-07"),
            (1013, "Kaliyeva", "Zarina", "Statistics", 69, "2026-05-13"),
        ],
    }
    for name, rows in expected.items():
        if results[name] != rows:
            raise CheckFailure(
                f"{name} returned {results[name]!r}, expected {rows!r}"
            )

    per_group = results["students_per_group"]
    if len(per_group) != 15 or any(row[3] != 1 for row in per_group):
        raise CheckFailure(f"Unexpected group sizes: {per_group!r}")

    free_rooms = [row[1] for row in results["available_classrooms"]]
    if "101" in free_rooms or len(free_rooms) != 14:
        raise CheckFailure(f"Unexpected free classrooms: {free_rooms!r}")


def write_download_bundle() -> None:
    """Copy the database and pack every dataset file into one zip."""
    downloads = ROOT / "downloads"
    downloads.mkdir(exist_ok=True)
    database_copy = downloads / "university.db"
    database_copy.write_bytes(DB_PATH.read_bytes())
    archive_path = downloads / "university-dataset.zip"
    prefix = "university-dataset"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / "data").glob("*.csv")):
            archive.write(path, f"{prefix}/data/{path.name}")
        for name in ("schema.sql", "seed.sql", "queries.sql"):
            archive.write(SQL_DIR / name, f"{prefix}/sql/{name}")
        archive.write(database_copy, f"{prefix}/university.db")
        archive.write(ROOT / "docs" / "subject-area.md", f"{prefix}/subject-area.md")
        archive.write(ROOT / "docs" / "query-results.md", f"{prefix}/query-results.md")


def write_report(executed: list[tuple[str, list[str], list[tuple]]]) -> None:
    lines = [
        "# Query results",
        "",
        "Results of `sql/queries.sql` against the 120-row sample dataset.",
        "",
    ]
    for name, columns, rows in executed:
        title = QUERY_TITLES.get(name, name)
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(value) for value in row) + " |")
        lines.append("")
    (ROOT / "docs" / "query-results.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    conn = load_database(DB_PATH)
    try:
        check_row_counts(conn)
        check_csv_matches_database(conn)
        check_constraints(conn)
        executed = run_queries(conn)
        check_query_answers({name: rows for name, _, rows in executed})
        write_report(executed)
    except CheckFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    write_download_bundle()
    print(f"OK: {DB_PATH}")
    print("8 tables, 120 rows, constraints enforced, 15 queries answered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
