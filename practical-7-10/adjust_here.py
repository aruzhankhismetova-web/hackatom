# Practical Work 7–10
# University database from Practice Work 2
#
# Change the values in the ADJUST block, then rebuild every file:
#     python3 build.py
#
# Emails, phones, student dates, groups, the schedule and the grades
# follow the Practice Work 2 records. If you rename a student or a
# teacher, the matching email is rebuilt from the new name.

# ============================================================
# ADJUST THE EXAMPLES HERE
# ============================================================

# Filter "one selected group", and SQL: WHERE group_id = ...
SELECTED_GROUP_ID = 1

# Search by last name, and search by student id.
# They can point at the same student or at two different students.
SEARCH_LAST_NAME = "Aliyeva"
SEARCH_STUDENT_ID = 1001

# Two-condition filter on Students.
# Default: women in groups 1–5 (IT-21 … IT-25, year 1).
FILTER_GENDER = "F"
FILTER_MAX_GROUP_ID = 5

# Extra queries from Practice Work 1 (the SQL file, part "Extra").
GRADE_BELOW = 70
FREE_DAY = "Monday"
FREE_START = "08:00:00"
FREE_END = "09:50:00"
SELECTED_COURSE_ID = 1
SELECTED_TEACHER_ID = 1
SELECTED_SCHEDULE_ID = 1
SELECTED_DEPARTMENT_ID = 1

# Printed on the report and on the Excel Settings sheet.
STUDENT_NAME = "Aruzhan"
STUDENT_GROUP = ""  # write your group, for example "IT-21"
REPORT_DATE = "9 November 2026"

# ============================================================
# PRACTICE WORK 2 DATA
# Edit a name, a course or a grade here, then run build.py again.
# ============================================================

# (last_name, first_name) in student_id order, starting at 1001.
STUDENT_NAMES = [
    ("Aliyeva", "Aruzhan"),
    ("Baimukhan", "Nursultan"),
    ("Suleimenova", "Amina"),
    ("Kairatov", "Dias"),
    ("Zholdas", "Madina"),
    ("Tursyn", "Alikhan"),
    ("Mukhanova", "Dana"),
    ("Yessen", "Islam"),
    ("Beketova", "Aigerim"),
    ("Ospan", "Miras"),
    ("Zhakupova", "Kamila"),
    ("Abilov", "Sanzhar"),
    ("Kaliyeva", "Zarina"),
    ("Amanzhol", "Timur"),
    ("Serik", "Ademi"),
]

# (first_name, last_name, academic_degree) in teacher_id order, 1..15.
# Each teacher belongs to the department with the same id.
TEACHERS_BASE = [
    ("Ayan", "Saparov", "MSc"),
    ("Dana", "Kassymova", "PhD"),
    ("Arman", "Bekov", "MSc"),
    ("Aigerim", "Nurgaliyeva", "PhD"),
    ("Dias", "Omarov", "MSc"),
    ("Madina", "Serikova", "MA"),
    ("Nurlan", "Tulegenov", "PhD"),
    ("Aliya", "Iskakova", "MSc"),
    ("Timur", "Akhmetov", "MSc"),
    ("Amina", "Zhaksylyk", "PhD"),
    ("Miras", "Bekturov", "MBA"),
    ("Kamila", "Rakhimova", "MA"),
    ("Sanzhar", "Yermekov", "MSc"),
    ("Zarina", "Abdullina", "PhD"),
    ("Ruslan", "Kenzhebayev", "MSc"),
]

# (department_name, building)
DEPARTMENTS_BASE = [
    ("Computer Science", "Building 1"),
    ("Information Technology", "Building 2"),
    ("Mathematics", "Building 3"),
    ("Physics", "Building 4"),
    ("Languages", "Building 5"),
    ("Software Engineering", "Building 1"),
    ("Information Systems", "Building 2"),
    ("Cybersecurity", "Building 3"),
    ("Data Science", "Building 4"),
    ("Engineering", "Building 5"),
    ("Economics", "Building 1"),
    ("Management", "Building 2"),
    ("Statistics", "Building 3"),
    ("Artificial Intelligence", "Building 4"),
    ("General Studies", "Building 5"),
]

# (course_name, credits, semester, department_id)
# This table is the "Subjects" table from the task sheet.
COURSES_BASE = [
    ("Database Systems", 5, 1, 1),
    ("Programming Fundamentals", 5, 1, 2),
    ("Discrete Mathematics", 4, 1, 3),
    ("Physics for IT", 3, 1, 4),
    ("Academic English", 3, 1, 5),
    ("Object-Oriented Programming", 5, 2, 6),
    ("Web Development", 4, 2, 2),
    ("Information Systems", 4, 2, 7),
    ("Network Security", 4, 3, 8),
    ("Data Analytics", 4, 3, 9),
    ("Software Testing", 3, 3, 6),
    ("Project Management", 3, 4, 12),
    ("Statistics", 4, 2, 13),
    ("Artificial Intelligence", 5, 4, 14),
    ("Engineering Basics", 3, 1, 10),
]

# One grade per student, course_id 1..15, dates 2026-05-01 .. 2026-05-15.
GRADE_VALUES = [67, 74, 81, 88, 95, 61, 68, 75, 82, 89, 96, 62, 69, 76, 83]

GROUP_SPECIALTIES = [
    (1, 5, "Software Engineering"),
    (6, 10, "Information Systems"),
    (11, 15, "Computer Science"),
]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _group_specialty(group_id):
    for start, end, name in GROUP_SPECIALTIES:
        if start <= group_id <= end:
            return name
    raise ValueError(f"No specialty for group_id {group_id}")


def build_tables():
    """Return the eight university tables as lists of tuples."""
    groups = []
    for i in range(1, 16):
        if i <= 5:
            year = 1
        elif i <= 10:
            year = 2
        else:
            year = 3
        groups.append((i, f"IT-{20 + i}", year, _group_specialty(i)))

    students = []
    for index, (last_name, first_name) in enumerate(STUDENT_NAMES):
        student_id = 1001 + index
        month = (index % 12) + 1
        day = 5 + index
        year = 2004 + (index % 3)
        gender = "F" if index % 2 == 0 else "M"
        phone = f"+7-707-{2000000 + index}"
        email = f"{first_name}.{last_name}@student.university.example".lower()
        students.append(
            (
                student_id,
                last_name,
                first_name,
                f"{year:04d}-{month:02d}-{day:02d}",
                gender,
                phone,
                email,
                index + 1,
            )
        )

    departments = [
        (i + 1, name, building) for i, (name, building) in enumerate(DEPARTMENTS_BASE)
    ]

    teachers = []
    for i, (first_name, last_name, degree) in enumerate(TEACHERS_BASE, start=1):
        phone = f"+7-701-{1000000 + i}"
        email = f"{first_name}.{last_name}{i}@university.example".lower()
        teachers.append((i, first_name, last_name, degree, phone, email, i))

    courses = [
        (i + 1, name, credits, semester, department_id)
        for i, (name, credits, semester, department_id) in enumerate(COURSES_BASE)
    ]

    capacities = [25, 30, 35, 20]
    classrooms = []
    for i in range(1, 16):
        classrooms.append(
            (i, str(100 + i), f"Building {((i - 1) % 5) + 1}", capacities[(i - 1) % 4])
        )

    schedule = []
    for i in range(1, 16):
        start_hour = 8 + ((i - 1) % 6)
        end_hour = start_hour + 1
        schedule.append(
            (
                i,
                i,
                i,
                i,
                i,
                WEEKDAYS[(i - 1) % 5],
                f"{start_hour:02d}:00:00",
                f"{end_hour:02d}:50:00",
            )
        )

    grades = []
    for i, grade_value in enumerate(GRADE_VALUES, start=1):
        grades.append((i, 1000 + i, i, grade_value, f"2026-05-{i:02d}"))

    return {
        "Groups": groups,
        "Departments": departments,
        "Classrooms": classrooms,
        "Teachers": teachers,
        "Courses": courses,
        "Students": students,
        "Schedule": schedule,
        "Grades": grades,
    }


COLUMNS = {
    "Groups": ["group_id", "group_name", "year_of_study", "specialty"],
    "Departments": ["department_id", "department_name", "building"],
    "Classrooms": ["classroom_id", "room_number", "building", "capacity"],
    "Teachers": [
        "teacher_id",
        "first_name",
        "last_name",
        "academic_degree",
        "phone",
        "email",
        "department_id",
    ],
    "Courses": ["course_id", "course_name", "credits", "semester", "department_id"],
    "Students": [
        "student_id",
        "last_name",
        "first_name",
        "birth_date",
        "gender",
        "phone",
        "email",
        "group_id",
    ],
    "Schedule": [
        "schedule_id",
        "course_id",
        "teacher_id",
        "group_id",
        "classroom_id",
        "day_of_week",
        "start_time",
        "end_time",
    ],
    "Grades": ["grade_id", "student_id", "course_id", "grade_value", "grade_date"],
}
