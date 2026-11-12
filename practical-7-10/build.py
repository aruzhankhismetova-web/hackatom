#!/usr/bin/env python3
"""Build the Practical Work 7–10 workbook, database, SQL script and report.

Edit adjust_here.py, then run:

    python3 build.py
"""

from __future__ import annotations

import sqlite3
import sys
from collections import Counter
from datetime import date, datetime, time
from html import escape
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import adjust_here as cfg  # noqa: E402

OUT_SQL = ROOT / "sql" / "practical_work_7_10.sql"
OUT_RESULTS = ROOT / "sql" / "query_results.txt"
OUT_DB = ROOT / "db" / "university.sqlite"
OUT_XLSX = ROOT / "University_Database.xlsx"
OUT_SHOTS = ROOT / "screenshots"
OUT_DOCX = ROOT / "report" / "Practical_Work_7-10.docx"
OUT_HTML = ROOT / "report" / "Practical_Work_7-10.html"
OUT_PDF = ROOT / "report" / "Practical_Work_7-10.pdf"

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
FONT = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Regular.ttf"), 15)
FONT_BOLD = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 15)
FONT_TITLE = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 20)
FONT_SMALL = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Regular.ttf"), 13)
FONT_ITALIC = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Italic.ttf"), 15)
FONT_MONO = ImageFont.truetype(str(FONT_DIR / "LiberationMono-Regular.ttf"), 14)

NAVY = "1F4E79"
NAVY_RGB = (31, 78, 121)
GOLD = "FFF2CC"
PALE = "F3F7FB"
GREEN = "E2EFDA"
ORANGE = "FCE4D6"
TEAL = "DDEBF7"
RED = "C00000"

THIN = Border(
    left=Side(style="thin", color="BFBFBF"),
    right=Side(style="thin", color="BFBFBF"),
    top=Side(style="thin", color="BFBFBF"),
    bottom=Side(style="thin", color="BFBFBF"),
)
HEADER_FILL = PatternFill("solid", fgColor=NAVY)
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name="Calibri", bold=True, color=NAVY, size=16)
NOTE_FONT = Font(name="Calibri", italic=True, color="595959", size=11)
LABEL_FONT = Font(name="Calibri", bold=True, size=12, color=NAVY)
BODY_FONT = Font(name="Calibri", size=11)
YELLOW = PatternFill("solid", fgColor=GOLD)
ALT = PatternFill("solid", fgColor=PALE)
WRAP = Alignment(wrap_text=True, vertical="center")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=True)


def fail(message):
    raise SystemExit(message)


def sql_literal(value):
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, int):
        return str(value)
    fail(f"Cannot put {value!r} into SQL")


def validate_settings():
    if cfg.FILTER_GENDER not in ("F", "M"):
        fail("FILTER_GENDER must be F or M.")
    for name in (
        "SELECTED_GROUP_ID",
        "SEARCH_STUDENT_ID",
        "FILTER_MAX_GROUP_ID",
        "GRADE_BELOW",
        "SELECTED_COURSE_ID",
        "SELECTED_TEACHER_ID",
        "SELECTED_SCHEDULE_ID",
        "SELECTED_DEPARTMENT_ID",
    ):
        if not isinstance(getattr(cfg, name), int):
            fail(f"{name} must be a whole number.")
    if not str(cfg.SEARCH_LAST_NAME).strip():
        fail("SEARCH_LAST_NAME cannot be empty.")
    if cfg.FREE_DAY not in cfg.WEEKDAYS and cfg.FREE_DAY not in (
        "Saturday",
        "Sunday",
    ):
        fail("FREE_DAY must be a weekday name, for example Monday.")
    for label, value in (("FREE_START", cfg.FREE_START), ("FREE_END", cfg.FREE_END)):
        try:
            datetime.strptime(value, "%H:%M:%S")
        except ValueError:
            fail(f"{label} must look like 08:00:00.")
    if cfg.FREE_END <= cfg.FREE_START:
        fail("FREE_END must be later than FREE_START.")
    if not str(cfg.STUDENT_NAME).strip():
        fail("STUDENT_NAME cannot be empty.")


def schema_sql():
    return """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Grades;
DROP TABLE IF EXISTS Schedule;
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Teachers;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Groups;
DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS Classrooms;
DROP TABLE IF EXISTS settings;

-- Groups must be created before Students and Schedule.
CREATE TABLE Groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL CHECK (length(trim(group_name)) > 0),
    year_of_study INTEGER NOT NULL CHECK (year_of_study > 0),
    specialty TEXT NOT NULL CHECK (length(trim(specialty)) > 0)
);

CREATE TABLE Departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL CHECK (length(trim(department_name)) > 0),
    building TEXT NOT NULL CHECK (length(trim(building)) > 0)
);

CREATE TABLE Classrooms (
    classroom_id INTEGER PRIMARY KEY,
    room_number TEXT NOT NULL CHECK (length(trim(room_number)) > 0),
    building TEXT NOT NULL CHECK (length(trim(building)) > 0),
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE Teachers (
    teacher_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0),
    last_name TEXT NOT NULL CHECK (length(trim(last_name)) > 0),
    academic_degree TEXT NOT NULL CHECK (length(trim(academic_degree)) > 0),
    phone TEXT NOT NULL CHECK (length(trim(phone)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0),
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Departments (department_id)
);

-- Courses is the subject table for this database.
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL CHECK (length(trim(course_name)) > 0),
    credits INTEGER NOT NULL CHECK (credits > 0),
    semester INTEGER NOT NULL CHECK (semester > 0),
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Departments (department_id)
);

CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY,
    last_name TEXT NOT NULL CHECK (length(trim(last_name)) > 0),
    first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0),
    birth_date TEXT NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('F', 'M')),
    phone TEXT NOT NULL CHECK (length(trim(phone)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0),
    group_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES Groups (group_id)
);

-- A birth date cannot be in the future.
-- SQLite rejects date('now') inside CHECK, so the rule is a trigger.
CREATE TRIGGER students_birth_date_insert
BEFORE INSERT ON Students
FOR EACH ROW
WHEN NEW.birth_date > date('now')
BEGIN
    SELECT RAISE(ABORT, 'birth date cannot be in the future');
END;

CREATE TABLE Schedule (
    schedule_id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    classroom_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL CHECK (
        day_of_week IN (
            'Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday'
        )
    ),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL CHECK (end_time > start_time),
    FOREIGN KEY (course_id) REFERENCES Courses (course_id),
    FOREIGN KEY (teacher_id) REFERENCES Teachers (teacher_id),
    FOREIGN KEY (group_id) REFERENCES Groups (group_id),
    FOREIGN KEY (classroom_id) REFERENCES Classrooms (classroom_id)
);

CREATE TABLE Grades (
    grade_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade_value INTEGER NOT NULL CHECK (grade_value BETWEEN 0 AND 100),
    grade_date TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students (student_id),
    FOREIGN KEY (course_id) REFERENCES Courses (course_id),
    -- A student cannot have two grades for the same course on the same date.
    UNIQUE (student_id, course_id, grade_date)
);

-- One row of choices for the adjustable queries.
-- This is not one of the eight university tables.
CREATE TABLE settings (
    selected_group_id INTEGER NOT NULL,
    search_last_name TEXT NOT NULL,
    search_student_id INTEGER NOT NULL,
    filter_gender TEXT NOT NULL,
    filter_max_group_id INTEGER NOT NULL,
    grade_below INTEGER NOT NULL,
    free_day TEXT NOT NULL,
    free_start TEXT NOT NULL,
    free_end TEXT NOT NULL,
    selected_course_id INTEGER NOT NULL,
    selected_teacher_id INTEGER NOT NULL,
    selected_schedule_id INTEGER NOT NULL,
    selected_department_id INTEGER NOT NULL
);
""".strip()


def inserts_sql(tables):
    chunks = []
    order = [
        "Groups",
        "Departments",
        "Classrooms",
        "Teachers",
        "Courses",
        "Students",
        "Schedule",
        "Grades",
    ]
    for name in order:
        columns = cfg.COLUMNS[name]
        values = []
        for row in tables[name]:
            values.append("(" + ", ".join(sql_literal(value) for value in row) + ")")
        chunks.append(
            f"INSERT INTO {name} ({', '.join(columns)}) VALUES\n"
            + ",\n".join(values)
            + ";"
        )
    return "\n\n".join(chunks)


def settings_insert_sql():
    columns = [
        "selected_group_id",
        "search_last_name",
        "search_student_id",
        "filter_gender",
        "filter_max_group_id",
        "grade_below",
        "free_day",
        "free_start",
        "free_end",
        "selected_course_id",
        "selected_teacher_id",
        "selected_schedule_id",
        "selected_department_id",
    ]
    values = [
        cfg.SELECTED_GROUP_ID,
        cfg.SEARCH_LAST_NAME,
        cfg.SEARCH_STUDENT_ID,
        cfg.FILTER_GENDER,
        cfg.FILTER_MAX_GROUP_ID,
        cfg.GRADE_BELOW,
        cfg.FREE_DAY,
        cfg.FREE_START,
        cfg.FREE_END,
        cfg.SELECTED_COURSE_ID,
        cfg.SELECTED_TEACHER_ID,
        cfg.SELECTED_SCHEDULE_ID,
        cfg.SELECTED_DEPARTMENT_ID,
    ]
    lines = ["-- ADJUST THIS INSERT. Then run the queries that read settings.", "INSERT INTO settings ("]
    lines.append("    " + ",\n    ".join(columns))
    lines.append(") VALUES (")
    rendered = []
    notes = {
        0: "selected group",
        1: "search by last name",
        2: "search by student id",
        3: "two-condition filter: gender",
        4: "two-condition filter: group_id <= this value",
        5: "grades below this score",
        6: "day used for a free-classroom search",
        7: "free-classroom window starts",
        8: "free-classroom window ends",
        9: "course used in the extra queries",
        10: "teacher used in the extra queries",
        11: "schedule row used as one class",
        12: "department used in the extra queries",
    }
    for index, value in enumerate(values):
        comma = "," if index < len(values) - 1 else ""
        rendered.append(f"    {sql_literal(value)}{comma}  -- {notes[index]}")
    lines.append("\n".join(rendered))
    lines.append(");")
    return "\n".join(lines)


def build_queries():
    """Queries shown in the report, in task order."""
    group_id = cfg.SELECTED_GROUP_ID
    student_id = cfg.SEARCH_STUDENT_ID
    last_name = sql_literal(cfg.SEARCH_LAST_NAME)
    gender = sql_literal(cfg.FILTER_GENDER)
    max_group = cfg.FILTER_MAX_GROUP_ID
    return [
        q(
            "08_all_students",
            "Part 2",
            "All records from Students",
            "SELECT *\nFROM Students;",
            "Every column and every student.",
        ),
        q(
            "08_student_names",
            "Part 2",
            "Student id, first name and last name",
            "SELECT student_id, first_name, last_name\nFROM Students;",
            "The task asks for these three columns only.",
        ),
        q(
            "08_groups",
            "Part 2",
            "All records from Groups",
            "SELECT *\nFROM Groups;",
            "Group number, name, year and specialty.",
        ),
        q(
            "08_courses",
            "Part 2",
            "Names of all subjects",
            "SELECT course_name\nFROM Courses;",
            "Courses is the subjects table in this database.",
        ),
        q(
            "09_where",
            "Part 3",
            "Students in the selected group",
            f"SELECT *\nFROM Students\nWHERE group_id = {group_id};",
            "WHERE keeps only the rows that match.",
            settings_sql=(
                "SELECT *\nFROM Students\n"
                "WHERE group_id = (SELECT selected_group_id FROM settings);"
            ),
        ),
        q(
            "09_order",
            "Part 3",
            "Students in alphabetical order",
            "SELECT *\nFROM Students\nORDER BY last_name ASC;",
            "ORDER BY sorts the rows. It does not remove any.",
            settings_sql="SELECT *\nFROM Students\nORDER BY last_name ASC;",
        ),
        q(
            "09_count",
            "Part 3",
            "Total number of students",
            "SELECT COUNT(*) AS student_count\nFROM Students;",
            "COUNT(*) counts the rows.",
            settings_sql="SELECT COUNT(*) AS student_count\nFROM Students;",
        ),
        q(
            "09_group",
            "Part 3",
            "Number of students in each group",
            "SELECT group_id, COUNT(*) AS student_count\n"
            "FROM Students\n"
            "GROUP BY group_id\n"
            "ORDER BY group_id;",
            "GROUP BY makes COUNT return one row per group.",
            settings_sql=(
                "SELECT group_id, COUNT(*) AS student_count\n"
                "FROM Students\nGROUP BY group_id\nORDER BY group_id;"
            ),
        ),
        q(
            "09_max",
            "Part 3",
            "Maximum grade",
            "SELECT MAX(grade_value) AS maximum_grade\nFROM Grades;",
            "The grade column in this database is grade_value.",
            settings_sql="SELECT MAX(grade_value) AS maximum_grade\nFROM Grades;",
        ),
        q(
            "09_min",
            "Part 3",
            "Minimum grade",
            "SELECT MIN(grade_value) AS minimum_grade\nFROM Grades;",
            "MIN returns the lowest grade_value.",
            settings_sql="SELECT MIN(grade_value) AS minimum_grade\nFROM Grades;",
        ),
        q(
            "09_avg",
            "Part 3",
            "Average grade",
            "SELECT AVG(grade_value) AS average_grade\nFROM Grades;",
            "AVG returns the mean of grade_value.",
            settings_sql="SELECT AVG(grade_value) AS average_grade\nFROM Grades;",
        ),
        q(
            "10_students_groups",
            "Part 4",
            "Student name and group name",
            "SELECT\n"
            "    Students.student_id,\n"
            "    Students.first_name,\n"
            "    Students.last_name,\n"
            "    Groups.group_name,\n"
            "    Groups.specialty,\n"
            "    Groups.year_of_study\n"
            "FROM Students\n"
            "INNER JOIN Groups\n"
            "    ON Students.group_id = Groups.group_id\n"
            "ORDER BY Students.last_name, Students.first_name;",
            "Connected by Students.group_id = Groups.group_id.",
            settings_sql=(
                "SELECT\n"
                "    Students.student_id,\n"
                "    Students.first_name,\n"
                "    Students.last_name,\n"
                "    Groups.group_name,\n"
                "    Groups.specialty,\n"
                "    Groups.year_of_study\n"
                "FROM Students\n"
                "INNER JOIN Groups\n"
                "    ON Students.group_id = Groups.group_id\n"
                "ORDER BY Students.last_name, Students.first_name;"
            ),
        ),
        q(
            "10_students_grades",
            "Part 4",
            "Students and their grades",
            "SELECT\n"
            "    Students.student_id,\n"
            "    Students.first_name,\n"
            "    Students.last_name,\n"
            "    Grades.course_id,\n"
            "    Grades.grade_value,\n"
            "    Grades.grade_date\n"
            "FROM Students\n"
            "INNER JOIN Grades\n"
            "    ON Students.student_id = Grades.student_id\n"
            "ORDER BY Students.last_name, Students.first_name;",
            "Connected by Grades.student_id = Students.student_id.",
            settings_sql=(
                "SELECT\n"
                "    Students.student_id,\n"
                "    Students.first_name,\n"
                "    Students.last_name,\n"
                "    Grades.course_id,\n"
                "    Grades.grade_value,\n"
                "    Grades.grade_date\n"
                "FROM Students\n"
                "INNER JOIN Grades\n"
                "    ON Students.student_id = Grades.student_id\n"
                "ORDER BY Students.last_name, Students.first_name;"
            ),
        ),
        q(
            "10_subject_grade",
            "Part 4",
            "Student name, subject and grade",
            "SELECT\n"
            "    Students.first_name,\n"
            "    Students.last_name,\n"
            "    Courses.course_name AS subject,\n"
            "    Grades.grade_value,\n"
            "    Grades.grade_date\n"
            "FROM Students\n"
            "INNER JOIN Grades\n"
            "    ON Students.student_id = Grades.student_id\n"
            "INNER JOIN Courses\n"
            "    ON Grades.course_id = Courses.course_id\n"
            "ORDER BY Students.last_name, Students.first_name;",
            "Grades.course_id matches Courses.course_id. Courses stores the subject name.",
            settings_sql=(
                "SELECT\n"
                "    Students.first_name,\n"
                "    Students.last_name,\n"
                "    Courses.course_name AS subject,\n"
                "    Grades.grade_value,\n"
                "    Grades.grade_date\n"
                "FROM Students\n"
                "INNER JOIN Grades\n"
                "    ON Students.student_id = Grades.student_id\n"
                "INNER JOIN Courses\n"
                "    ON Grades.course_id = Courses.course_id\n"
                "ORDER BY Students.last_name, Students.first_name;"
            ),
        ),
        q(
            "10_inner",
            "Part 4",
            "INNER JOIN: departments and courses",
            "SELECT\n"
            "    Departments.department_name,\n"
            "    Courses.course_name\n"
            "FROM Departments\n"
            "INNER JOIN Courses\n"
            "    ON Departments.department_id = Courses.department_id\n"
            "ORDER BY Departments.department_id, Courses.course_name;",
            "A department with no course does not appear.",
            settings_sql=(
                "SELECT\n"
                "    Departments.department_name,\n"
                "    Courses.course_name\n"
                "FROM Departments\n"
                "INNER JOIN Courses\n"
                "    ON Departments.department_id = Courses.department_id\n"
                "ORDER BY Departments.department_id, Courses.course_name;"
            ),
        ),
        q(
            "10_left",
            "Part 4",
            "LEFT JOIN: every department",
            "SELECT\n"
            "    Departments.department_name,\n"
            "    Courses.course_name\n"
            "FROM Departments\n"
            "LEFT JOIN Courses\n"
            "    ON Departments.department_id = Courses.department_id\n"
            "ORDER BY Departments.department_id, Courses.course_name;",
            "Every department stays. A missing course is NULL.",
            settings_sql=(
                "SELECT\n"
                "    Departments.department_name,\n"
                "    Courses.course_name\n"
                "FROM Departments\n"
                "LEFT JOIN Courses\n"
                "    ON Departments.department_id = Courses.department_id\n"
                "ORDER BY Departments.department_id, Courses.course_name;"
            ),
        ),
        q(
            "10_compare",
            "Part 4",
            "One student before and after the JOIN",
            f"SELECT\n"
            f"    'Students table' AS source_table,\n"
            f"    student_id,\n"
            f"    first_name,\n"
            f"    last_name,\n"
            f"    CAST(group_id AS TEXT) AS group_info\n"
            f"FROM Students\n"
            f"WHERE student_id = {student_id}\n"
            f"UNION ALL\n"
            f"SELECT\n"
            f"    'Students JOIN Groups' AS source_table,\n"
            f"    Students.student_id,\n"
            f"    Students.first_name,\n"
            f"    Students.last_name,\n"
            f"    Groups.group_name\n"
            f"FROM Students\n"
            f"INNER JOIN Groups\n"
            f"    ON Students.group_id = Groups.group_id\n"
            f"WHERE Students.student_id = {student_id};",
            "The Students table stores the group id. The JOIN adds the group name.",
            settings_sql=(
                "SELECT\n"
                "    'Students table' AS source_table,\n"
                "    student_id,\n"
                "    first_name,\n"
                "    last_name,\n"
                "    CAST(group_id AS TEXT) AS group_info\n"
                "FROM Students\n"
                "WHERE student_id = (SELECT search_student_id FROM settings)\n"
                "UNION ALL\n"
                "SELECT\n"
                "    'Students JOIN Groups' AS source_table,\n"
                "    Students.student_id,\n"
                "    Students.first_name,\n"
                "    Students.last_name,\n"
                "    Groups.group_name\n"
                "FROM Students\n"
                "INNER JOIN Groups\n"
                "    ON Students.group_id = Groups.group_id\n"
                "WHERE Students.student_id = (SELECT search_student_id FROM settings);"
            ),
        ),
    ]


def topic7_queries():
    group_id = cfg.SELECTED_GROUP_ID
    student_id = cfg.SEARCH_STUDENT_ID
    last_name = sql_literal(cfg.SEARCH_LAST_NAME)
    gender = sql_literal(cfg.FILTER_GENDER)
    max_group = cfg.FILTER_MAX_GROUP_ID
    return [
        q(
            "07_sort_name_sql",
            "Topic 7 as SQL",
            "Sort students by last name",
            "SELECT *\nFROM Students\nORDER BY last_name ASC, first_name ASC;",
            "Same order as the Excel sheet 07_Sort_Last_Name.",
            screenshot=False,
        ),
        q(
            "07_sort_group_sql",
            "Topic 7 as SQL",
            "Sort students by group",
            "SELECT *\nFROM Students\nORDER BY group_id ASC, last_name ASC;",
            "Same order as the Excel sheet 07_Sort_Group.",
            screenshot=False,
        ),
        q(
            "07_one_group_sql",
            "Topic 7 as SQL",
            "Filter one group",
            f"SELECT *\nFROM Students\nWHERE group_id = {group_id}\nORDER BY last_name;",
            "Same rows as the Excel sheet 07_Filter_One_Group.",
            screenshot=False,
            settings_sql=(
                "SELECT *\nFROM Students\n"
                "WHERE group_id = (SELECT selected_group_id FROM settings)\n"
                "ORDER BY last_name;"
            ),
        ),
        q(
            "07_search_id_sql",
            "Topic 7 as SQL",
            "Search by student id",
            f"SELECT *\nFROM Students\nWHERE student_id = {student_id};",
            "Same rows as the first table on 07_Search.",
            screenshot=False,
            settings_sql=(
                "SELECT *\nFROM Students\n"
                "WHERE student_id = (SELECT search_student_id FROM settings);"
            ),
        ),
        q(
            "07_search_name_sql",
            "Topic 7 as SQL",
            "Search by last name",
            f"SELECT *\nFROM Students\nWHERE last_name COLLATE NOCASE = {last_name};",
            "The search ignores capital letters.",
            screenshot=False,
            settings_sql=(
                "SELECT *\nFROM Students\n"
                "WHERE last_name COLLATE NOCASE = "
                "(SELECT search_last_name FROM settings);"
            ),
        ),
        q(
            "07_two_sql",
            "Topic 7 as SQL",
            "Filter with two conditions",
            f"SELECT *\nFROM Students\n"
            f"WHERE gender = {gender}\n"
            f"  AND group_id <= {max_group}\n"
            f"ORDER BY group_id, last_name;",
            "Both conditions must be true.",
            screenshot=False,
            settings_sql=(
                "SELECT *\nFROM Students\n"
                "WHERE gender = (SELECT filter_gender FROM settings)\n"
                "  AND group_id <= (SELECT filter_max_group_id FROM settings)\n"
                "ORDER BY group_id, last_name;"
            ),
        ),
    ]


def extra_queries():
    return [
        q(
            "ex_group_students",
            "Extra",
            "Practice 1. Students in a selected group",
            "SELECT student_id, last_name, first_name, group_id\n"
            "FROM Students\n"
            "WHERE group_id = (SELECT selected_group_id FROM settings)\n"
            "ORDER BY last_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_student_group",
            "Extra",
            "Practice 1. Group of a selected student",
            "SELECT\n"
            "    s.student_id, s.last_name, s.first_name,\n"
            "    g.group_name, g.year_of_study, g.specialty\n"
            "FROM Students s\n"
            "INNER JOIN Groups g ON s.group_id = g.group_id\n"
            "WHERE s.student_id = (SELECT search_student_id FROM settings);",
            "",
            screenshot=False,
        ),
        q(
            "ex_student_courses",
            "Extra",
            "Practice 1. Courses a student studies",
            "SELECT s.last_name, s.first_name, c.course_name, c.credits, c.semester\n"
            "FROM Students s\n"
            "INNER JOIN Schedule sch ON sch.group_id = s.group_id\n"
            "INNER JOIN Courses c ON c.course_id = sch.course_id\n"
            "WHERE s.student_id = (SELECT search_student_id FROM settings)\n"
            "ORDER BY c.course_name;",
            "A student's courses are the courses scheduled for that student's group.",
            screenshot=False,
        ),
        q(
            "ex_student_grades",
            "Extra",
            "Practice 1. Grades of a selected student",
            "SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date\n"
            "FROM Students s\n"
            "INNER JOIN Grades g ON g.student_id = s.student_id\n"
            "INNER JOIN Courses c ON c.course_id = g.course_id\n"
            "WHERE s.student_id = (SELECT search_student_id FROM settings)\n"
            "ORDER BY g.grade_date;",
            "",
            screenshot=False,
        ),
        q(
            "ex_student_avg",
            "Extra",
            "Practice 1. Average grade of a selected student",
            "SELECT\n"
            "    s.last_name,\n"
            "    s.first_name,\n"
            "    ROUND(AVG(g.grade_value), 2) AS average_grade\n"
            "FROM Students s\n"
            "INNER JOIN Grades g ON g.student_id = s.student_id\n"
            "WHERE s.student_id = (SELECT search_student_id FROM settings)\n"
            "GROUP BY s.student_id, s.last_name, s.first_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_course_teacher",
            "Extra",
            "Practice 1. Teacher of a selected course",
            "SELECT c.course_name, t.first_name, t.last_name, t.academic_degree\n"
            "FROM Courses c\n"
            "INNER JOIN Schedule sch ON sch.course_id = c.course_id\n"
            "INNER JOIN Teachers t ON t.teacher_id = sch.teacher_id\n"
            "WHERE c.course_id = (SELECT selected_course_id FROM settings)\n"
            "ORDER BY t.last_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_teacher_courses",
            "Extra",
            "Practice 1. Courses of a selected teacher",
            "SELECT t.first_name, t.last_name, c.course_name\n"
            "FROM Teachers t\n"
            "INNER JOIN Schedule sch ON sch.teacher_id = t.teacher_id\n"
            "INNER JOIN Courses c ON c.course_id = sch.course_id\n"
            "WHERE t.teacher_id = (SELECT selected_teacher_id FROM settings)\n"
            "ORDER BY c.course_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_group_schedule",
            "Extra",
            "Practice 1. Schedule of a selected group",
            "SELECT\n"
            "    g.group_name,\n"
            "    c.course_name,\n"
            "    t.first_name || ' ' || t.last_name AS teacher,\n"
            "    cl.room_number,\n"
            "    cl.building,\n"
            "    sch.day_of_week,\n"
            "    sch.start_time,\n"
            "    sch.end_time\n"
            "FROM Schedule sch\n"
            "INNER JOIN Groups g ON g.group_id = sch.group_id\n"
            "INNER JOIN Courses c ON c.course_id = sch.course_id\n"
            "INNER JOIN Teachers t ON t.teacher_id = sch.teacher_id\n"
            "INNER JOIN Classrooms cl ON cl.classroom_id = sch.classroom_id\n"
            "WHERE sch.group_id = (SELECT selected_group_id FROM settings)\n"
            "ORDER BY sch.day_of_week, sch.start_time;",
            "",
            screenshot=False,
        ),
        q(
            "ex_teacher_schedule",
            "Extra",
            "Practice 1. Schedule of a selected teacher",
            "SELECT\n"
            "    t.first_name || ' ' || t.last_name AS teacher,\n"
            "    c.course_name,\n"
            "    g.group_name,\n"
            "    cl.room_number,\n"
            "    cl.building,\n"
            "    sch.day_of_week,\n"
            "    sch.start_time,\n"
            "    sch.end_time\n"
            "FROM Schedule sch\n"
            "INNER JOIN Teachers t ON t.teacher_id = sch.teacher_id\n"
            "INNER JOIN Courses c ON c.course_id = sch.course_id\n"
            "INNER JOIN Groups g ON g.group_id = sch.group_id\n"
            "INNER JOIN Classrooms cl ON cl.classroom_id = sch.classroom_id\n"
            "WHERE sch.teacher_id = (SELECT selected_teacher_id FROM settings)\n"
            "ORDER BY sch.day_of_week, sch.start_time;",
            "",
            screenshot=False,
        ),
        q(
            "ex_classroom",
            "Extra",
            "Practice 1. Classroom of a selected class",
            "SELECT\n"
            "    sch.schedule_id,\n"
            "    c.course_name,\n"
            "    cl.room_number,\n"
            "    cl.building,\n"
            "    cl.capacity,\n"
            "    sch.day_of_week,\n"
            "    sch.start_time,\n"
            "    sch.end_time\n"
            "FROM Schedule sch\n"
            "INNER JOIN Courses c ON c.course_id = sch.course_id\n"
            "INNER JOIN Classrooms cl ON cl.classroom_id = sch.classroom_id\n"
            "WHERE sch.schedule_id = (SELECT selected_schedule_id FROM settings);",
            "",
            screenshot=False,
        ),
        q(
            "ex_department_courses",
            "Extra",
            "Practice 1. Courses of a selected department",
            "SELECT d.department_name, c.course_name, c.credits, c.semester\n"
            "FROM Departments d\n"
            "INNER JOIN Courses c ON c.department_id = d.department_id\n"
            "WHERE d.department_id = (SELECT selected_department_id FROM settings)\n"
            "ORDER BY c.course_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_students_per_group",
            "Extra",
            "Practice 1. How many students are in each group",
            "SELECT g.group_id, g.group_name, COUNT(s.student_id) AS student_count\n"
            "FROM Groups g\n"
            "LEFT JOIN Students s ON s.group_id = g.group_id\n"
            "GROUP BY g.group_id, g.group_name\n"
            "ORDER BY g.group_id;",
            "LEFT JOIN keeps a group even when it has no students.",
            screenshot=False,
        ),
        q(
            "ex_top_averages",
            "Extra",
            "Practice 1. Highest average grades",
            "SELECT\n"
            "    s.student_id,\n"
            "    s.last_name,\n"
            "    s.first_name,\n"
            "    ROUND(AVG(g.grade_value), 2) AS average_grade\n"
            "FROM Students s\n"
            "INNER JOIN Grades g ON g.student_id = s.student_id\n"
            "GROUP BY s.student_id, s.last_name, s.first_name\n"
            "ORDER BY average_grade DESC, s.last_name\n"
            "LIMIT 5;",
            "",
            screenshot=False,
        ),
        q(
            "ex_below",
            "Extra",
            "Practice 1. Grades below a chosen score",
            "SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date\n"
            "FROM Grades g\n"
            "INNER JOIN Students s ON s.student_id = g.student_id\n"
            "INNER JOIN Courses c ON c.course_id = g.course_id\n"
            "WHERE g.grade_value < (SELECT grade_below FROM settings)\n"
            "ORDER BY g.grade_value, s.last_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_free_rooms",
            "Extra",
            "Practice 1. Classrooms free at a chosen time",
            "SELECT cl.classroom_id, cl.room_number, cl.building, cl.capacity\n"
            "FROM Classrooms cl\n"
            "CROSS JOIN settings st\n"
            "WHERE NOT EXISTS (\n"
            "    SELECT 1\n"
            "    FROM Schedule sch\n"
            "    WHERE sch.classroom_id = cl.classroom_id\n"
            "      AND sch.day_of_week = st.free_day\n"
            "      AND sch.start_time < st.free_end\n"
            "      AND sch.end_time > st.free_start\n"
            ")\n"
            "ORDER BY cl.classroom_id;",
            "A room is busy when its class overlaps the chosen window.",
            screenshot=False,
        ),
        q(
            "ex_who_max",
            "Extra",
            "Who received the maximum grade",
            "SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date\n"
            "FROM Grades g\n"
            "INNER JOIN Students s ON s.student_id = g.student_id\n"
            "INNER JOIN Courses c ON c.course_id = g.course_id\n"
            "WHERE g.grade_value = (SELECT MAX(grade_value) FROM Grades)\n"
            "ORDER BY s.last_name;",
            "",
            screenshot=False,
        ),
        q(
            "ex_who_min",
            "Extra",
            "Who received the minimum grade",
            "SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date\n"
            "FROM Grades g\n"
            "INNER JOIN Students s ON s.student_id = g.student_id\n"
            "INNER JOIN Courses c ON c.course_id = g.course_id\n"
            "WHERE g.grade_value = (SELECT MIN(grade_value) FROM Grades)\n"
            "ORDER BY s.last_name;",
            "",
            screenshot=False,
        ),
    ]


def q(key, part, title, sql, note, settings_sql=None, screenshot=True):
    return {
        "key": key,
        "part": part,
        "title": title,
        "sql": sql.strip() + ("" if sql.strip().endswith(";") else ";"),
        "note": note,
        "settings_sql": None
        if settings_sql is None
        else settings_sql.strip() + ("" if settings_sql.strip().endswith(";") else ";"),
        "screenshot": screenshot,
    }


def dict_rows(table_name, tables):
    columns = cfg.COLUMNS[table_name]
    return [dict(zip(columns, row)) for row in tables[table_name]]


def person_name(row):
    return f"{row['first_name']} {row['last_name']}"


def check_tables(tables):
    students = dict_rows("Students", tables)
    groups = dict_rows("Groups", tables)
    teachers = dict_rows("Teachers", tables)
    departments = dict_rows("Departments", tables)
    courses = dict_rows("Courses", tables)
    classrooms = dict_rows("Classrooms", tables)
    schedule = dict_rows("Schedule", tables)
    grades = dict_rows("Grades", tables)
    today = date.today().isoformat()

    def unique(rows, key):
        values = [row[key] for row in rows]
        if len(values) != len(set(values)):
            fail(f"Duplicate {key}")

    for rows, key in (
        (students, "student_id"),
        (groups, "group_id"),
        (teachers, "teacher_id"),
        (departments, "department_id"),
        (courses, "course_id"),
        (classrooms, "classroom_id"),
        (schedule, "schedule_id"),
        (grades, "grade_id"),
    ):
        unique(rows, key)
    unique(students, "email")
    unique(teachers, "email")

    group_ids = {row["group_id"] for row in groups}
    department_ids = {row["department_id"] for row in departments}
    course_ids = {row["course_id"] for row in courses}
    teacher_ids = {row["teacher_id"] for row in teachers}
    classroom_ids = {row["classroom_id"] for row in classrooms}
    student_ids = {row["student_id"] for row in students}

    for row in students:
        if row["group_id"] not in group_ids:
            fail(f"Student {row['student_id']} has a missing group")
        if row["birth_date"] > today:
            fail(f"Student {row['student_id']} has a future birth date")
        if row["gender"] not in ("F", "M"):
            fail("Gender must be F or M")
    for row in teachers:
        if row["department_id"] not in department_ids:
            fail(f"Teacher {row['teacher_id']} has a missing department")
    for row in courses:
        if row["department_id"] not in department_ids:
            fail(f"Course {row['course_id']} has a missing department")
        if row["credits"] <= 0:
            fail("Credits must be greater than 0")
    for row in classrooms:
        if row["capacity"] <= 0:
            fail("Capacity must be greater than 0")
    seen_grade = set()
    for row in grades:
        if row["student_id"] not in student_ids or row["course_id"] not in course_ids:
            fail(f"Grade {row['grade_id']} points at a missing student or course")
        if not 0 <= row["grade_value"] <= 100:
            fail("Grade must be from 0 to 100")
        key = (row["student_id"], row["course_id"], row["grade_date"])
        if key in seen_grade:
            fail("Duplicate grade for the same student, course and date")
        seen_grade.add(key)
    for row in schedule:
        if row["course_id"] not in course_ids:
            fail("Schedule course is missing")
        if row["teacher_id"] not in teacher_ids:
            fail("Schedule teacher is missing")
        if row["group_id"] not in group_ids:
            fail("Schedule group is missing")
        if row["classroom_id"] not in classroom_ids:
            fail("Schedule classroom is missing")
        if row["end_time"] <= row["start_time"]:
            fail("Class end time must be later than the start time")

    return {
        "students": students,
        "groups": groups,
        "teachers": teachers,
        "departments": departments,
        "courses": courses,
        "classrooms": classrooms,
        "schedule": schedule,
        "grades": grades,
    }


def overlaps(start_a, end_a, start_b, end_b):
    return start_a < end_b and end_a > start_b


def expected_filters(data):
    students = data["students"]
    one_group = [row for row in students if row["group_id"] == cfg.SELECTED_GROUP_ID]
    by_id = [row for row in students if row["student_id"] == cfg.SEARCH_STUDENT_ID]
    by_name = [
        row
        for row in students
        if row["last_name"].casefold() == cfg.SEARCH_LAST_NAME.casefold()
    ]
    two = [
        row
        for row in students
        if row["gender"] == cfg.FILTER_GENDER and row["group_id"] <= cfg.FILTER_MAX_GROUP_ID
    ]
    by_last = sorted(students, key=lambda row: (row["last_name"].casefold(), row["first_name"].casefold()))
    by_group = sorted(students, key=lambda row: (row["group_id"], row["last_name"].casefold()))
    return one_group, by_id, by_name, two, by_last, by_group


def render_sql_file(queries, topic7, extras, tables):
    group_line = cfg.STUDENT_GROUP.strip() or "(write your group in adjust_here.py)"
    header = f"""-- Practical Work 7-10
-- Data sorting, filtering, SQL queries and joining tables
-- University database from Practice Work 2
-- Student: {cfg.STUDENT_NAME}
-- Group: {group_line}
-- Date: {cfg.REPORT_DATE}
--
-- The task sheet says Subjects and grade.
-- In this database the subject table is Courses, and the grade column is grade_value.
--
-- HOW TO ADJUST WITHOUT REBUILDING
-- 1. Edit the INSERT into settings (the block marked ADJUST THIS INSERT).
-- 2. Run the section "Queries that read the settings table".
--    Also run "Extra queries from Practice Work 1".
-- Parts 2, 3 and 4 below repeat the same values directly, so each query
-- can be read on its own. To rewrite those copies as well, edit
-- adjust_here.py and run:  python3 build.py
--
-- Open this database in SQLiteStudio or DB Browser for SQLite:
--     db/university.sqlite
-- Or from the terminal, inside the practical-7-10 folder:
--     sqlite3 db/university.sqlite
"""
    parts = [header, schema_sql(), "", inserts_sql(tables), "", settings_insert_sql(), ""]

    def add_section(title, items, use_settings=False):
        parts.append("-" * 72)
        parts.append(f"-- {title}")
        parts.append("-" * 72)
        parts.append("")
        for item in items:
            sql = item["settings_sql"] if use_settings else item["sql"]
            if use_settings and not sql:
                continue
            parts.append(f"-- {item['part']}. {item['title']}")
            if item["note"]:
                parts.append(f"-- {item['note']}")
            parts.append(sql)
            parts.append("")

    add_section("Part 2, Part 3 and Part 4", queries)
    add_section("Topic 7 as SQL. Same filters as the Excel result sheets", topic7)
    add_section(
        "Queries that read the settings table. Run these after you edit settings",
        queries + topic7,
        use_settings=True,
    )
    add_section("Extra queries from Practice Work 1", extras)
    text = "\n".join(parts).rstrip() + "\n"
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.write_text(text, encoding="utf-8")
    return text


def load_database(setup_sql):
    OUT_DB.parent.mkdir(parents=True, exist_ok=True)
    if OUT_DB.exists():
        OUT_DB.unlink()
    connection = sqlite3.connect(OUT_DB)
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(setup_sql)
    connection.commit()
    return connection


def run_select(connection, sql):
    cursor = connection.execute(sql)
    headers = [item[0] for item in cursor.description]
    rows = cursor.fetchall()
    return headers, rows


def format_result(headers, rows):
    shown = [[("NULL" if value is None else str(value)) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in shown:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def line(values):
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    separator = "-+-".join("-" * width for width in widths)
    lines = [line(headers), separator]
    lines.extend(line(row) for row in shown)
    if not shown:
        lines.append("(no rows)")
    else:
        noun = "row" if len(shown) == 1 else "rows"
        lines.append(f"({len(shown)} {noun})")
    return "\n".join(lines)


def ids_of(rows, index):
    return [row[index] for row in rows]


def assert_same_rows(left, right, label):
    if list(left) != list(right):
        fail(f"{label} did not match the settings query.")


def check_queries(connection, data, queries, topic7, extras):
    students = data["students"]
    grades = data["grades"]
    one_group, by_id, by_name, two, by_last, by_group = expected_filters(data)
    results = {}

    def execute(item, sql=None):
        headers, rows = run_select(connection, sql or item["sql"])
        results[item["key"]] = (headers, rows, item)
        return headers, rows

    for item in queries + topic7:
        _, rows = execute(item)
        if item["settings_sql"]:
            _, settings_rows = run_select(connection, item["settings_sql"])
            assert_same_rows(rows, settings_rows, item["title"])

    for item in extras:
        execute(item)

    def student_ids(rows):
        return [row[0] for row in rows]

    _, where_rows, _ = results["09_where"]
    if student_ids(where_rows) != [row["student_id"] for row in one_group]:
        fail("WHERE group filter returned unexpected students.")

    _, order_rows, _ = results["09_order"]
    if [row[1] for row in order_rows] != [row["last_name"] for row in by_last]:
        # SELECT * column 1 is last_name
        fail("ORDER BY last_name is not alphabetical.")

    _, count_rows, _ = results["09_count"]
    if count_rows[0][0] != len(students):
        fail("COUNT(*) is wrong.")

    _, group_rows, _ = results["09_group"]
    counts = Counter(row["group_id"] for row in students)
    if [(row[0], row[1]) for row in group_rows] != sorted(counts.items()):
        fail("GROUP BY counts are wrong.")

    _, max_rows, _ = results["09_max"]
    _, min_rows, _ = results["09_min"]
    _, avg_rows, _ = results["09_avg"]
    values = [row["grade_value"] for row in grades]
    if max_rows[0][0] != max(values) or min_rows[0][0] != min(values):
        fail("MAX or MIN is wrong.")
    if abs(avg_rows[0][0] - (sum(values) / len(values))) > 1e-9:
        fail("AVG is wrong.")

    _, join_rows, _ = results["10_students_groups"]
    if len(join_rows) != len(students):
        fail("Students JOIN Groups dropped or duplicated students.")
    _, grade_rows, _ = results["10_students_grades"]
    if len(grade_rows) != len(grades):
        # True when every grade belongs to one student and the join is inner.
        # If a grade points at a real student this equals the grade count.
        fail("Students JOIN Grades has an unexpected number of rows.")

    courses = data["courses"]
    departments = data["departments"]
    course_departments = {row["department_id"] for row in courses}
    empty_departments = [
        row["department_name"]
        for row in departments
        if row["department_id"] not in course_departments
    ]
    _, inner_rows, _ = results["10_inner"]
    _, left_rows, _ = results["10_left"]
    if len(inner_rows) != len(courses):
        fail("INNER JOIN Departments/Courses should return one row per course.")
    if len(left_rows) != len(courses) + len(empty_departments):
        fail("LEFT JOIN Departments/Courses has an unexpected number of rows.")

    _, name_rows, _ = results["07_search_name_sql"]
    if [row[0] for row in name_rows] != [row["student_id"] for row in by_name]:
        fail("Last-name search returned unexpected students.")
    _, id_rows, _ = results["07_search_id_sql"]
    if [row[0] for row in id_rows] != [row["student_id"] for row in by_id]:
        fail("Student-id search returned unexpected students.")
    _, two_rows, _ = results["07_two_sql"]
    if [row[0] for row in two_rows] != [row["student_id"] for row in sorted(two, key=lambda row: (row["group_id"], row["last_name"].casefold()))]:
        fail("Two-condition filter returned unexpected students.")

    _, free_rows, _ = results["ex_free_rooms"]
    busy = set()
    for row in data["schedule"]:
        if row["day_of_week"] == cfg.FREE_DAY and overlaps(
            row["start_time"], row["end_time"], cfg.FREE_START, cfg.FREE_END
        ):
            busy.add(row["classroom_id"])
    free_ids = [
        row["classroom_id"]
        for row in data["classrooms"]
        if row["classroom_id"] not in busy
    ]
    if [row[0] for row in free_rows] != free_ids:
        fail("Free-classroom query returned unexpected rooms.")

    _, below_rows, _ = results["ex_below"]
    expected_below = sorted(
        (
            row
            for row in grades
            if row["grade_value"] < cfg.GRADE_BELOW
        ),
        key=lambda row: (row["grade_value"], next(s["last_name"] for s in students if s["student_id"] == row["student_id"])),
    )
    if len(below_rows) != len(expected_below):
        fail("Grades-below query returned an unexpected number of rows.")

    # A bad foreign key must be rejected.
    probe = sqlite3.connect(":memory:")
    probe.execute("PRAGMA foreign_keys = ON;")
    probe.executescript(schema_sql())
    try:
        probe.execute(
            "INSERT INTO Students (student_id, last_name, first_name, birth_date, gender, phone, email, group_id) "
            "VALUES (1, 'Test', 'Test', '2004-01-01', 'F', '1', 't@example.com', 999)"
        )
        fail("A student with a missing group was accepted.")
    except sqlite3.IntegrityError:
        pass
    finally:
        probe.close()

    return results


def write_results_log(results, ordered_items):
    chunks = []
    for item in ordered_items:
        headers, rows, _stored = results[item["key"]]
        chunks.append("=" * 72)
        chunks.append(f"{item['part']}. {item['title']}")
        chunks.append(item["sql"])
        chunks.append(format_result(headers, rows))
        chunks.append("")
    OUT_RESULTS.write_text("\n".join(chunks), encoding="utf-8")


def excel_value(column, value):
    if value is None:
        return None
    if column in ("birth_date", "grade_date"):
        return datetime.strptime(value, "%Y-%m-%d").date()
    if column in ("start_time", "end_time"):
        return datetime.strptime(value, "%H:%M:%S").time()
    return value


def apply_number_format(cell, column):
    if column in ("birth_date", "grade_date"):
        cell.number_format = "YYYY-MM-DD"
    elif column in ("start_time", "end_time"):
        cell.number_format = "HH:MM"


def paint_header(ws, row, headers):
    for column, name in enumerate(headers, start=1):
        cell = ws.cell(row, column, name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = THIN


def write_data_sheet(wb, title, rows, columns, tab_color):
    ws = wb.create_sheet(title)
    ws.sheet_properties.tabColor = tab_color
    paint_header(ws, 1, columns)
    center_columns = {
        "student_id",
        "group_id",
        "teacher_id",
        "department_id",
        "course_id",
        "classroom_id",
        "schedule_id",
        "grade_id",
        "gender",
        "credits",
        "semester",
        "capacity",
        "year_of_study",
        "grade_value",
        "room_number",
    }
    for row_index, row in enumerate(rows, start=2):
        for col_index, name in enumerate(columns, start=1):
            value = excel_value(name, row[col_index - 1])
            cell = ws.cell(row_index, col_index, value)
            cell.font = BODY_FONT
            cell.border = THIN
            cell.alignment = CENTER if name in center_columns else LEFT_ALIGN
            apply_number_format(cell, name)
            if row_index % 2 == 0:
                cell.fill = ALT
    last_row = max(2, 1 + len(rows))
    ref = f"A1:{get_column_letter(len(columns))}{last_row}"
    table = Table(displayName=f"tbl{title}", ref=ref)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(table)
    ws.freeze_panes = "A2"
    fit_columns(ws, min_width=12, max_width=46)
    prepare_print(ws, title)
    ws.print_title_rows = "1:1"
    return ws


def fit_columns(ws, min_width=12, max_width=42):
    for column in ws.columns:
        letter = get_column_letter(column[0].column)
        longest = 0
        for cell in column:
            if cell.value is None:
                continue
            longest = max(longest, min(len(str(cell.value)), max_width))
        ws.column_dimensions[letter].width = max(min_width, longest + 2)


def prepare_print(ws, title):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_setup.horizontalCentered = True
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddHeader.left.text = "Practical Work 7-10"
    ws.oddHeader.right.text = title
    ws.oddFooter.right.text = "Page &P of &N"
    ws.page_setup.leftMargin = 0.4
    ws.page_setup.rightMargin = 0.4
    ws.sheet_view.showGridLines = False


def write_result_sheet(wb, title, note, headers, rows, tab_color):
    ws = wb.create_sheet(title)
    ws.sheet_properties.tabColor = tab_color
    span = max(len(headers), 4)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    ws["A1"] = title.replace("_", " ")
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = LEFT_ALIGN
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    ws["A2"] = note
    ws["A2"].font = NOTE_FONT
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 36
    paint_header(ws, 4, headers)
    if not rows:
        ws["A5"] = "No rows match these settings."
        ws["A5"].font = Font(name="Calibri", italic=True, color=RED, size=12)
    for row_index, row in enumerate(rows, start=5):
        for col_index, value in enumerate(row, start=1):
            column = headers[col_index - 1]
            cell = ws.cell(row_index, col_index, excel_value(column, value))
            cell.font = BODY_FONT
            cell.border = THIN
            cell.alignment = LEFT_ALIGN
            apply_number_format(cell, column)
            if value is None:
                cell.value = "NULL"
                cell.font = Font(name="Calibri", italic=True, color="808080", size=11)
            elif row_index % 2 == 1:
                cell.fill = ALT
    last_row = 4 if not rows else 4 + len(rows)
    if rows:
        ref = f"A4:{get_column_letter(len(headers))}{last_row}"
        safe_name = "tbl" + "".join(ch for ch in title if ch.isalnum())
        table = Table(displayName=safe_name[:40], ref=ref)
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(table)
        ws.freeze_panes = "A5"
    fit_columns(ws, max_width=40)
    for column in range(1, span + 1):
        letter = get_column_letter(column)
        ws.column_dimensions[letter].width = max(ws.column_dimensions[letter].width or 12, 14)
    prepare_print(ws, title)
    return ws


def write_live_sheet(wb, title, note, headers, formula):
    ws = wb.create_sheet(title)
    ws.sheet_properties.tabColor = "ED7D31"
    span = max(len(headers), 4)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    ws["A1"] = "OPTIONAL live sheet — Excel 365 or Google Sheets"
    ws["A1"].font = Font(name="Calibri", bold=True, color=RED, size=14)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    ws["A2"] = note
    ws["A2"].font = NOTE_FONT
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 48
    paint_header(ws, 4, headers)
    ws["A5"] = formula
    ws["A5"].font = Font(name="Calibri", size=11)
    fit_columns(ws, max_width=28)
    prepare_print(ws, title)
    return ws


def write_start_and_settings(wb, data):
    ws = wb.active
    ws.title = "Start_Here"
    ws.sheet_properties.tabColor = NAVY
    group_text = cfg.STUDENT_GROUP.strip() or "(type your group in the Your group row on the Settings sheet)"
    selected = next(
        (row for row in data["groups"] if row["group_id"] == cfg.SELECTED_GROUP_ID),
        None,
    )
    if selected:
        selected_text = (
            f"{selected['group_id']} — {selected['group_name']}, "
            f"year {selected['year_of_study']}, {selected['specialty']}"
        )
    else:
        selected_text = f"{cfg.SELECTED_GROUP_ID} (this group id is not in Groups)"
    lines = [
        "Practical Work №7–10",
        "Sorting, filtering, SQL queries and joining tables",
        f"Student: {cfg.STUDENT_NAME}",
        f"Group: {group_text}",
        f"Date: {cfg.REPORT_DATE}",
        "",
        "This workbook continues the university database from Practice Work 2.",
        "It has eight tables: Students, Groups, Teachers, Departments, Courses, Classrooms, Schedule and Grades.",
        "The task sheet says Subjects. In this database that table is called Courses.",
        "The task sheet says grade. In this database the column is called grade_value, from 0 to 100.",
        "",
        "Saved examples (green and blue result sheets)",
        f"Selected group: {selected_text}",
        f"Search by last name: {cfg.SEARCH_LAST_NAME}",
        f"Search by student id: {cfg.SEARCH_STUDENT_ID}",
        f"Two conditions: gender = {cfg.FILTER_GENDER} and group_id <= {cfg.FILTER_MAX_GROUP_ID}",
        "",
        "How to adjust the work",
        "1. Excel filter arrows. Open Students, Groups or any other data sheet. The header arrows sort and filter. This is the Topic 7 method, and it works in Excel and in Google Sheets.",
        "2. Yellow Settings cells plus the orange Live sheets. Change a yellow value. The Live sheets use SORT and FILTER and update in Excel 365 and in Google Sheets. If a Live sheet shows #NAME?, leave it and use the saved sheets plus the filter arrows. Your group is the yellow cell in the Your group row.",
        "3. SQL settings. Open sql/practical_work_7_10.sql and edit the INSERT into settings. Then run the section “Queries that read the settings table”. The database file is db/university.sqlite.",
        "4. Rebuild everything from one place. Edit the ADJUST block in adjust_here.py and run python3 build.py. That rewrites this workbook, the SQL script, the screenshots and the report together.",
        "",
        "Sheet guide",
        "Settings — yellow cells for the examples, and your name and group.",
        "Students … Grades — the eight tables from Practice Work 2.",
        "07_ sheets — saved sort, filter and search results.",
        "10_ sheets — saved JOIN results, so they can be compared with the original tables.",
        "Live_ sheets — optional formulas that follow the Settings sheet.",
        "",
        "SQL script: sql/practical_work_7_10.sql",
        "Report: report/Practical_Work_7-10.docx",
        "",
        "Do not insert rows above the yellow values on Settings. Edit the values in place.",
        "build.py overwrites this workbook. If you want to keep hand-made Excel changes, do that after the last rebuild.",
    ]
    ws.merge_cells("A1:G1")
    for index, line in enumerate(lines, start=1):
        cell = ws.cell(index, 1, line if line else None)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        if index == 1:
            cell.font = Font(name="Calibri", bold=True, size=20, color=NAVY)
            ws.row_dimensions[index].height = 28
        elif line.endswith("sheets)") or line in ("How to adjust the work", "Sheet guide"):
            cell.font = LABEL_FONT
            ws.row_dimensions[index].height = 20
        else:
            cell.font = Font(name="Calibri", size=12)
            ws.row_dimensions[index].height = 18 if len(line) < 110 else 32
        ws.merge_cells(start_row=index, start_column=1, end_row=index, end_column=7)
    ws.column_dimensions["A"].width = 28
    for letter in "BCDEFG":
        ws.column_dimensions[letter].width = 18
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.sheet_view.showGridLines = False
    ws.oddFooter.right.text = "Practical Work 7-10"

    settings = wb.create_sheet("Settings", 1)
    settings.sheet_properties.tabColor = "BF8F00"
    settings["A1"] = "Settings for the examples"
    settings["A1"].font = TITLE_FONT
    settings.merge_cells("A1:C1")
    settings["A2"] = (
        "Yellow cells are the values used to build the saved sheets. "
        "The orange Live sheets read these cells directly. "
        "Type a new value, or pick one from the list."
    )
    settings["A2"].font = NOTE_FONT
    settings["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    settings.merge_cells("A2:C2")
    settings.row_dimensions[2].height = 32
    headers = ["Setting", "Value", "Where it is used"]
    for column, name in enumerate(headers, start=1):
        cell = settings.cell(4, column, name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
    setting_rows = [
        ("Selected group_id", cfg.SELECTED_GROUP_ID, "One-group filter, and SQL WHERE group_id"),
        ("Search last name", cfg.SEARCH_LAST_NAME, "Search by last name"),
        ("Search student_id", cfg.SEARCH_STUDENT_ID, "Search by student id"),
        ("Gender", cfg.FILTER_GENDER, "Two-condition filter, condition 1"),
        ("Maximum group_id", cfg.FILTER_MAX_GROUP_ID, "Two-condition filter, condition 2: group_id <= this value"),
        ("Grade below", cfg.GRADE_BELOW, "Extra SQL query: grades below this score"),
        ("Free day", cfg.FREE_DAY, "Extra SQL query: classrooms free on this day"),
        ("Free window start", cfg.FREE_START, "Extra SQL query: free-classroom window"),
        ("Free window end", cfg.FREE_END, "Extra SQL query: free-classroom window"),
        ("Your name", cfg.STUDENT_NAME, "Cover and report"),
        ("Your group", cfg.STUDENT_GROUP, "Type your group here before you submit"),
    ]
    for offset, (label, value, used) in enumerate(setting_rows):
        row = 5 + offset
        settings.cell(row, 1, label).font = Font(name="Calibri", size=11)
        value_cell = settings.cell(row, 2, value if value != "" else None)
        value_cell.fill = YELLOW
        value_cell.font = Font(name="Calibri", bold=True, size=12)
        value_cell.alignment = CENTER
        value_cell.border = THIN
        settings.cell(row, 1).border = THIN
        settings.cell(row, 1).alignment = LEFT_ALIGN
        used_cell = settings.cell(row, 3, used)
        used_cell.font = NOTE_FONT
        used_cell.alignment = LEFT_ALIGN
        used_cell.border = THIN
        settings.row_dimensions[row].height = 22
    settings.column_dimensions["A"].width = 24
    settings.column_dimensions["B"].width = 22
    settings.column_dimensions["C"].width = 78
    settings.row_dimensions[1].height = 24
    settings.freeze_panes = "A5"
    settings.sheet_view.showGridLines = False

    group_validation = DataValidation(type="list", formula1="=Groups!$A$2:$A$16", allow_blank=False)
    group_validation.errorStyle = "warning"
    group_validation.add("B5")
    group_validation.add("B9")
    settings.add_data_validation(group_validation)
    name_validation = DataValidation(type="list", formula1="=Students!$B$2:$B$16", allow_blank=False)
    name_validation.errorStyle = "warning"
    name_validation.add("B6")
    settings.add_data_validation(name_validation)
    id_validation = DataValidation(type="list", formula1="=Students!$A$2:$A$16", allow_blank=False)
    id_validation.errorStyle = "warning"
    id_validation.add("B7")
    settings.add_data_validation(id_validation)
    gender_validation = DataValidation(type="list", formula1='"F,M"', allow_blank=False)
    gender_validation.add("B8")
    settings.add_data_validation(gender_validation)
    prepare_print(settings, "Settings")
    return settings


def student_table_rows(student_rows):
    headers = cfg.COLUMNS["Students"]
    rows = []
    for row in student_rows:
        rows.append(tuple(row[name] for name in headers))
    return headers, rows


def write_workbook(tables, data, results):
    wb = Workbook()
    wb.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True)
    wb.properties.title = "University Database — Practical Work 7–10"
    wb.properties.creator = cfg.STUDENT_NAME
    wb.properties.subject = "Sorting, filtering, SQL and JOIN"
    write_start_and_settings(wb, data)

    data_order = [
        "Students",
        "Groups",
        "Teachers",
        "Departments",
        "Courses",
        "Classrooms",
        "Schedule",
        "Grades",
    ]
    for name in data_order:
        write_data_sheet(wb, name, tables[name], cfg.COLUMNS[name], NAVY)

    one_group, by_id, by_name, two, by_last, by_group = expected_filters(data)
    headers, _ = student_table_rows(data["students"])
    selected = next(
        (row for row in data["groups"] if row["group_id"] == cfg.SELECTED_GROUP_ID), None
    )
    group_note = (
        f"group_id = {cfg.SELECTED_GROUP_ID}"
        if selected is None
        else (
            f"group_id = {selected['group_id']} ({selected['group_name']}, "
            f"{selected['specialty']}, year {selected['year_of_study']})"
        )
    )
    write_result_sheet(
        wb,
        "07_Sort_Last_Name",
        "Saved result. Students sorted A to Z by last_name. Change it with the last_name filter arrow on the Students sheet, or change the data and run build.py.",
        headers,
        [tuple(row[name] for name in headers) for row in by_last],
        "548235",
    )
    same_order = [row["student_id"] for row in by_group] == [
        row["student_id"] for row in sorted(data["students"], key=lambda row: row["student_id"])
    ]
    group_sort_note = (
        "Saved result. Students sorted by group_id. In the current data this order matches student_id order, because student 1001 is in group 1, student 1002 is in group 2, and so on."
        if same_order
        else "Saved result. Students sorted by group_id, then by last name."
    )
    write_result_sheet(
        wb,
        "07_Sort_Group",
        group_sort_note,
        headers,
        [tuple(row[name] for name in headers) for row in by_group],
        "548235",
    )
    write_result_sheet(
        wb,
        "07_Filter_One_Group",
        f"Saved result. Filter: {group_note}. To choose another group, use the group_id arrow on Students, or change Selected group_id in adjust_here.py and rebuild.",
        headers,
        [tuple(row[name] for name in headers) for row in one_group],
        "548235",
    )

    search = wb.create_sheet("07_Search")
    search.sheet_properties.tabColor = "548235"
    search["A1"] = "07 Search"
    search["A1"].font = TITLE_FONT
    search["A2"] = (
        f"Saved result of two searches. By student_id = {cfg.SEARCH_STUDENT_ID}, "
        f"and by last name = {cfg.SEARCH_LAST_NAME}. "
        "The SQL search is not case-sensitive. Use the filter arrows on Students to try another value."
    )
    search["A2"].font = NOTE_FONT
    search["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    search.merge_cells("A1:H1")
    search.merge_cells("A2:H2")
    search.row_dimensions[2].height = 32
    search["A3"] = f"Search by student_id = {cfg.SEARCH_STUDENT_ID}"
    search["A3"].font = LABEL_FONT
    paint_header(search, 4, headers)
    write_plain_rows(search, 5, headers, by_id)
    start = 7 + max(len(by_id), 1)
    search.cell(start, 1, f"Search by last name = {cfg.SEARCH_LAST_NAME}").font = LABEL_FONT
    paint_header(search, start + 1, headers)
    write_plain_rows(search, start + 2, headers, by_name)
    fit_columns(search, max_width=42)
    prepare_print(search, "07_Search")

    write_result_sheet(
        wb,
        "07_Two_Conditions",
        f"Saved result. Condition 1: gender = {cfg.FILTER_GENDER}. Condition 2: group_id <= {cfg.FILTER_MAX_GROUP_ID}. Both must be true. Change FILTER_GENDER and FILTER_MAX_GROUP_ID in adjust_here.py, or use both filter arrows on Students.",
        headers,
        [tuple(row[name] for name in headers) for row in sorted(two, key=lambda row: (row["group_id"], row["last_name"].casefold()))],
        "548235",
    )

    def sheet_from_query(title, key, note, color):
        headers_q, rows, _item = results[key]
        write_result_sheet(wb, title, note, list(headers_q), rows, color)

    sheet_from_query(
        "10_Students_Groups",
        "10_students_groups",
        "Saved JOIN. Students.group_id = Groups.group_id. Compare group_id on the Students sheet with group_name here.",
        "2F5496",
    )
    sheet_from_query(
        "10_Students_Grades",
        "10_students_grades",
        "Saved JOIN. Grades.student_id = Students.student_id. course_id is still the course number; the next sheet replaces it with the subject name.",
        "2F5496",
    )
    sheet_from_query(
        "10_Subject_Grade",
        "10_subject_grade",
        "Saved JOIN. Students to Grades on student_id, then Grades to Courses on course_id. Courses is the subjects table.",
        "2F5496",
    )
    sheet_from_query(
        "10_Inner_Join",
        "10_inner",
        "INNER JOIN keeps a department only when it has a matching course.",
        "2F5496",
    )
    sheet_from_query(
        "10_Left_Join",
        "10_left",
        "LEFT JOIN keeps every department. NULL means that department has no course.",
        "2F5496",
    )
    sheet_from_query(
        "10_Compare_Join",
        "10_compare",
        "The same student in the original Students table and after INNER JOIN Groups. group_info changes from the id to the group name.",
        "2F5496",
    )

    student_headers = cfg.COLUMNS["Students"]
    write_live_sheet(
        wb,
        "Live_Sort_Last_Name",
        "Updates when the Students sheet changes. Requires Excel 365 or Google Sheets. Saved copy: 07_Sort_Last_Name.",
        student_headers,
        '=SORT(FILTER(Students!A2:H200,Students!A2:A200<>""),2,TRUE)',
    )
    write_live_sheet(
        wb,
        "Live_Sort_Group",
        "Sorts by column H (group_id). Requires Excel 365 or Google Sheets. Saved copy: 07_Sort_Group.",
        student_headers,
        '=SORT(FILTER(Students!A2:H200,Students!A2:A200<>""),8,TRUE)',
    )
    write_live_sheet(
        wb,
        "Live_One_Group",
        "Reads Settings!B5 (selected group_id). Change the yellow cell, then this list updates. Requires Excel 365 or Google Sheets.",
        student_headers,
        '=FILTER(Students!A2:H200,Students!H2:H200=Settings!B5,"No students in this group")',
    )
    write_live_sheet(
        wb,
        "Live_Search_ID",
        "Reads Settings!B7 (student id).",
        student_headers,
        '=FILTER(Students!A2:H200,Students!A2:A200=Settings!B7,"No student with this id")',
    )
    write_live_sheet(
        wb,
        "Live_Search_Name",
        "Reads Settings!B6 (last name). This formula is case-sensitive. The SQL search is not.",
        student_headers,
        '=FILTER(Students!A2:H200,Students!B2:B200=Settings!B6,"No student with this last name")',
    )
    write_live_sheet(
        wb,
        "Live_Two_Conditions",
        "Reads Settings!B8 (gender) and Settings!B9 (maximum group_id). Both conditions must be true.",
        student_headers,
        '=FILTER(Students!A2:H200,(Students!E2:E200=Settings!B8)*(Students!H2:H200<=Settings!B9),"No students match both conditions")',
    )
    wb.save(OUT_XLSX)


def write_plain_rows(ws, start_row, headers, student_rows):
    if not student_rows:
        cell = ws.cell(start_row, 1, "No student found.")
        cell.font = Font(name="Calibri", italic=True, color=RED, size=12)
        return
    for offset, row in enumerate(student_rows):
        for col_index, name in enumerate(headers, start=1):
            cell = ws.cell(start_row + offset, col_index, excel_value(name, row[name]))
            cell.font = BODY_FONT
            cell.border = THIN
            cell.alignment = LEFT_ALIGN
            apply_number_format(cell, name)
            if offset % 2 == 1:
                cell.fill = ALT


def wrap_pixels(text, font, max_width):
    lines = []
    for raw in text.splitlines() or [""]:
        if raw == "":
            lines.append("")
            continue
        current = ""
        for word in raw.split(" "):
            trial = word if current == "" else current + " " + word
            if font.getlength(trial) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def render_figure(path, title, note, headers, rows, sql=None):
    pad = 18
    row_h = 28
    header_h = 32
    shown = [[("NULL" if value is None else str(value)) for value in row] for row in rows]
    col_widths = []
    for index, header in enumerate(headers):
        width = FONT_BOLD.getlength(header)
        for row in shown:
            width = max(width, FONT.getlength(row[index]))
        col_widths.append(int(min(max(width + 18, 64), 390)))
    table_w = sum(col_widths) + 2
    min_w = 760
    content_w = max(table_w, min_w)
    note_lines = wrap_pixels(note, FONT_SMALL, content_w - 8)
    sql_lines = []
    if sql:
        sql_lines = wrap_pixels(sql, FONT_MONO, content_w - 16)
    title_h = 34
    note_h = 8 + 18 * max(len(note_lines), 1)
    sql_h = 0 if not sql_lines else 16 + 18 * len(sql_lines) + 12
    table_h = header_h + max(len(shown), 1) * row_h
    footer_h = 28
    width = content_w + pad * 2
    height = pad + title_h + note_h + sql_h + 10 + table_h + footer_h + pad
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 8), fill=NAVY_RGB)
    y = pad
    draw.text((pad, y), title, font=FONT_TITLE, fill=NAVY_RGB)
    y += title_h
    for line in note_lines:
        draw.text((pad, y), line, font=FONT_SMALL, fill=(80, 80, 80))
        y += 18
    y += 8
    if sql_lines:
        box_h = 12 + 18 * len(sql_lines)
        draw.rounded_rectangle((pad, y, pad + content_w, y + box_h), radius=6, fill=(244, 246, 248), outline=(210, 216, 224))
        text_y = y + 6
        for line in sql_lines:
            draw.text((pad + 8, text_y), line, font=FONT_MONO, fill=(20, 20, 20))
            text_y += 18
        y += box_h + 12
    x = pad
    draw.rectangle((x, y, x + table_w, y + header_h), fill=NAVY_RGB)
    cursor_x = x
    for index, header in enumerate(headers):
        draw.text((cursor_x + 8, y + 7), header, font=FONT_BOLD, fill="white")
        cursor_x += col_widths[index]
    y += header_h
    if not shown:
        draw.rectangle((x, y, x + table_w, y + row_h), outline=(220, 224, 230))
        draw.text((x + 8, y + 5), "No rows returned", font=FONT_ITALIC, fill=(140, 140, 140))
        y += row_h
    for row_index, row in enumerate(shown):
        bg = (243, 247, 251) if row_index % 2 else (255, 255, 255)
        draw.rectangle((x, y, x + table_w, y + row_h), fill=bg, outline=(220, 224, 230))
        cursor_x = x
        for col_index, value in enumerate(row):
            if value == "NULL":
                draw.text((cursor_x + 8, y + 5), "NULL", font=FONT_ITALIC, fill=(150, 150, 150))
            else:
                draw.text((cursor_x + 8, y + 5), value, font=FONT, fill=(20, 20, 20))
            cursor_x += col_widths[col_index]
        y += row_h
    noun = "row" if len(rows) == 1 else "rows"
    draw.text((pad, y + 8), f"{len(rows)} {noun}", font=FONT_SMALL, fill=(90, 90, 90))
    image.save(path, "PNG")


def make_screenshots(data, results):
    OUT_SHOTS.mkdir(parents=True, exist_ok=True)
    headers = cfg.COLUMNS["Students"]
    one_group, by_id, by_name, two, by_last, by_group = expected_filters(data)

    def student_matrix(rows):
        return [tuple(row[name] for name in headers) for row in rows]

    figures = []

    def add(filename, title, note, matrix_headers, matrix_rows, sql=None):
        path = OUT_SHOTS / filename
        render_figure(path, title, note, matrix_headers, matrix_rows, sql)
        figures.append({"path": path, "title": title, "note": note})

    add(
        "01_sort_last_name.png",
        "Topic 7. Students sorted by last name",
        "Excel sheet 07_Sort_Last_Name. All students stay in the list; only the order changes.",
        headers,
        student_matrix(by_last),
    )
    add(
        "02_sort_group.png",
        "Topic 7. Students sorted by group",
        "Excel sheet 07_Sort_Group. Sorted by group_id ascending.",
        headers,
        student_matrix(by_group),
    )
    add(
        "03_filter_one_group.png",
        "Topic 7. One selected group",
        f"Excel sheet 07_Filter_One_Group. Condition: group_id = {cfg.SELECTED_GROUP_ID}.",
        headers,
        student_matrix(one_group),
    )
    add(
        "04_search_id.png",
        "Topic 7. Search by student id",
        f"Excel sheet 07_Search. student_id = {cfg.SEARCH_STUDENT_ID}.",
        headers,
        student_matrix(by_id),
    )
    add(
        "05_search_name.png",
        "Topic 7. Search by last name",
        f"Excel sheet 07_Search. last_name = {cfg.SEARCH_LAST_NAME}.",
        headers,
        student_matrix(by_name),
    )
    add(
        "06_two_conditions.png",
        "Topic 7. Two conditions",
        f"Excel sheet 07_Two_Conditions. gender = {cfg.FILTER_GENDER} AND group_id <= {cfg.FILTER_MAX_GROUP_ID}.",
        headers,
        student_matrix(sorted(two, key=lambda row: (row["group_id"], row["last_name"].casefold()))),
    )
    shot_names = {
        "08_all_students": "07_sql_all_students.png",
        "08_student_names": "08_sql_student_names.png",
        "08_groups": "09_sql_groups.png",
        "08_courses": "10_sql_courses.png",
        "09_where": "11_sql_where_group.png",
        "09_order": "12_sql_order_by.png",
        "09_count": "13_sql_count.png",
        "09_group": "14_sql_group_by.png",
        "09_max": "15_sql_max.png",
        "09_min": "16_sql_min.png",
        "09_avg": "17_sql_avg.png",
        "10_students_groups": "18_sql_join_groups.png",
        "10_students_grades": "19_sql_join_grades.png",
        "10_subject_grade": "20_sql_join_subject.png",
        "10_inner": "21_sql_inner_join.png",
        "10_left": "22_sql_left_join.png",
        "10_compare": "23_sql_compare_join.png",
    }
    for key, filename in shot_names.items():
        q_headers, q_rows, item = results[key]
        add(
            filename,
            f"{item['part']}. {item['title']}",
            item["note"] or "Executed in SQLite.",
            q_headers,
            q_rows,
            item["sql"],
        )
    return figures


def names_list(rows):
    if not rows:
        return "no students"
    return ", ".join(person_name(row) for row in rows)


def grade_people(data, target):
    found = []
    for grade in data["grades"]:
        if grade["grade_value"] == target:
            student = next(row for row in data["students"] if row["student_id"] == grade["student_id"])
            course = next(row for row in data["courses"] if row["course_id"] == grade["course_id"])
            found.append(f"{person_name(student)} in {course['course_name']} ({grade['grade_date']})")
    return "; ".join(found)


def build_story(data, results, figures):
    students = data["students"]
    grades = data["grades"]
    one_group, by_id, by_name, two, by_last, by_group = expected_filters(data)
    values = [row["grade_value"] for row in grades]
    maximum = max(values)
    minimum = min(values)
    average = sum(values) / len(values)
    counts = Counter(row["group_id"] for row in students)
    count_text = (
        "every group has exactly 1 student"
        if set(counts.values()) == {1}
        else "the group counts are " + ", ".join(f"group {gid}: {count}" for gid, count in sorted(counts.items()))
    )
    same_order = [row["student_id"] for row in by_group] == sorted(row["student_id"] for row in students)
    selected = next((row for row in data["groups"] if row["group_id"] == cfg.SELECTED_GROUP_ID), None)
    if selected:
        selected_text = (
            f"group {selected['group_id']} ({selected['group_name']}, "
            f"year {selected['year_of_study']}, {selected['specialty']})"
        )
    else:
        selected_text = f"group_id {cfg.SELECTED_GROUP_ID}, which is not in the Groups table"
    years = set()
    for row in two:
        group = next(item for item in data["groups"] if item["group_id"] == row["group_id"])
        years.add(group["year_of_study"])
    if len(years) == 1 and two:
        year_text = f" All of these students are in year {next(iter(years))}."
    else:
        year_text = ""
    empty_departments = []
    course_departments = {row["department_id"] for row in data["courses"]}
    for row in data["departments"]:
        if row["department_id"] not in course_departments:
            empty_departments.append(row["department_name"])
    multi = []
    department_course_counts = Counter(row["department_id"] for row in data["courses"])
    for department_id, count in sorted(department_course_counts.items()):
        if count > 1:
            name = next(row["department_name"] for row in data["departments"] if row["department_id"] == department_id)
            multi.append(f"{name} ({count} courses)")
    inner_n = len(results["10_inner"][1])
    left_n = len(results["10_left"][1])
    group_line = cfg.STUDENT_GROUP.strip() or "(write your group in adjust_here.py or on the Excel Settings sheet)"
    blocks = []
    add = blocks.append
    add(("h1", "Practical Work №7–10"))
    add(("p", "Data Sorting, Filtering, SQL Queries and Joining Tables"))
    add(("p", f"Student: {cfg.STUDENT_NAME}"))
    add(("p", f"Group: {group_line}"))
    add(("p", f"Date: {cfg.REPORT_DATE}"))
    add(("p", "Dataset: university educational process from Practice Work 2"))
    add(("h2", "1. What was done"))
    add((
        "p",
        "I continued the university database from Practice Work 2. It stores students, groups, teachers, departments, courses, classrooms, the class schedule and grades. "
        f"There are {len(data['groups'])} groups, {len(students)} students, {len(data['teachers'])} teachers, {len(data['departments'])} departments, {len(data['courses'])} courses, {len(data['classrooms'])} classrooms, {len(data['schedule'])} schedule rows and {len(grades)} grades.",
    ))
    add((
        "p",
        "The task sheet uses the names Subjects and grade. In my database the subject table is called Courses, and the mark is stored in grade_value on a scale of 0–100. The queries use those names.",
    ))
    add((
        "p",
        f"The saved examples use {selected_text}, a last-name search for {cfg.SEARCH_LAST_NAME}, a search for student id {cfg.SEARCH_STUDENT_ID}, and a two-condition filter gender = {cfg.FILTER_GENDER} and group_id <= {cfg.FILTER_MAX_GROUP_ID}.",
    ))
    add((
        "p",
        "To change those examples and rebuild the workbook, the SQL file, the screenshots and this report together, edit the ADJUST block at the top of adjust_here.py and run python3 build.py. "
        "To change a filter only in the spreadsheet, use the header arrows on the Students sheet, or the yellow cells on Settings together with the orange Live sheets (Excel 365 or Google Sheets). "
        "To change the SQL only, edit the INSERT into settings in sql/practical_work_7_10.sql and run the section “Queries that read the settings table”.",
    ))
    add(("h2", "2. Part 1 — Sorting, filtering and searching"))
    add((
        "p",
        f"I sorted the Students sheet by last name from A to Z. The first row is {by_last[0]['last_name']} {by_last[0]['first_name']} and the last row is {by_last[-1]['last_name']} {by_last[-1]['first_name']}. All {len(students)} students remain visible.",
    ))
    add(("figure", figures[0]))
    if same_order:
        add((
            "p",
            "I also sorted the same sheet by group_id. The order matches the original student_id order, because the Practice Work 2 list places student 1001 in group 1, student 1002 in group 2, and continues in the same way through the last student. The sort is still a group sort: the key is group_id.",
        ))
    else:
        add(("p", "I sorted the same sheet by group_id and then by last name. This order is saved on sheet 07_Sort_Group."))
    add(("figure", figures[1]))
    add((
        "p",
        f"I filtered the students to one group, {selected_text}. The filter returns {names_list(one_group)}.",
    ))
    add(("figure", figures[2]))
    id_text = names_list(by_id) if by_id else "no student"
    name_text = names_list(by_name) if by_name else "no student"
    add((
        "p",
        f"I searched by student id {cfg.SEARCH_STUDENT_ID} and found {id_text}. I searched by last name {cfg.SEARCH_LAST_NAME} and found {name_text}. In SQL the last-name search uses COLLATE NOCASE, so the capital letters do not matter.",
    ))
    add(("figure", figures[3]))
    add(("figure", figures[4]))
    add((
        "p",
        f"I then filtered with two conditions at once: gender = {cfg.FILTER_GENDER}, and group_id <= {cfg.FILTER_MAX_GROUP_ID}. A row must satisfy both. The result is {names_list(sorted(two, key=lambda row: row['group_id']))}.{year_text}",
    ))
    add(("figure", figures[5]))
    add(("h2", "3. Part 2 — Introduction to SQL"))
    add((
        "p",
        "I loaded the eight tables into SQLite (db/university.sqlite) and ran the queries in sql/practical_work_7_10.sql. The first queries only display data. SELECT * FROM Students returns every column. The second query returns student_id, first_name and last_name. SELECT * FROM Groups returns the groups. The subject names come from Courses, because that is the subject table in this database.",
    ))
    for figure in figures[6:10]:
        add(("figure", figure))
    add(("h2", "4. Part 3 — WHERE, ORDER BY, GROUP BY and aggregates"))
    add((
        "p",
        f"WHERE group_id = {cfg.SELECTED_GROUP_ID} returns {names_list(one_group)}. ORDER BY last_name ASC returns all {len(students)} students in alphabetical order. COUNT(*) returns {len(students)}. GROUP BY group_id returns one count per group; in the current data, {count_text}.",
    ))
    add((
        "p",
        f"MAX(grade_value) returns {maximum} ({grade_people(data, maximum)}). MIN(grade_value) returns {minimum} ({grade_people(data, minimum)}). AVG(grade_value) returns {average:.2f}. The exact SQLite value is {results['09_avg'][1][0][0]}.",
    ))
    for figure in figures[10:17]:
        add(("figure", figure))
    add(("h2", "5. Part 4 — Joining tables"))
    add((
        "p",
        "The tables stay separate. Students stores group_id, not the group name. Groups stores the name once. Grades stores student_id and course_id, not the student’s name and not the subject name. JOIN matches the shared id and shows the related columns on one row.",
    ))
    add((
        "table",
        ["Result", "Column in the first table", "Column in the second table"],
        [
            ["Student name with group name", "Students.group_id", "Groups.group_id"],
            ["Student with grade", "Grades.student_id", "Students.student_id"],
            ["Subject name with grade", "Grades.course_id", "Courses.course_id"],
            ["Department with its courses", "Courses.department_id", "Departments.department_id"],
        ],
    ))
    compare_headers, compare_rows, _item = results["10_compare"]
    if compare_rows:
        original = compare_rows[0]
        joined = compare_rows[1] if len(compare_rows) > 1 else None
        compare_sentence = (
            f"For student {original[1]}, the Students table shows group info {original[4]}. "
        )
        if joined:
            compare_sentence += (
                f"After INNER JOIN Groups, the same student shows group info {joined[4]}. "
                "The original tables are unchanged. The query only reads them together."
            )
    else:
        compare_sentence = "The comparison query returned no student for the selected id."
    add(("p", compare_sentence))
    for figure in figures[17:20]:
        add(("figure", figure))
    add(("figure", figures[22]))
    if empty_departments:
        empty_text = ", ".join(empty_departments)
        difference = (
            f"INNER JOIN returns {inner_n} rows, one for each course. "
            f"LEFT JOIN returns {left_n} rows. The extra rows are {empty_text}: those departments have no course, so course_name is NULL."
        )
    else:
        difference = (
            f"INNER JOIN and LEFT JOIN both return {inner_n} rows, because every department currently has at least one course. "
            "If a department had no course, INNER JOIN would hide it and LEFT JOIN would keep it with NULL in course_name."
        )
    multi_text = (
        " " + " and ".join(multi) + " appear on more than one row because each course is its own row."
        if multi
        else ""
    )
    add(("p", difference + multi_text))
    add(("figure", figures[20]))
    add(("figure", figures[21]))
    add(("h2", "6. Individual assignment"))
    add(("h3", "1. What is the difference between sorting and filtering?"))
    add((
        "p",
        f"Sorting changes the order of the rows and keeps every row. Filtering hides the rows that do not match a condition. Searching finds a row by a specific value, such as a student id or a last name. In this work, sorting Students by last name still shows all {len(students)} students, with {by_last[0]['last_name']} first. Filtering to {selected_text} shows {names_list(one_group)} and hides the other students.",
    ))
    add(("h3", "2. What is SQL used for?"))
    add((
        "p",
        "SQL is the language used to work with a relational database. It creates tables, inserts the rows, and then retrieves or updates them. I used it to display the university tables, to filter and sort students, to summarise grades with COUNT, MAX, MIN and AVG, and to bring related tables together with JOIN.",
    ))
    add(("h3", "3. What is the difference between WHERE and ORDER BY?"))
    add((
        "p",
        f"WHERE decides which rows are included. ORDER BY decides the order of the rows that were included. WHERE group_id = {cfg.SELECTED_GROUP_ID} returns only that group. ORDER BY last_name ASC returns every student, arranged alphabetically. WHERE does the filtering. ORDER BY does the sorting. One query can use both.",
    ))
    add(("h3", "4. Why do we use GROUP BY and aggregate functions?"))
    add((
        "p",
        f"An aggregate function turns many rows into one value. COUNT counts rows, MAX and MIN find the largest and smallest values, and AVG calculates the mean. GROUP BY divides the rows into groups before that calculation, so the function returns one result per group. COUNT(*) on Students returns {len(students)}. With GROUP BY group_id, the same function returns a separate count for each group ({count_text}). On Grades, MAX is {maximum}, MIN is {minimum} and the average is {average:.2f}.",
    ))
    add(("h3", "5. What is the purpose of JOIN?"))
    add((
        "p",
        "JOIN combines columns from related tables into one result. The database stores each fact once: the group name lives in Groups, and Students stores only group_id. Matching Students.group_id to Groups.group_id shows the student’s name and the group name together without copying the group name into every student row.",
    ))
    add(("h3", "6. What is the difference between INNER JOIN and LEFT JOIN?"))
    add((
        "p",
        "INNER JOIN returns only rows that have a match in both tables. LEFT JOIN returns every row from the left table, and fills the right-hand columns with NULL when there is no match. "
        + difference,
    ))
    add(("h2", "7. Conclusion"))
    add((
        "p",
        "The same university tables can be sorted and filtered in the spreadsheet and queried in SQLite. WHERE and the Excel filter choose rows, ORDER BY and the Excel sort choose the order, GROUP BY with aggregate functions summarises rows, and JOIN reads related tables together through the shared ids.",
    ))
    add((
        "p",
        "Files: University_Database.xlsx, db/university.sqlite, sql/practical_work_7_10.sql, sql/query_results.txt, the screenshots folder, and this report.",
    ))
    return blocks


def render_docx(blocks):
    document = Document()
    document.core_properties.author = cfg.STUDENT_NAME
    document.core_properties.title = "Practical Work 7–10"
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(12)
    figure_no = 0
    for kind, *payload in blocks:
        if kind == "h1":
            document.add_heading(payload[0], level=0)
        elif kind == "h2":
            document.add_heading(payload[0], level=1)
        elif kind == "h3":
            document.add_heading(payload[0], level=2)
        elif kind == "p":
            document.add_paragraph(payload[0])
        elif kind == "table":
            headers, rows = payload
            table = document.add_table(rows=1, cols=len(headers))
            table.style = "Table Grid"
            for index, header in enumerate(headers):
                cell = table.rows[0].cells[index]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
            for row in rows:
                cells = table.add_row().cells
                for index, value in enumerate(row):
                    cells[index].text = str(value)
            document.add_paragraph("")
        elif kind == "figure":
            figure = payload[0]
            figure_no += 1
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            with Image.open(figure["path"]) as image:
                display = min(6.5, max(3.4, image.width / 150))
            paragraph.add_run().add_picture(str(figure["path"]), width=Inches(display))
            caption = document.add_paragraph(f"Figure {figure_no}. {figure['title']}.")
            caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in caption.runs:
                run.italic = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUT_DOCX)


def render_html(blocks):
    figure_no = 0
    parts = [
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"/>",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>",
        f"<title>Practical Work 7–10 — {escape(cfg.STUDENT_NAME)}</title>",
        "<style>",
        "body{font-family:Georgia,serif;max-width:980px;margin:0 auto;padding:24px;line-height:1.55;color:#1a1a1a;background:#fff}",
        "h1,h2,h3{font-family:Calibri,'Segoe UI',Arial,sans-serif;color:#1F4E79}",
        "table{width:100%;border-collapse:collapse;font-family:Calibri,Arial,sans-serif;font-size:.95rem;margin:1rem 0}",
        "th,td{border:1px solid #999;padding:8px;vertical-align:top} th{background:#1F4E79;color:#fff}",
        "img{max-width:100%;height:auto;border:1px solid #ddd}",
        "figure{margin:1.2rem 0} figcaption{text-align:center;color:#555;font-style:italic;font-size:.92rem;margin-top:.4rem}",
        ".toolbar{position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid #ddd;margin-bottom:1rem;display:flex;gap:8px;flex-wrap:wrap;font-family:Calibri,Arial,sans-serif}",
        ".toolbar a{background:#1F4E79;color:#fff;padding:8px 12px;border-radius:6px;text-decoration:none}",
        "@media print{.toolbar{display:none}}",
        "</style></head><body>",
        "<div class=\"toolbar\">",
        "<a href=\"Practical_Work_7-10.docx\" download>Download Word</a>",
        "<a href=\"Practical_Work_7-10.pdf\" download>Download PDF</a>",
        "<a href=\"../University_Database.xlsx\" download>Download Excel</a>",
        "<a href=\"../sql/practical_work_7_10.sql\" download>Download SQL</a>",
        "</div>",
    ]
    for kind, *payload in blocks:
        if kind == "h1":
            parts.append(f"<h1>{escape(payload[0])}</h1>")
        elif kind == "h2":
            parts.append(f"<h2>{escape(payload[0])}</h2>")
        elif kind == "h3":
            parts.append(f"<h3>{escape(payload[0])}</h3>")
        elif kind == "p":
            parts.append(f"<p>{escape(payload[0])}</p>")
        elif kind == "table":
            headers, rows = payload
            parts.append("<table><tr>" + "".join(f"<th>{escape(header)}</th>" for header in headers) + "</tr>")
            for row in rows:
                parts.append("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>")
            parts.append("</table>")
        elif kind == "figure":
            figure = payload[0]
            figure_no += 1
            relative = Path("..") / "screenshots" / figure["path"].name
            parts.append("<figure>")
            parts.append(f"<img src=\"{escape(str(relative))}\" alt=\"{escape(figure['title'])}\"/>")
            parts.append(f"<figcaption>Figure {figure_no}. {escape(figure['title'])}.</figcaption>")
            parts.append("</figure>")
    parts.append("</body></html>")
    OUT_HTML.write_text("".join(parts), encoding="utf-8")


def write_pdf():
    import shutil
    import subprocess

    if OUT_PDF.exists():
        OUT_PDF.unlink()
    soffice = shutil.which("soffice")
    if soffice:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--norestore",
                "--convert-to",
                "pdf",
                "--outdir",
                str(OUT_PDF.parent),
                str(OUT_DOCX),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        produced = OUT_PDF.parent / (OUT_DOCX.stem + ".pdf")
        if produced.exists() and produced != OUT_PDF:
            produced.replace(OUT_PDF)
        if OUT_PDF.exists() and OUT_PDF.stat().st_size > 0:
            return True
    command = [
        "timeout",
        "40",
        "google-chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--user-data-dir=/tmp/chrome-pw710-pdf",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUT_PDF}",
        OUT_HTML.resolve().as_uri(),
    ]
    subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return OUT_PDF.exists() and OUT_PDF.stat().st_size > 0


def spot_check_original_dataset(tables):
    """Confirm the generated rows still match Practice Work 2 before any edit."""
    students = tables["Students"]
    expected_first = (
        1001,
        "Aliyeva",
        "Aruzhan",
        "2004-01-05",
        "F",
        "+7-707-2000000",
        "aruzhan.aliyeva@student.university.example",
        1,
    )
    if students[0] != expected_first:
        return False
    if students[11][1:4] != ("Abilov", "Sanzhar", "2006-12-16"):
        return False
    if students[14][3] != "2006-03-19":
        return False
    teachers = tables["Teachers"]
    if teachers[0] != (
        1,
        "Ayan",
        "Saparov",
        "MSc",
        "+7-701-1000001",
        "ayan.saparov1@university.example",
        1,
    ):
        return False
    if teachers[9][5] != "amina.zhaksylyk10@university.example":
        return False
    courses = tables["Courses"]
    if courses[6] != (7, "Web Development", 4, 2, 2):
        return False
    if courses[11] != (12, "Project Management", 3, 4, 12):
        return False
    grades = tables["Grades"]
    if grades[0] != (1, 1001, 1, 67, "2026-05-01"):
        return False
    if grades[14] != (15, 1015, 15, 83, "2026-05-15"):
        return False
    schedule = tables["Schedule"]
    if schedule[0][5:] != ("Monday", "08:00:00", "09:50:00"):
        return False
    if schedule[5][5:] != ("Monday", "13:00:00", "14:50:00"):
        return False
    if schedule[14][5:] != ("Friday", "10:00:00", "11:50:00"):
        return False
    groups = tables["Groups"]
    if groups[0] != (1, "IT-21", 1, "Software Engineering"):
        return False
    if groups[14] != (15, "IT-35", 3, "Computer Science"):
        return False
    classrooms = tables["Classrooms"]
    if classrooms[0] != (1, "101", "Building 1", 25):
        return False
    if classrooms[3] != (4, "104", "Building 4", 20):
        return False
    if classrooms[14] != (15, "115", "Building 5", 35):
        return False
    return True


def main():
    validate_settings()
    tables = cfg.build_tables()
    for name, rows in tables.items():
        if not rows:
            fail(f"{name} is empty")
        width = len(cfg.COLUMNS[name])
        for row in rows:
            if len(row) != width:
                fail(f"{name} has a row with the wrong number of columns: {row}")
    original = spot_check_original_dataset(tables)
    data = check_tables(tables)
    queries = build_queries()
    topic7 = topic7_queries()
    extras = extra_queries()
    sql_text = render_sql_file(queries, topic7, extras, tables)
    # Setup is everything before the first query section banner.
    marker = "-- Part 2, Part 3 and Part 4"
    setup_sql = sql_text.split(marker)[0]
    connection = load_database(setup_sql)
    try:
        results = check_queries(connection, data, queries, topic7, extras)
    finally:
        connection.close()
    # The full script must also load cleanly, including every query.
    probe = sqlite3.connect(":memory:")
    try:
        probe.execute("PRAGMA foreign_keys = ON;")
        probe.executescript(sql_text)
    finally:
        probe.close()
    write_results_log(results, queries + topic7 + extras)
    write_workbook(tables, data, results)
    figures = make_screenshots(data, results)
    blocks = build_story(data, results, figures)
    render_docx(blocks)
    render_html(blocks)
    pdf_ok = write_pdf()
    print(f"Workbook: {OUT_XLSX}")
    print(f"Database: {OUT_DB}")
    print(f"SQL:      {OUT_SQL}")
    print(f"Results:  {OUT_RESULTS}")
    print(f"Report:   {OUT_DOCX}")
    print(f"HTML:     {OUT_HTML}")
    print(f"PDF:      {OUT_PDF if pdf_ok else 'not created'}")
    print(f"Shots:    {len(figures)}")
    print(f"Original Practice Work 2 rows: {'yes' if original else 'edited'}")
    if not original:
        print("Data no longer matches the untouched Practice Work 2 rows. That is expected after you edit adjust_here.py.")
    if not pdf_ok:
        print("PDF was not created. The Word report and the HTML report are still ready.")


if __name__ == "__main__":
    main()
