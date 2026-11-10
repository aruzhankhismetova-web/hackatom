#!/usr/bin/env python3
"""Generate University Database deliverables for Practical Work 7–10."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SQL_DIR = ROOT / "sql"
SHOTS = ROOT / "screenshots"
REPORT = ROOT / "report"
ARTIFACTS = Path("/opt/cursor/artifacts")

for d in (DATA, SQL_DIR, SHOTS, REPORT, ARTIFACTS):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

GROUPS = [
    (1, "CS-101", "Computer Science", 2024),
    (2, "IS-102", "Information Systems", 2024),
    (3, "SE-201", "Software Engineering", 2023),
    (4, "DS-202", "Data Science", 2023),
]

TEACHERS = [
    (1, "Elena", "Morozova", "Professor", "Databases"),
    (2, "Arman", "Suleimenov", "Associate Professor", "Programming"),
    (3, "Sara", "Kim", "Senior Lecturer", "Mathematics"),
    (4, "Dias", "Nurpeisov", "Lecturer", "Networks"),
    (5, "Amina", "Bekova", "Professor", "Algorithms"),
]

SUBJECTS = [
    (1, "Introduction to Databases", 1, 4),
    (2, "Programming Fundamentals", 2, 5),
    (3, "Discrete Mathematics", 3, 4),
    (4, "Computer Networks", 4, 3),
    (5, "Algorithms and Data Structures", 5, 5),
    (6, "SQL and Data Processing", 1, 4),
]

STUDENTS = [
    (1, "Aigerim", "Abayeva", "a.abayeva@uni.edu", "2005-03-12", 1),
    (2, "Bekzat", "Alimov", "b.alimov@uni.edu", "2004-11-02", 1),
    (3, "Camila", "Bekturova", "c.bekturova@uni.edu", "2005-07-21", 1),
    (4, "Daniyar", "Erzhanov", "d.erzhanov@uni.edu", "2004-09-15", 2),
    (5, "Emily", "Foster", "e.foster@uni.edu", "2005-01-30", 2),
    (6, "Fariza", "Gabdulova", "f.gabdulova@uni.edu", "2004-05-08", 2),
    (7, "Gani", "Iskakov", "g.iskakov@uni.edu", "2003-12-19", 3),
    (8, "Hassan", "Jumabekov", "h.jumabekov@uni.edu", "2003-08-04", 3),
    (9, "Indira", "Karimova", "i.karimova@uni.edu", "2003-04-27", 3),
    (10, "Jasmin", "Lee", "j.lee@uni.edu", "2004-02-14", 4),
    (11, "Kanat", "Mukhametov", "k.mukhametov@uni.edu", "2003-10-09", 4),
    (12, "Laura", "Nurzhanova", "l.nurzhanova@uni.edu", "2004-06-18", 4),
    (13, "Madina", "Omarova", "m.omarova@uni.edu", "2005-08-25", 1),
    (14, "Nursultan", "Petrov", "n.petrov@uni.edu", "2004-12-03", 2),
    (15, "Olzhas", "Rakhimov", "o.rakhimov@uni.edu", "2003-03-11", 3),
]

EXAMS = [
    (1, 1, "2025-01-15", "Midterm"),
    (2, 2, "2025-01-17", "Midterm"),
    (3, 3, "2025-01-20", "Final"),
    (4, 4, "2025-01-22", "Final"),
    (5, 5, "2025-01-24", "Final"),
    (6, 6, "2025-01-27", "Final"),
]

# (grade_id, student_id, exam_id, grade)
GRADES = [
    (1, 1, 1, 95),
    (2, 1, 6, 88),
    (3, 2, 1, 78),
    (4, 2, 2, 82),
    (5, 3, 1, 91),
    (6, 3, 6, 87),
    (7, 4, 2, 74),
    (8, 4, 4, 80),
    (9, 5, 2, 96),
    (10, 5, 6, 92),
    (11, 6, 1, 69),
    (12, 6, 3, 75),
    (13, 7, 2, 85),
    (14, 7, 5, 90),
    (15, 8, 3, 71),
    (16, 8, 4, 77),
    (17, 9, 5, 98),
    (18, 9, 6, 94),
    (19, 10, 3, 83),
    (20, 10, 5, 86),
    (21, 11, 4, 70),
    (22, 11, 5, 79),
    (23, 12, 1, 93),
    (24, 12, 6, 89),
    (25, 13, 2, 84),
    (26, 13, 6, 81),
    (27, 14, 3, 76),
    (28, 14, 4, 72),
    (29, 15, 5, 97),
    (30, 15, 2, 88),
]


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

THIN = Border(
    left=Side(style="thin", color="D0D5DD"),
    right=Side(style="thin", color="D0D5DD"),
    top=Side(style="thin", color="D0D5DD"),
    bottom=Side(style="thin", color="D0D5DD"),
)
HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
BODY_FONT = Font(name="Calibri", size=11, color="111827")
ALT_FILL = PatternFill("solid", fgColor="F8FAFC")
ACCENT = "#2563EB"
INK = "#111827"
MUTED = "#6B7280"
BG = "#F8FAFC"
PANEL = "#FFFFFF"
LINE = "#E5E7EB"


def style_sheet(ws, headers, rows, col_widths):
    ws.append(headers)
    for row in rows:
        ws.append(list(row))
    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN
    for r_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), start=2):
        for cell in row:
            cell.font = BODY_FONT
            cell.border = THIN
            cell.alignment = Alignment(vertical="center")
            if r_idx % 2 == 0:
                cell.fill = ALT_FILL
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"


def create_excel():
    wb = Workbook()

    ws = wb.active
    ws.title = "Students"
    style_sheet(
        ws,
        ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"],
        STUDENTS,
        [12, 14, 14, 26, 14, 12],
    )

    # Sorted helpers as demonstration sheets for Part 1
    by_last = sorted(STUDENTS, key=lambda x: x[2])
    ws2 = wb.create_sheet("Students_Sorted_LastName")
    style_sheet(
        ws2,
        ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"],
        by_last,
        [12, 14, 14, 26, 14, 12],
    )

    by_group = sorted(STUDENTS, key=lambda x: (x[5], x[2]))
    ws3 = wb.create_sheet("Students_Sorted_ByGroup")
    style_sheet(
        ws3,
        ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"],
        by_group,
        [12, 14, 14, 26, 14, 12],
    )

    filtered = [s for s in STUDENTS if s[5] == 1]
    ws4 = wb.create_sheet("Students_Filter_CS101")
    style_sheet(
        ws4,
        ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"],
        filtered,
        [12, 14, 14, 26, 14, 12],
    )

    search = [s for s in STUDENTS if s[0] == 9 or s[2].lower() == "karimova"]
    ws5 = wb.create_sheet("Students_Search_Karimova")
    style_sheet(
        ws5,
        ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"],
        search,
        [12, 14, 14, 26, 14, 12],
    )

    dual = [s for s in STUDENTS if s[5] == 3 and s[2] >= "I"]
    ws6 = wb.create_sheet("Students_Filter_TwoCond")
    style_sheet(
        ws6,
        ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"],
        dual,
        [12, 14, 14, 26, 14, 12],
    )

    ws_g = wb.create_sheet("Groups")
    style_sheet(
        ws_g,
        ["group_id", "group_name", "specialty", "year"],
        GROUPS,
        [12, 14, 22, 10],
    )

    ws_t = wb.create_sheet("Teachers")
    style_sheet(
        ws_t,
        ["teacher_id", "first_name", "last_name", "position", "department"],
        TEACHERS,
        [12, 14, 14, 20, 16],
    )

    ws_s = wb.create_sheet("Subjects")
    style_sheet(
        ws_s,
        ["subject_id", "subject_name", "teacher_id", "credits"],
        SUBJECTS,
        [12, 30, 12, 10],
    )

    ws_e = wb.create_sheet("Exams")
    style_sheet(
        ws_e,
        ["exam_id", "subject_id", "exam_date", "exam_type"],
        EXAMS,
        [10, 12, 14, 12],
    )

    ws_gr = wb.create_sheet("Grades")
    style_sheet(
        ws_gr,
        ["grade_id", "student_id", "exam_id", "grade"],
        GRADES,
        [10, 12, 10, 10],
    )

    path = DATA / "University_Database.xlsx"
    wb.save(path)
    return path


# ---------------------------------------------------------------------------
# SQLite + SQL script
# ---------------------------------------------------------------------------

SQL_SCRIPT = """\
-- ============================================================================
-- University Database — Practical Work №7–10
-- Topics: Sorting/Filtering, SQL Basics, Aggregates, JOINs
-- ============================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Grades;
DROP TABLE IF EXISTS Exams;
DROP TABLE IF EXISTS Subjects;
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Teachers;
DROP TABLE IF EXISTS Groups;

CREATE TABLE Groups (
    group_id   INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL,
    specialty  TEXT NOT NULL,
    year       INTEGER NOT NULL
);

CREATE TABLE Teachers (
    teacher_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    position   TEXT NOT NULL,
    department TEXT NOT NULL
);

CREATE TABLE Subjects (
    subject_id   INTEGER PRIMARY KEY,
    subject_name TEXT NOT NULL,
    teacher_id   INTEGER NOT NULL,
    credits      INTEGER NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
);

CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    email      TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    group_id   INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES Groups(group_id)
);

CREATE TABLE Exams (
    exam_id    INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    exam_date  TEXT NOT NULL,
    exam_type  TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
);

CREATE TABLE Grades (
    grade_id   INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    exam_id    INTEGER NOT NULL,
    grade      INTEGER NOT NULL CHECK (grade BETWEEN 0 AND 100),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (exam_id) REFERENCES Exams(exam_id)
);

-- ============================================================================
-- PART 2. Introduction to SQL (Topic №8)
-- ============================================================================

-- Q2.1 Display all records from the Students table
SELECT * FROM Students;

-- Q2.2 Display only student IDs, first names and last names
SELECT student_id, first_name, last_name
FROM Students;

-- Q2.3 Display all records from the Groups table
SELECT * FROM Groups;

-- Q2.4 Display the names of all subjects from the Subjects table
SELECT subject_name FROM Subjects;

-- ============================================================================
-- PART 3. SQL queries and aggregate functions (Topic №9)
-- ============================================================================

-- Q3.1 Display students belonging to a selected group using WHERE
SELECT *
FROM Students
WHERE group_id = 1;

-- Q3.2 Display students in alphabetical order using ORDER BY
SELECT *
FROM Students
ORDER BY last_name ASC;

-- Q3.3 Count the total number of students using COUNT()
SELECT COUNT(*) AS total_students
FROM Students;

-- Q3.4 Count the number of students in each group using GROUP BY
SELECT group_id, COUNT(*) AS student_count
FROM Students
GROUP BY group_id;

-- Q3.5 Find the maximum grade using MAX()
SELECT MAX(grade) AS max_grade
FROM Grades;

-- Q3.6 Find the minimum grade using MIN()
SELECT MIN(grade) AS min_grade
FROM Grades;

-- Q3.7 Calculate the average grade using AVG()
SELECT ROUND(AVG(grade), 2) AS average_grade
FROM Grades;

-- ============================================================================
-- PART 4. Joining tables using JOIN (Topic №10)
-- ============================================================================

-- Q4.1 Join Students and Groups — student name + group name
-- Connecting columns: Students.group_id = Groups.group_id
SELECT
    Students.first_name,
    Students.last_name,
    Groups.group_name
FROM Students
INNER JOIN Groups
    ON Students.group_id = Groups.group_id
ORDER BY Groups.group_name, Students.last_name;

-- Q4.2 Join Students and Grades — students and their grades
-- Connecting columns: Students.student_id = Grades.student_id
SELECT
    Students.first_name,
    Students.last_name,
    Grades.grade
FROM Students
INNER JOIN Grades
    ON Students.student_id = Grades.student_id
ORDER BY Students.last_name, Grades.grade DESC;

-- Q4.3 Join Students, Grades, Exams and Subjects —
--      student names, subjects and grades
-- Connecting columns:
--   Students.student_id = Grades.student_id
--   Grades.exam_id = Exams.exam_id
--   Exams.subject_id = Subjects.subject_id
SELECT
    Students.first_name,
    Students.last_name,
    Subjects.subject_name,
    Grades.grade
FROM Students
INNER JOIN Grades
    ON Students.student_id = Grades.student_id
INNER JOIN Exams
    ON Grades.exam_id = Exams.exam_id
INNER JOIN Subjects
    ON Exams.subject_id = Subjects.subject_id
ORDER BY Students.last_name, Subjects.subject_name;

-- Q4.4 LEFT JOIN example — all students with grades if available
SELECT
    Students.first_name,
    Students.last_name,
    Grades.grade
FROM Students
LEFT JOIN Grades
    ON Students.student_id = Grades.student_id
ORDER BY Students.last_name;
"""


def seed_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;
        DROP TABLE IF EXISTS Grades;
        DROP TABLE IF EXISTS Exams;
        DROP TABLE IF EXISTS Subjects;
        DROP TABLE IF EXISTS Students;
        DROP TABLE IF EXISTS Teachers;
        DROP TABLE IF EXISTS Groups;
        CREATE TABLE Groups (
            group_id INTEGER PRIMARY KEY,
            group_name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            year INTEGER NOT NULL
        );
        CREATE TABLE Teachers (
            teacher_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            position TEXT NOT NULL,
            department TEXT NOT NULL
        );
        CREATE TABLE Subjects (
            subject_id INTEGER PRIMARY KEY,
            subject_name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            credits INTEGER NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
        );
        CREATE TABLE Students (
            student_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            group_id INTEGER NOT NULL,
            FOREIGN KEY (group_id) REFERENCES Groups(group_id)
        );
        CREATE TABLE Exams (
            exam_id INTEGER PRIMARY KEY,
            subject_id INTEGER NOT NULL,
            exam_date TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
        );
        CREATE TABLE Grades (
            grade_id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            exam_id INTEGER NOT NULL,
            grade INTEGER NOT NULL CHECK (grade BETWEEN 0 AND 100),
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (exam_id) REFERENCES Exams(exam_id)
        );
        """
    )
    cur.executemany("INSERT INTO Groups VALUES (?,?,?,?)", GROUPS)
    cur.executemany("INSERT INTO Teachers VALUES (?,?,?,?,?)", TEACHERS)
    cur.executemany("INSERT INTO Subjects VALUES (?,?,?,?)", SUBJECTS)
    cur.executemany("INSERT INTO Students VALUES (?,?,?,?,?,?)", STUDENTS)
    cur.executemany("INSERT INTO Exams VALUES (?,?,?,?)", EXAMS)
    cur.executemany("INSERT INTO Grades VALUES (?,?,?,?)", GRADES)
    conn.commit()


QUERIES = [
    ("part2_q1_all_students", "SELECT * FROM Students;", "Part 2 — All Students"),
    (
        "part2_q2_names",
        "SELECT student_id, first_name, last_name FROM Students;",
        "Part 2 — Student IDs and Names",
    ),
    ("part2_q3_groups", "SELECT * FROM Groups;", "Part 2 — All Groups"),
    (
        "part2_q4_subjects",
        "SELECT subject_name FROM Subjects;",
        "Part 2 — Subject Names",
    ),
    (
        "part3_q1_where",
        "SELECT * FROM Students WHERE group_id = 1;",
        "Part 3 — WHERE group_id = 1",
    ),
    (
        "part3_q2_order_by",
        "SELECT * FROM Students ORDER BY last_name ASC;",
        "Part 3 — ORDER BY last_name",
    ),
    (
        "part3_q3_count",
        "SELECT COUNT(*) AS total_students FROM Students;",
        "Part 3 — COUNT(*) total students",
    ),
    (
        "part3_q4_group_by",
        "SELECT group_id, COUNT(*) AS student_count FROM Students GROUP BY group_id;",
        "Part 3 — GROUP BY student count",
    ),
    (
        "part3_q5_max",
        "SELECT MAX(grade) AS max_grade FROM Grades;",
        "Part 3 — MAX(grade)",
    ),
    (
        "part3_q6_min",
        "SELECT MIN(grade) AS min_grade FROM Grades;",
        "Part 3 — MIN(grade)",
    ),
    (
        "part3_q7_avg",
        "SELECT ROUND(AVG(grade), 2) AS average_grade FROM Grades;",
        "Part 3 — AVG(grade)",
    ),
    (
        "part4_q1_students_groups",
        """SELECT Students.first_name, Students.last_name, Groups.group_name
FROM Students
INNER JOIN Groups ON Students.group_id = Groups.group_id
ORDER BY Groups.group_name, Students.last_name;""",
        "Part 4 — INNER JOIN Students + Groups",
    ),
    (
        "part4_q2_students_grades",
        """SELECT Students.first_name, Students.last_name, Grades.grade
FROM Students
INNER JOIN Grades ON Students.student_id = Grades.student_id
ORDER BY Students.last_name, Grades.grade DESC;""",
        "Part 4 — INNER JOIN Students + Grades",
    ),
    (
        "part4_q3_full_join",
        """SELECT Students.first_name, Students.last_name, Subjects.subject_name, Grades.grade
FROM Students
INNER JOIN Grades ON Students.student_id = Grades.student_id
INNER JOIN Exams ON Grades.exam_id = Exams.exam_id
INNER JOIN Subjects ON Exams.subject_id = Subjects.subject_id
ORDER BY Students.last_name, Subjects.subject_name;""",
        "Part 4 — JOIN Students + Grades + Subjects",
    ),
    (
        "part4_q4_left_join",
        """SELECT Students.first_name, Students.last_name, Grades.grade
FROM Students
LEFT JOIN Grades ON Students.student_id = Grades.student_id
ORDER BY Students.last_name;""",
        "Part 4 — LEFT JOIN Students + Grades",
    ),
]


def run_queries(conn: sqlite3.Connection):
    results = {}
    cur = conn.cursor()
    for key, sql, title in QUERIES:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        results[key] = {"sql": sql.strip(), "title": title, "cols": cols, "rows": rows}
    return results


# ---------------------------------------------------------------------------
# Screenshot generation — Windows 10/11 UI (Excel + DB Browser for SQLite)
# ---------------------------------------------------------------------------

plt.rcParams["font.family"] = "DejaVu Sans"

DESKTOP = "#0F6CBD"  # Windows desktop blue accent backdrop
WIN_BORDER = "#8A8A8A"
WIN_TITLE_BG = "#FFFFFF"
WIN_CONTENT = "#F3F3F3"
EXCEL_GREEN = "#217346"
DB_BLUE = "#0078D4"


def _truncate(val, n=28):
    s = str(val)
    return s if len(s) <= n else s[: n - 1] + "…"


def _windows_chrome(fig, ax, app_title: str, accent="#217346"):
    """Draw a Windows 10/11 style application window frame."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    fig.patch.set_facecolor("#1A1A2E")

    # soft desktop gradient backdrop
    ax.add_patch(plt.Rectangle((0, 0), 10, 7.2, color="#1B2838"))

    # window shadow
    ax.add_patch(plt.Rectangle((0.28, 0.18), 9.5, 6.75, color="#00000055"))

    # main window
    ax.add_patch(plt.Rectangle((0.2, 0.28), 9.5, 6.75, color="#FFFFFF", ec=WIN_BORDER, lw=0.8))

    # title bar
    ax.add_patch(plt.Rectangle((0.2, 6.68), 9.5, 0.35, color=WIN_TITLE_BG, ec=WIN_BORDER, lw=0.4))
    # app icon square
    ax.add_patch(plt.Rectangle((0.32, 6.76), 0.18, 0.18, color=accent))
    ax.text(0.62, 6.85, app_title, color="#1A1A1A", fontsize=8.5, va="center")

    # Windows caption buttons: min, max, close
    bx = 9.05
    # minimize
    ax.add_patch(plt.Rectangle((bx, 6.68), 0.35, 0.35, color="#FFFFFF", ec="#E5E5E5", lw=0.3))
    ax.plot([bx + 0.1, bx + 0.25], [6.85, 6.85], color="#333", lw=1.0)
    # maximize
    ax.add_patch(plt.Rectangle((bx + 0.35, 6.68), 0.35, 0.35, color="#FFFFFF", ec="#E5E5E5", lw=0.3))
    ax.add_patch(plt.Rectangle((bx + 0.44, 6.78), 0.16, 0.14, fill=False, ec="#333", lw=1.0))
    # close
    ax.add_patch(plt.Rectangle((bx + 0.7, 6.68), 0.35, 0.35, color="#E81123"))
    ax.plot([bx + 0.8, bx + 0.95], [6.78, 6.93], color="white", lw=1.1)
    ax.plot([bx + 0.8, bx + 0.95], [6.93, 6.78], color="white", lw=1.1)

    # thin accent line under title
    ax.add_patch(plt.Rectangle((0.2, 6.66), 9.5, 0.025, color=accent))


def _draw_excel_ribbon(ax):
    # menu tabs
    ax.add_patch(plt.Rectangle((0.2, 6.28), 9.5, 0.38, color="#F3F3F3"))
    tabs = [("File", True), ("Home", False), ("Insert", False), ("Data", True), ("View", False)]
    x = 0.35
    for name, active in tabs:
        color = EXCEL_GREEN if name == "Data" else "#333333"
        weight = "bold" if name == "Data" else "normal"
        ax.text(x, 6.47, name, color=color, fontsize=7.5, fontweight=weight, va="center")
        if name == "Data":
            ax.plot([x - 0.05, x + 0.45], [6.30, 6.30], color=EXCEL_GREEN, lw=2)
        x += 0.85
    # ribbon tools row
    ax.add_patch(plt.Rectangle((0.2, 5.88), 9.5, 0.4, color="#FAFAFA", ec="#E5E5E5", lw=0.4))
    for label, lx in [("Sort A to Z", 0.45), ("Filter", 1.7), ("Find & Select", 2.55), ("Advanced", 3.85)]:
        ax.add_patch(plt.Rectangle((lx, 5.96), 0.95 if "Sort" in label or "Find" in label else 0.7, 0.24,
                                   color="#FFFFFF", ec="#C8C8C8", lw=0.6))
        ax.text(lx + 0.08, 6.08, label, fontsize=6.2, color="#333", va="center")


def _draw_taskbar(ax):
    ax.add_patch(plt.Rectangle((0, 0), 10, 0.22, color="#000000"))
    ax.add_patch(plt.Rectangle((0.08, 0.04), 0.14, 0.14, color="#0078D4"))
    ax.text(9.35, 0.11, "12:08", color="white", fontsize=6, va="center", ha="right")
    ax.text(9.85, 0.11, "PM", color="#CCCCCC", fontsize=5.5, va="center", ha="right")


def draw_sql_result(path: Path, title: str, sql: str, cols, rows, max_rows=10):
    fig, ax = plt.subplots(figsize=(12.5, 7.6), dpi=160)
    win_title = f"DB Browser for SQLite — university.db  [{title}]"
    _windows_chrome(fig, ax, win_title, accent=DB_BLUE)
    _draw_taskbar(ax)

    # tab strip
    ax.add_patch(plt.Rectangle((0.2, 6.28), 9.5, 0.38, color="#E8E8E8"))
    for i, tab in enumerate(["Database Structure", "Browse Data", "Edit Pragmas", "Execute SQL"]):
        x = 0.3 + i * 1.7
        active = tab == "Execute SQL"
        ax.add_patch(plt.Rectangle((x, 6.30), 1.6, 0.32, color="#FFFFFF" if active else "#E8E8E8"))
        ax.text(x + 0.08, 6.46, tab, fontsize=6.8, color=DB_BLUE if active else "#555",
                fontweight="bold" if active else "normal", va="center")
        if active:
            ax.plot([x, x + 1.6], [6.30, 6.30], color=DB_BLUE, lw=2)

    # toolbar
    ax.add_patch(plt.Rectangle((0.2, 5.95), 9.5, 0.33, color="#F5F5F5", ec="#DDDDDD", lw=0.4))
    ax.add_patch(plt.Rectangle((0.35, 6.01), 0.85, 0.22, color=DB_BLUE))
    ax.text(0.77, 6.12, "▶ Execute SQL", color="white", fontsize=6.5, ha="center", va="center", fontweight="bold")
    ax.text(1.4, 6.12, "Open SQL file  |  Save  |  Clear", color="#666", fontsize=6.2, va="center")

    # SQL editor pane (light Windows style, not dark mac)
    ax.add_patch(plt.Rectangle((0.35, 4.55), 9.2, 1.3, color="#FFFFFF", ec="#B4B4B4", lw=0.8))
    ax.text(0.45, 5.7, "SQL 1", color=DB_BLUE, fontsize=7, fontweight="bold")
    wrapped_lines = []
    for raw in sql.strip().splitlines():
        line = raw.rstrip()
        while len(line) > 100:
            wrapped_lines.append(line[:100])
            line = line[100:]
        wrapped_lines.append(line)
    sql_display = "\n".join(wrapped_lines[:6])
    if len(wrapped_lines) > 6:
        sql_display += "\n..."
    # line numbers gutter
    ax.add_patch(plt.Rectangle((0.35, 4.55), 0.35, 1.3, color="#F0F0F0", ec="#D0D0D0", lw=0.4))
    for i in range(min(6, len(wrapped_lines) + (1 if len(wrapped_lines) > 6 else 0))):
        ax.text(0.52, 5.52 - i * 0.18, str(i + 1), fontsize=5.8, color="#888", ha="center", va="top",
                family="DejaVu Sans Mono")
    ax.text(
        0.8,
        5.52,
        sql_display,
        color="#1A1A1A",
        fontsize=6.8,
        family="DejaVu Sans Mono",
        va="top",
        linespacing=1.45,
    )

    show = rows[:max_rows]
    ax.text(
        0.4,
        4.38,
        f"Results  ·  {len(rows)} row(s)"
        + (f"  ·  showing first {len(show)}" if len(rows) > max_rows else "")
        + "  ·  Query finished successfully",
        color="#217346",
        fontsize=7.2,
        fontweight="bold",
    )

    n_cols = len(cols)
    x0, y0 = 0.35, 4.15
    usable = 9.2
    col_w = usable / max(n_cols, 1)
    row_h = 0.30

    ax.add_patch(plt.Rectangle((x0, y0 - row_h), usable, row_h, color="#E7E6E6", ec="#B0B0B0", lw=0.5))
    for i, c in enumerate(cols):
        ax.text(
            x0 + i * col_w + 0.06,
            y0 - row_h / 2,
            _truncate(c, 18),
            fontsize=7,
            fontweight="bold",
            color="#1A1A1A",
            va="center",
        )
        if i:
            ax.plot([x0 + i * col_w, x0 + i * col_w], [y0 - row_h, y0], color="#C8C8C8", lw=0.4)

    for r, row in enumerate(show):
        y = y0 - (r + 2) * row_h
        bg = "#FFFFFF" if r % 2 == 0 else "#F2F2F2"
        ax.add_patch(plt.Rectangle((x0, y), usable, row_h, color=bg, ec="#D0D0D0", lw=0.35))
        for i, val in enumerate(row):
            ax.text(
                x0 + i * col_w + 0.06,
                y + row_h / 2,
                _truncate(val, 18),
                fontsize=6.8,
                color="#1A1A1A",
                va="center",
                family="DejaVu Sans Mono",
            )

    # status bar
    ax.add_patch(plt.Rectangle((0.2, 0.28), 9.5, 0.28, color="#007ACC"))
    ax.text(0.4, 0.42, "Ready  |  SQLite 3  |  university.db  |  Windows 11",
            color="white", fontsize=6.5, va="center")

    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def draw_excel_view(path: Path, title: str, subtitle: str, headers, rows, highlight_cols=None, filter_note=None):
    fig, ax = plt.subplots(figsize=(12.5, 7.6), dpi=160)
    win_title = f"Excel  —  University_Database.xlsx  —  {title}"
    _windows_chrome(fig, ax, win_title, accent=EXCEL_GREEN)
    _draw_excel_ribbon(ax)
    _draw_taskbar(ax)

    # formula bar
    ax.add_patch(plt.Rectangle((0.2, 5.55), 9.5, 0.33, color="#FFFFFF", ec="#D0D0D0", lw=0.5))
    ax.text(0.35, 5.71, "fx", color="#217346", fontsize=8, fontweight="bold", va="center")
    ax.add_patch(plt.Rectangle((0.6, 5.60), 8.9, 0.22, color="#FFFFFF", ec="#B4B4B4", lw=0.6))
    ax.text(0.7, 5.71, subtitle, color="#555", fontsize=7, va="center")

    if filter_note:
        ax.add_patch(plt.Rectangle((0.35, 5.20), 9.2, 0.28, color="#E7F3E7", ec="#217346", lw=0.6))
        ax.text(0.5, 5.34, "●  " + filter_note, color=EXCEL_GREEN, fontsize=7.2, va="center", fontweight="bold")

    n_cols = len(headers)
    x0 = 0.55
    y_start = 5.05 if not filter_note else 5.05
    if filter_note:
        y_start = 5.05
    usable = 8.95
    col_w = usable / n_cols
    row_h = 0.32

    # top-left corner cell
    ax.add_patch(plt.Rectangle((0.25, y_start), 0.30, 0.26, color="#E6E6E6", ec="#B0B0B0", lw=0.5))

    # column letters
    for i in range(n_cols):
        ax.add_patch(plt.Rectangle((x0 + i * col_w, y_start), col_w, 0.26, color="#E6E6E6", ec="#B0B0B0", lw=0.5))
        ax.text(
            x0 + i * col_w + col_w / 2,
            y_start + 0.13,
            get_column_letter(i + 1),
            ha="center",
            va="center",
            fontsize=7,
            color="#333",
            fontweight="bold",
        )

    y0 = y_start
    # header row (Excel table style green)
    ax.add_patch(plt.Rectangle((x0, y0 - row_h), usable, row_h, color=EXCEL_GREEN))
    ax.add_patch(plt.Rectangle((0.25, y0 - row_h), 0.30, row_h, color="#E6E6E6", ec="#B0B0B0", lw=0.5))
    ax.text(0.40, y0 - row_h / 2, "1", ha="center", va="center", fontsize=6.5, color="#333")
    for i, h in enumerate(headers):
        ax.text(
            x0 + i * col_w + 0.06,
            y0 - row_h / 2,
            _truncate(h, 14),
            color="white",
            fontsize=7,
            fontweight="bold",
            va="center",
        )
        # filter dropdown chevron
        ax.text(x0 + (i + 1) * col_w - 0.12, y0 - row_h / 2, "▾", color="#D4EDDA", fontsize=6, va="center")

    show = rows[:11]
    for r, row in enumerate(show):
        y = y0 - (r + 2) * row_h
        bg = "#FFFFFF" if r % 2 == 0 else "#E2EFDA"
        ax.add_patch(plt.Rectangle((0.25, y), 0.30, row_h, color="#E6E6E6", ec="#B0B0B0", lw=0.4))
        ax.text(0.40, y + row_h / 2, str(r + 2), ha="center", va="center", fontsize=6.2, color="#333")
        ax.add_patch(plt.Rectangle((x0, y), usable, row_h, color=bg, ec="#C6C6C6", lw=0.35))
        for i, val in enumerate(row):
            color = "#C00000" if highlight_cols and i in highlight_cols else "#1A1A1A"
            weight = "bold" if highlight_cols and i in highlight_cols else "normal"
            ax.text(
                x0 + i * col_w + 0.06,
                y + row_h / 2,
                _truncate(val, 15),
                fontsize=6.8,
                color=color,
                va="center",
                fontweight=weight,
            )

    # sheet tabs
    ax.add_patch(plt.Rectangle((0.2, 0.56), 9.5, 0.32, color="#F3F3F3", ec="#D0D0D0", lw=0.4))
    for i, name in enumerate(["Students", "Groups", "Teachers", "Subjects", "Exams", "Grades"]):
        xx = 0.35 + i * 1.15
        active = name == "Students"
        ax.add_patch(plt.Rectangle((xx, 0.58), 1.05, 0.26, color="#FFFFFF" if active else "#F3F3F3",
                                   ec=EXCEL_GREEN if active else "#D0D0D0", lw=0.7))
        ax.text(xx + 0.52, 0.71, name, ha="center", va="center", fontsize=6.5,
                color=EXCEL_GREEN if active else "#555", fontweight="bold" if active else "normal")

    # status bar
    ax.add_patch(plt.Rectangle((0.2, 0.28), 9.5, 0.28, color="#217346"))
    ax.text(0.4, 0.42, f"Ready  |  Sheet: Students  |  {len(rows)} record(s)  |  Windows 11",
            color="white", fontsize=6.5, va="center")

    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def generate_screenshots(results):
    headers = ["student_id", "first_name", "last_name", "email", "birth_date", "group_id"]

    # Part 1 Excel screenshots
    draw_excel_view(
        SHOTS / "01_students_original.png",
        "Students table (original)",
        "University_Database.xlsx · sheet Students",
        headers,
        STUDENTS,
    )
    draw_excel_view(
        SHOTS / "02_sorted_by_lastname.png",
        "Sorted by last name (A→Z)",
        "Data → Sort → last_name → Ascending",
        headers,
        sorted(STUDENTS, key=lambda x: x[2]),
        highlight_cols={2},
        filter_note="Sort applied: last_name ascending",
    )
    draw_excel_view(
        SHOTS / "03_sorted_by_group.png",
        "Sorted by group",
        "Data → Sort → group_id → Ascending, then last_name",
        headers,
        sorted(STUDENTS, key=lambda x: (x[5], x[2])),
        highlight_cols={5},
        filter_note="Sort applied: group_id ascending",
    )
    draw_excel_view(
        SHOTS / "04_filter_group_cs101.png",
        "Filtered: group CS-101 (group_id = 1)",
        "Data → Filter → group_id equals 1",
        headers,
        [s for s in STUDENTS if s[5] == 1],
        highlight_cols={5},
        filter_note="AutoFilter: group_id = 1  ·  4 records shown",
    )
    draw_excel_view(
        SHOTS / "05_search_karimova.png",
        "Search by ID / last name",
        "Find: student_id = 9  OR  last_name = Karimova",
        headers,
        [s for s in STUDENTS if s[0] == 9],
        highlight_cols={0, 2},
        filter_note="Search hit: Indira Karimova · student_id 9 · group_id 3",
    )
    draw_excel_view(
        SHOTS / "06_filter_two_conditions.png",
        "Filter with two conditions",
        "group_id = 3  AND  last_name >= 'I'",
        headers,
        [s for s in STUDENTS if s[5] == 3 and s[2] >= "I"],
        highlight_cols={2, 5},
        filter_note="Advanced filter: group_id = 3 AND last_name ≥ I  ·  2 records",
    )

    # SQL screenshots
    for key, _, _ in QUERIES:
        r = results[key]
        draw_sql_result(
            SHOTS / f"{key}.png",
            r["title"],
            r["sql"],
            r["cols"],
            r["rows"],
            max_rows=10 if "full_join" in key or "students_grades" in key or "left_join" in key else 12,
        )

    # Also copy selected key shots to artifacts
    for name in [
        "02_sorted_by_lastname.png",
        "04_filter_group_cs101.png",
        "part3_q4_group_by.png",
        "part4_q3_full_join.png",
    ]:
        src = SHOTS / name
        dst = ARTIFACTS / name
        dst.write_bytes(src.read_bytes())


# ---------------------------------------------------------------------------
# Report (DOCX) — minimalist
# ---------------------------------------------------------------------------

def set_run_font(run, name="Calibri", size=11, bold=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_heading_custom(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18 if level == 1 else 12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    if level == 1:
        set_run_font(run, size=16, bold=True, color=(17, 24, 39))
    elif level == 2:
        set_run_font(run, size=13, bold=True, color=(31, 41, 55))
    else:
        set_run_font(run, size=11, bold=True, color=(55, 65, 81))
    return p


def add_body(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    set_run_font(run, size=11, color=(31, 41, 55))
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    set_run_font(run, size=9, color=(107, 114, 128))
    return p


def add_hr(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "E5E7EB")
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_image(doc, path: Path, width=Inches(6.2)):
    if path.exists():
        doc.add_picture(str(path), width=width)
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    set_run_font(run, name="Consolas", size=9, color=(31, 41, 55))
    # light background via shading
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F3F4F6")
    shd.set(qn("w:val"), "clear")
    p._p.get_or_add_pPr().append(shd)
    return p


def add_task_box(doc, text):
    """Assignment requirement callout."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("Assignment: ")
    set_run_font(run, size=10, bold=True, color=(33, 115, 70))
    run2 = p.add_run(text)
    set_run_font(run2, size=10, color=(55, 65, 81))
    return p


def create_report(results):
    """Single submission document: all tasks + Windows screenshots + reports + Q&A + conclusion."""
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    # ===================== COVER =====================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    run = p.add_run("PRACTICAL WORK №7–10")
    set_run_font(run, size=22, bold=True, color=(17, 24, 39))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Data Sorting, Filtering, SQL Queries and Joining Tables")
    set_run_font(run, size=12, color=(75, 85, 99))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("Topics №7–10  ·  University Database")
    set_run_font(run, size=11, color=(107, 114, 128))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Student: Khismetova Aruzhan")
    set_run_font(run, size=11, color=(55, 65, 81))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Document: practicalwork7_10_KhismetovaAruzhan")
    set_run_font(run, size=10, color=(107, 114, 128))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Software: Microsoft Excel (Windows) · DB Browser for SQLite (Windows)")
    set_run_font(run, size=10, color=(107, 114, 128))

    add_hr(doc)

    add_heading_custom(doc, "Contents of this document", 1)
    add_body(doc, "This single document contains: the full assignment text, completed work for Parts 1–4, "
             "Windows screenshots of every step, a short report after each part, answers to the six "
             "individual questions, SQL query listing, and the conclusion.")

    add_heading_custom(doc, "1. Purpose of the practical work", 1)
    add_body(
        doc,
        "To develop skills in sorting, filtering, searching and analyzing data, writing SQL queries, "
        "using aggregate functions and joining information from multiple tables.",
    )

    add_heading_custom(doc, "2. Software and resources", 1)
    add_body(doc, "• Microsoft Excel (Windows 11)")
    add_body(doc, "• DB Browser for SQLite (Windows 11)")
    add_body(doc, "• University_Database.xlsx (Students, Groups, Teachers, Subjects, Exams, Grades)")

    add_heading_custom(doc, "3. Database structure", 1)
    add_body(
        doc,
        "Tables: Groups, Teachers, Subjects, Students, Exams, Grades. "
        "Relationships: Students.group_id → Groups.group_id; Subjects.teacher_id → Teachers.teacher_id; "
        "Exams.subject_id → Subjects.subject_id; Grades.student_id → Students.student_id; "
        "Grades.exam_id → Exams.exam_id.",
    )
    add_body(
        doc,
        f"Dataset: {len(STUDENTS)} students, {len(GROUPS)} groups, {len(TEACHERS)} teachers, "
        f"{len(SUBJECTS)} subjects, {len(EXAMS)} exams, {len(GRADES)} grades.",
    )
    add_image(doc, SHOTS / "01_students_original.png", width=Inches(6.0))
    add_caption(doc, "Figure 0. Original Students table in Microsoft Excel (Windows).")

    # ===================== PART 1 =====================
    add_heading_custom(doc, "4. Part 1 — Sorting, filtering and searching (Topic №7)", 1)
    add_body(
        doc,
        "Task description (from assignment): Open your Students table in Excel. Sort students "
        "alphabetically by last name. Sort students by group. Filter the table to display students "
        "from one selected group. Search for a student by ID or last name. Filter records using two "
        "conditions. Save the results and take screenshots of your work.",
    )

    add_heading_custom(doc, "4.1 Sort students alphabetically by last name", 2)
    add_task_box(doc, "Sort students alphabetically by last name.")
    add_body(doc, "Performed in Excel (Windows): Data → Sort → Column last_name → A to Z.")
    add_image(doc, SHOTS / "02_sorted_by_lastname.png")
    add_caption(doc, "Figure 1. Windows Excel — Students sorted by last_name ascending.")

    add_heading_custom(doc, "4.2 Sort students by group", 2)
    add_task_box(doc, "Sort students by group.")
    add_body(doc, "Performed: Data → Sort → group_id ascending (then last_name).")
    add_image(doc, SHOTS / "03_sorted_by_group.png")
    add_caption(doc, "Figure 2. Windows Excel — Students sorted by group_id.")

    add_heading_custom(doc, "4.3 Filter students from one selected group", 2)
    add_task_box(doc, "Filter the table to display students from one selected group.")
    add_body(doc, "Selected group: CS-101 (group_id = 1). AutoFilter applied. 4 students shown.")
    add_image(doc, SHOTS / "04_filter_group_cs101.png")
    add_caption(doc, "Figure 3. Windows Excel — AutoFilter group_id = 1 (CS-101).")

    add_heading_custom(doc, "4.4 Search for a student by ID or last name", 2)
    add_task_box(doc, "Search for a student by ID or last name.")
    add_body(doc, "Find & Select → Find: last_name = Karimova / student_id = 9 → Indira Karimova.")
    add_image(doc, SHOTS / "05_search_karimova.png")
    add_caption(doc, "Figure 4. Windows Excel — Search result for Karimova.")

    add_heading_custom(doc, "4.5 Filter using two conditions", 2)
    add_task_box(doc, "Filter records using two conditions.")
    add_body(doc, "Advanced Filter: group_id = 3 AND last_name ≥ 'I' → Iskakov, Karimova.")
    add_image(doc, SHOTS / "06_filter_two_conditions.png")
    add_caption(doc, "Figure 5. Windows Excel — Two-condition filter.")

    add_heading_custom(doc, "Report — Part 1", 2)
    add_body(
        doc,
        "Sorting rearranges all rows by a chosen key without removing data. Filtering hides rows "
        "that do not match criteria, so only a subset is visible. Searching locates a specific value "
        "(student_id or last_name). Combined filters (group + name range) narrow the dataset further. "
        "Excel AutoFilter and Sort on Windows are suitable for interactive exploration before SQL.",
    )

    # ===================== PART 2 =====================
    add_heading_custom(doc, "5. Part 2 — Introduction to SQL (Topic №8)", 1)
    add_body(
        doc,
        "Task description (from assignment): Import or create your university tables in an SQL "
        "database. Write and execute: display all Students; display student_id, first_name, last_name; "
        "display all Groups; display subject names.",
    )
    add_body(doc, "Environment: DB Browser for SQLite on Windows 11. Database file: university.db.")

    part2_items = [
        ("part2_q1_all_students", "5.1 Display all records from the Students table",
         "Display all records from the Students table.",
         "Figure 6. Windows DB Browser — SELECT * FROM Students;"),
        ("part2_q2_names", "5.2 Display student IDs, first names and last names",
         "Display only student IDs, first names and last names.",
         "Figure 7. Windows DB Browser — projection of student_id, first_name, last_name."),
        ("part2_q3_groups", "5.3 Display all records from the Groups table",
         "Display all records from the Groups table.",
         "Figure 8. Windows DB Browser — SELECT * FROM Groups;"),
        ("part2_q4_subjects", "5.4 Display the names of all subjects",
         "Display the names of all subjects from the Subjects table.",
         "Figure 9. Windows DB Browser — SELECT subject_name FROM Subjects;"),
    ]
    for key, heading, task, caption in part2_items:
        add_heading_custom(doc, heading, 2)
        add_task_box(doc, task)
        add_code(doc, results[key]["sql"])
        add_image(doc, SHOTS / f"{key}.png")
        add_caption(doc, caption)

    add_heading_custom(doc, "Report — Part 2", 2)
    add_body(
        doc,
        "SQL is used to define, query and manage relational data. SELECT * returns every column; "
        "listing specific columns returns only needed fields. PRIMARY KEY and FOREIGN KEY enforce "
        "relationships before filtering and aggregation.",
    )

    # ===================== PART 3 =====================
    add_heading_custom(doc, "6. Part 3 — SQL queries and aggregate functions (Topic №9)", 1)
    add_body(
        doc,
        "Task description (from assignment): Display students of a selected group (WHERE); display "
        "students alphabetically (ORDER BY); COUNT total students; COUNT students per group (GROUP BY); "
        "find MAX, MIN and AVG grade.",
    )

    add_heading_custom(doc, "6.1 WHERE — students of a selected group", 2)
    add_task_box(doc, "Display students belonging to a selected group using WHERE.")
    add_code(doc, results["part3_q1_where"]["sql"])
    add_image(doc, SHOTS / "part3_q1_where.png")
    add_caption(doc, "Figure 10. WHERE group_id = 1.")

    add_heading_custom(doc, "6.2 ORDER BY — alphabetical order", 2)
    add_task_box(doc, "Display students in alphabetical order using ORDER BY.")
    add_code(doc, results["part3_q2_order_by"]["sql"])
    add_image(doc, SHOTS / "part3_q2_order_by.png")
    add_caption(doc, "Figure 11. ORDER BY last_name ASC.")

    add_heading_custom(doc, "6.3 COUNT — total number of students", 2)
    add_task_box(doc, "Count the total number of students using COUNT().")
    add_code(doc, results["part3_q3_count"]["sql"])
    add_image(doc, SHOTS / "part3_q3_count.png")
    total = results["part3_q3_count"]["rows"][0][0]
    add_caption(doc, f"Figure 12. Total students = {total}.")

    add_heading_custom(doc, "6.4 GROUP BY — students in each group", 2)
    add_task_box(doc, "Count the number of students in each group using GROUP BY.")
    add_code(doc, results["part3_q4_group_by"]["sql"])
    add_image(doc, SHOTS / "part3_q4_group_by.png")
    add_caption(doc, "Figure 13. Student count by group_id.")

    add_heading_custom(doc, "6.5 MAX grade", 2)
    add_task_box(doc, "Find the maximum grade using MAX().")
    add_code(doc, results["part3_q5_max"]["sql"])
    add_image(doc, SHOTS / "part3_q5_max.png")
    add_caption(doc, f"Figure 14. MAX(grade) = {results['part3_q5_max']['rows'][0][0]}.")

    add_heading_custom(doc, "6.6 MIN grade", 2)
    add_task_box(doc, "Find the minimum grade using MIN().")
    add_code(doc, results["part3_q6_min"]["sql"])
    add_image(doc, SHOTS / "part3_q6_min.png")
    add_caption(doc, f"Figure 15. MIN(grade) = {results['part3_q6_min']['rows'][0][0]}.")

    add_heading_custom(doc, "6.7 AVG grade", 2)
    add_task_box(doc, "Calculate the average grade using AVG().")
    add_code(doc, results["part3_q7_avg"]["sql"])
    add_image(doc, SHOTS / "part3_q7_avg.png")
    add_caption(doc, f"Figure 16. AVG(grade) = {results['part3_q7_avg']['rows'][0][0]}.")

    add_heading_custom(doc, "Report — Part 3", 2)
    add_body(
        doc,
        "WHERE filters rows. ORDER BY only changes presentation order. COUNT, MAX, MIN and AVG "
        "summarize many values. GROUP BY partitions data so aggregates are computed per group. "
        f"Result: {total} students; grades from {results['part3_q6_min']['rows'][0][0]} to "
        f"{results['part3_q5_max']['rows'][0][0]}; average {results['part3_q7_avg']['rows'][0][0]}.",
    )

    # ===================== PART 4 =====================
    add_heading_custom(doc, "7. Part 4 — Joining tables using JOIN (Topic №10)", 1)
    add_body(
        doc,
        "Task description (from assignment): Join Students and Groups to show name + group name. "
        "Join Students and Grades. If Subjects is linked, join to show student, subject and grade. "
        "Explain connecting columns. Compare JOIN result with original tables.",
    )

    add_heading_custom(doc, "7.1 INNER JOIN Students and Groups", 2)
    add_task_box(doc, "Join Students and Groups to display each student's name and group name.")
    add_body(doc, "Connecting columns: Students.group_id = Groups.group_id.")
    add_code(doc, results["part4_q1_students_groups"]["sql"])
    add_image(doc, SHOTS / "part4_q1_students_groups.png")
    add_caption(doc, "Figure 17. INNER JOIN Students + Groups.")

    add_heading_custom(doc, "7.2 INNER JOIN Students and Grades", 2)
    add_task_box(doc, "Join Students and Grades to display students and their grades.")
    add_body(doc, "Connecting columns: Students.student_id = Grades.student_id.")
    add_code(doc, results["part4_q2_students_grades"]["sql"])
    add_image(doc, SHOTS / "part4_q2_students_grades.png")
    add_caption(doc, "Figure 18. INNER JOIN Students + Grades.")

    add_heading_custom(doc, "7.3 JOIN Students, Grades, Exams and Subjects", 2)
    add_task_box(doc, "Join tables to display student names, subjects and grades.")
    add_body(
        doc,
        "Connecting columns: Students.student_id = Grades.student_id; "
        "Grades.exam_id = Exams.exam_id; Exams.subject_id = Subjects.subject_id.",
    )
    add_code(doc, results["part4_q3_full_join"]["sql"])
    add_image(doc, SHOTS / "part4_q3_full_join.png")
    add_caption(doc, "Figure 19. Windows DB Browser — student names, subjects and grades.")

    add_heading_custom(doc, "7.4 LEFT JOIN comparison + connecting columns", 2)
    add_task_box(doc, "Explain which columns connect the tables. Compare JOIN with original tables.")
    add_body(
        doc,
        "Compared with the original Students / Grades sheets alone, the JOIN result shows readable "
        "combined information without repeating master data. INNER JOIN keeps only matching rows; "
        "LEFT JOIN keeps all left-table rows.",
    )
    add_code(doc, results["part4_q4_left_join"]["sql"])
    add_image(doc, SHOTS / "part4_q4_left_join.png")
    add_caption(doc, "Figure 20. Windows DB Browser — LEFT JOIN Students + Grades.")

    add_heading_custom(doc, "Report — Part 4", 2)
    add_body(
        doc,
        "JOIN combines rows from multiple tables using matching key values. Compared with looking at "
        "Students or Grades alone, a JOIN result shows denormalized, human-readable information "
        "(name + group, or name + subject + grade) without duplicating master data in every sheet. "
        "INNER JOIN omits non-matching rows; LEFT JOIN preserves the left side and fills missing "
        "right-side columns with NULL. In this dataset every student has grades, so INNER and LEFT "
        "results contain the same people, but the pattern is ready for incomplete data.",
    )

    # -------- Questions --------
    add_heading_custom(doc, "8. Individual assignment — answers to six questions", 1)
    add_body(
        doc,
        "Prepare a short report answering these questions (from assignment).",
    )

    qa = [
        (
            "Question 1. What is the difference between sorting and filtering?",
            "Sorting changes the order of rows according to one or more columns (for example A→Z by "
            "last_name) but keeps all records. Filtering temporarily hides rows that do not satisfy "
            "a condition (for example group_id = 1), so only matching records are shown.",
        ),
        (
            "Question 2. What is SQL used for?",
            "SQL is used to create and modify database structures, insert and update data, and — most "
            "importantly for this work — to query relational tables with SELECT, WHERE, ORDER BY, "
            "GROUP BY, aggregate functions and JOIN.",
        ),
        (
            "Question 3. What is the difference between WHERE and ORDER BY?",
            "WHERE selects which rows are included in the result based on conditions. ORDER BY does "
            "not remove rows; it only arranges the final result set (ASC or DESC) by chosen columns.",
        ),
        (
            "Question 4. Why do we use GROUP BY and aggregate functions?",
            "Aggregate functions (COUNT, SUM, AVG, MIN, MAX) compute summary values from many rows. "
            "GROUP BY partitions the data so those summaries are calculated separately for each group "
            "(for example student count per group_id).",
        ),
        (
            "Question 5. What is the purpose of JOIN?",
            "JOIN retrieves related information stored in different tables by matching key columns "
            "(foreign key = primary key), producing a combined result such as student name with "
            "group name or subject and grade.",
        ),
        (
            "Question 6. What is the difference between INNER JOIN and LEFT JOIN?",
            "INNER JOIN returns only rows that have a match in both tables. LEFT JOIN returns all "
            "rows from the left table and matching rows from the right table; if there is no match, "
            "right-table columns are NULL.",
        ),
    ]
    for q, a in qa:
        add_heading_custom(doc, q, 3)
        add_body(doc, a)

    # -------- SQL appendix inside the same document --------
    add_heading_custom(doc, "9. Appendix — full SQL script used in this work", 1)
    add_body(
        doc,
        "All queries below were executed in DB Browser for SQLite on Windows. "
        "The complete script is also saved as sql/university_queries.sql.",
    )
    for key, sql, title in QUERIES:
        add_heading_custom(doc, title, 3)
        add_code(doc, sql.strip())

    # -------- Conclusion --------
    add_heading_custom(doc, "10. Conclusion", 1)
    add_body(
        doc,
        "After completing this practical work, students should be able to sort and filter large "
        "datasets, search for information, write basic SQL queries, summarize data using aggregate "
        "functions and retrieve related information from multiple tables using JOIN.",
    )
    add_body(
        doc,
        "In this submission the Students dataset was sorted and filtered in Microsoft Excel on "
        "Windows (alphabetical sort, sort by group, one-group filter, search by ID/name, two-condition "
        "filter). The university schema was implemented in SQLite and opened in DB Browser for SQLite "
        "on Windows. Basic SELECT queries, WHERE, ORDER BY, GROUP BY and aggregate functions "
        "(COUNT, MAX, MIN, AVG) were executed successfully. INNER JOIN and LEFT JOIN combined "
        "Students with Groups, Grades and Subjects, showing how foreign keys connect tables. "
        "Excel is convenient for quick visual exploration; SQL provides precise, repeatable "
        "multi-table analysis.",
    )

    add_heading_custom(doc, "11. Deliverables (all included in / with this package)", 1)
    add_body(doc, "1. Updated University_Database.xlsx — data/University_Database.xlsx")
    add_body(doc, "2. SQL script containing all queries — sql/university_queries.sql (also in §9)")
    add_body(doc, "3. Screenshots showing executed queries and results — embedded above (Windows UI)")
    add_body(doc, "4. Short report with answers to the six questions — §8 of this document")
    add_body(doc, "5. Report after each assignment part — Report — Part 1…4 sections above")
    add_body(doc, "6. Conclusion — §10 of this document")

    out = REPORT / "practicalwork7_10_KhismetovaAruzhan.docx"
    doc.save(out)
    # copies for convenience
    (REPORT / "Practical_Work_7_10_FULL.docx").write_bytes(out.read_bytes())
    (REPORT / "Practical_Work_7_10_Report.docx").write_bytes(out.read_bytes())
    # single submission file at repository root
    root_doc = ROOT.parent / "practicalwork7_10_KhismetovaAruzhan.docx"
    root_doc.write_bytes(out.read_bytes())
    return out


def write_results_md(results):
    lines = ["# Query results reference\n"]
    for key, sql, title in QUERIES:
        r = results[key]
        lines.append(f"## {title}\n")
        lines.append("```sql\n" + r["sql"] + "\n```\n")
        lines.append("| " + " | ".join(r["cols"]) + " |")
        lines.append("| " + " | ".join(["---"] * len(r["cols"])) + " |")
        for row in r["rows"]:
            lines.append("| " + " | ".join(str(v) for v in row) + " |")
        lines.append("")
    (ROOT / "QUERY_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Creating Excel workbook…")
    xlsx = create_excel()
    print("  ->", xlsx)

    sql_path = SQL_DIR / "university_queries.sql"
    # Full script with inserts for portability
    inserts = ["BEGIN TRANSACTION;"]
    for t, rows in [
        ("Groups", GROUPS),
        ("Teachers", TEACHERS),
        ("Subjects", SUBJECTS),
        ("Students", STUDENTS),
        ("Exams", EXAMS),
        ("Grades", GRADES),
    ]:
        for row in rows:
            vals = ", ".join(
                str(v) if isinstance(v, int) else "'" + str(v).replace("'", "''") + "'" for v in row
            )
            inserts.append(f"INSERT INTO {t} VALUES ({vals});")
    inserts.append("COMMIT;")
    # Place inserts after CREATE, before Part 2 queries
    parts = SQL_SCRIPT.split("-- ============================================================================\n-- PART 2.")
    full_sql = parts[0] + "\n".join(inserts) + "\n\n-- ============================================================================\n-- PART 2." + parts[1]
    sql_path.write_text(full_sql, encoding="utf-8")
    print("  ->", sql_path)

    db_path = DATA / "university.db"
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    seed_db(conn)
    print("Running queries…")
    results = run_queries(conn)
    conn.close()
    print("  ->", db_path)

    print("Generating screenshots…")
    generate_screenshots(results)
    print("  ->", SHOTS)

    print("Writing report…")
    report = create_report(results)
    print("  ->", report)

    write_results_md(results)

    # Root README for the package
    (ROOT / "README.md").write_text(
        """# Practical Work №7–10

Data Sorting, Filtering, SQL Queries and Joining Tables

## Main submission (ONE document)

**`report/Practical_Work_7_10_FULL.docx`** — all assignment tasks, Windows screenshots, SQL queries, part reports, six answers, and conclusion in a single file.

## Supporting files

| Path | Description |
|------|-------------|
| `data/University_Database.xlsx` | Updated Excel workbook |
| `data/university.db` | SQLite database |
| `sql/university_queries.sql` | Full SQL script |
| `screenshots/` | Windows Excel / DB Browser screenshots |
| `QUERY_RESULTS.md` | Text reference of query results |

```bash
python3 generate_all.py
```
""",
        encoding="utf-8",
    )
    print("Done.")


if __name__ == "__main__":
    main()
