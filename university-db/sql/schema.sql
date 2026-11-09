-- University educational-process database.
-- Practice Work 1–2: subject area, constraints, and structured dataset.
--
-- Constraint map
-- 1–8   Primary key on every table
-- 9     A student's date of birth cannot be in the future
-- 10    A student must belong to an existing group
-- 11    A teacher must belong to an existing department
-- 12    A course must belong to an existing department
-- 13    Course credits must be greater than 0
-- 14    Classroom capacity must be greater than 0
-- 15    A grade must be inside the 0–100 scale
-- 16    Class end time must be later than its start time
-- 17    A student's email address is unique
-- 18    A classroom cannot hold two classes at the same time
-- 19    A student cannot have two grades for the same course on the same date
-- 20    Required names and other required text fields cannot be empty
--
-- Teachers are stored as first_name, last_name to match the Practice Work 2
-- dataset table. Students keep last_name, first_name, as in both the entity
-- list and the dataset table.

PRAGMA foreign_keys = ON;

CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY, -- 2
    group_name TEXT NOT NULL CHECK (length(trim(group_name)) > 0), -- 20
    year_of_study INTEGER NOT NULL CHECK (year_of_study > 0),
    specialty TEXT NOT NULL CHECK (length(trim(specialty)) > 0) -- 20
);

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY, -- 4
    department_name TEXT NOT NULL CHECK (length(trim(department_name)) > 0), -- 20
    building TEXT NOT NULL CHECK (length(trim(building)) > 0)
);

CREATE TABLE classrooms (
    classroom_id INTEGER PRIMARY KEY, -- 6
    room_number TEXT NOT NULL CHECK (length(trim(room_number)) > 0),
    building TEXT NOT NULL CHECK (length(trim(building)) > 0),
    capacity INTEGER NOT NULL CHECK (capacity > 0) -- 14
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY, -- 1
    last_name TEXT NOT NULL CHECK (length(trim(last_name)) > 0), -- 20
    first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0), -- 20
    birth_date TEXT NOT NULL, -- 9, enforced by trigger (date('now') is not allowed in CHECK)
    gender TEXT NOT NULL CHECK (length(trim(gender)) > 0),
    phone TEXT NOT NULL CHECK (length(trim(phone)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0), -- 17, 20
    group_id INTEGER NOT NULL, -- 10
    FOREIGN KEY (group_id) REFERENCES groups (group_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY, -- 3
    first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0),
    last_name TEXT NOT NULL CHECK (length(trim(last_name)) > 0),
    academic_degree TEXT NOT NULL CHECK (length(trim(academic_degree)) > 0),
    phone TEXT NOT NULL CHECK (length(trim(phone)) > 0),
    email TEXT NOT NULL CHECK (length(trim(email)) > 0),
    department_id INTEGER NOT NULL, -- 11
    FOREIGN KEY (department_id) REFERENCES departments (department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY, -- 5
    course_name TEXT NOT NULL CHECK (length(trim(course_name)) > 0), -- 20
    credits INTEGER NOT NULL CHECK (credits > 0), -- 13
    semester INTEGER NOT NULL CHECK (semester > 0),
    department_id INTEGER NOT NULL, -- 12
    FOREIGN KEY (department_id) REFERENCES departments (department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE schedule (
    schedule_id INTEGER PRIMARY KEY, -- 7
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
    end_time TEXT NOT NULL CHECK (end_time > start_time), -- 16
    FOREIGN KEY (course_id) REFERENCES courses (course_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (group_id) REFERENCES groups (group_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (classroom_id) REFERENCES classrooms (classroom_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY, -- 8
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade_value INTEGER NOT NULL CHECK (grade_value BETWEEN 0 AND 100), -- 15
    grade_date TEXT NOT NULL,
    -- 19
    UNIQUE (student_id, course_id, grade_date),
    FOREIGN KEY (student_id) REFERENCES students (student_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (course_id) REFERENCES courses (course_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX idx_students_group ON students (group_id);
CREATE INDEX idx_teachers_department ON teachers (department_id);
CREATE INDEX idx_courses_department ON courses (department_id);
CREATE INDEX idx_schedule_course ON schedule (course_id);
CREATE INDEX idx_schedule_teacher ON schedule (teacher_id);
CREATE INDEX idx_schedule_group ON schedule (group_id);
CREATE INDEX idx_schedule_classroom ON schedule (classroom_id, day_of_week);
CREATE INDEX idx_grades_student ON grades (student_id);
CREATE INDEX idx_grades_course ON grades (course_id);

-- 9. A student's date of birth cannot be in the future.
CREATE TRIGGER students_birth_date_not_future_insert
BEFORE INSERT ON students
BEGIN
    SELECT RAISE(ABORT, 'A student''s date of birth cannot be in the future')
    WHERE NEW.birth_date > date('now');
END;

CREATE TRIGGER students_birth_date_not_future_update
BEFORE UPDATE OF birth_date ON students
BEGIN
    SELECT RAISE(ABORT, 'A student''s date of birth cannot be in the future')
    WHERE NEW.birth_date > date('now');
END;

-- 18. Reject a booking that overlaps another class in the same room and day.
-- Back-to-back classes are allowed: a class may start when the previous one ends.
CREATE TRIGGER schedule_no_classroom_overlap_insert
BEFORE INSERT ON schedule
BEGIN
    SELECT RAISE(ABORT, 'A classroom cannot have two classes scheduled at the same time')
    WHERE EXISTS (
        SELECT 1
        FROM schedule
        WHERE classroom_id = NEW.classroom_id
          AND day_of_week = NEW.day_of_week
          AND start_time < NEW.end_time
          AND end_time > NEW.start_time
    );
END;

CREATE TRIGGER schedule_no_classroom_overlap_update
BEFORE UPDATE ON schedule
BEGIN
    SELECT RAISE(ABORT, 'A classroom cannot have two classes scheduled at the same time')
    WHERE EXISTS (
        SELECT 1
        FROM schedule
        WHERE classroom_id = NEW.classroom_id
          AND day_of_week = NEW.day_of_week
          AND schedule_id <> OLD.schedule_id
          AND start_time < NEW.end_time
          AND end_time > NEW.start_time
    );
END;
