-- Practical Work 7-10
-- Data sorting, filtering, SQL queries and joining tables
-- University database from Practice Work 2
-- Student: Asylai
-- Group: SE1-24
-- Date: 9 November 2026
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

INSERT INTO Groups (group_id, group_name, year_of_study, specialty) VALUES
(1, 'IT-21', 1, 'Software Engineering'),
(2, 'IT-22', 1, 'Software Engineering'),
(3, 'IT-23', 1, 'Software Engineering'),
(4, 'IT-24', 1, 'Software Engineering'),
(5, 'IT-25', 1, 'Software Engineering'),
(6, 'IT-26', 2, 'Information Systems'),
(7, 'IT-27', 2, 'Information Systems'),
(8, 'IT-28', 2, 'Information Systems'),
(9, 'IT-29', 2, 'Information Systems'),
(10, 'IT-30', 2, 'Information Systems'),
(11, 'IT-31', 3, 'Computer Science'),
(12, 'IT-32', 3, 'Computer Science'),
(13, 'IT-33', 3, 'Computer Science'),
(14, 'IT-34', 3, 'Computer Science'),
(15, 'IT-35', 3, 'Computer Science');

INSERT INTO Departments (department_id, department_name, building) VALUES
(1, 'Computer Science', 'Building 1'),
(2, 'Information Technology', 'Building 2'),
(3, 'Mathematics', 'Building 3'),
(4, 'Physics', 'Building 4'),
(5, 'Languages', 'Building 5'),
(6, 'Software Engineering', 'Building 1'),
(7, 'Information Systems', 'Building 2'),
(8, 'Cybersecurity', 'Building 3'),
(9, 'Data Science', 'Building 4'),
(10, 'Engineering', 'Building 5'),
(11, 'Economics', 'Building 1'),
(12, 'Management', 'Building 2'),
(13, 'Statistics', 'Building 3'),
(14, 'Artificial Intelligence', 'Building 4'),
(15, 'General Studies', 'Building 5');

INSERT INTO Classrooms (classroom_id, room_number, building, capacity) VALUES
(1, '101', 'Building 1', 25),
(2, '102', 'Building 2', 30),
(3, '103', 'Building 3', 35),
(4, '104', 'Building 4', 20),
(5, '105', 'Building 5', 25),
(6, '106', 'Building 1', 30),
(7, '107', 'Building 2', 35),
(8, '108', 'Building 3', 20),
(9, '109', 'Building 4', 25),
(10, '110', 'Building 5', 30),
(11, '111', 'Building 1', 35),
(12, '112', 'Building 2', 20),
(13, '113', 'Building 3', 25),
(14, '114', 'Building 4', 30),
(15, '115', 'Building 5', 35);

INSERT INTO Teachers (teacher_id, first_name, last_name, academic_degree, phone, email, department_id) VALUES
(1, 'Ayan', 'Saparov', 'MSc', '+7-701-1000001', 'ayan.saparov1@university.example', 1),
(2, 'Dana', 'Kassymova', 'PhD', '+7-701-1000002', 'dana.kassymova2@university.example', 2),
(3, 'Arman', 'Bekov', 'MSc', '+7-701-1000003', 'arman.bekov3@university.example', 3),
(4, 'Aigerim', 'Nurgaliyeva', 'PhD', '+7-701-1000004', 'aigerim.nurgaliyeva4@university.example', 4),
(5, 'Dias', 'Omarov', 'MSc', '+7-701-1000005', 'dias.omarov5@university.example', 5),
(6, 'Madina', 'Serikova', 'MA', '+7-701-1000006', 'madina.serikova6@university.example', 6),
(7, 'Nurlan', 'Tulegenov', 'PhD', '+7-701-1000007', 'nurlan.tulegenov7@university.example', 7),
(8, 'Aliya', 'Iskakova', 'MSc', '+7-701-1000008', 'aliya.iskakova8@university.example', 8),
(9, 'Timur', 'Akhmetov', 'MSc', '+7-701-1000009', 'timur.akhmetov9@university.example', 9),
(10, 'Amina', 'Zhaksylyk', 'PhD', '+7-701-1000010', 'amina.zhaksylyk10@university.example', 10),
(11, 'Miras', 'Bekturov', 'MBA', '+7-701-1000011', 'miras.bekturov11@university.example', 11),
(12, 'Kamila', 'Rakhimova', 'MA', '+7-701-1000012', 'kamila.rakhimova12@university.example', 12),
(13, 'Sanzhar', 'Yermekov', 'MSc', '+7-701-1000013', 'sanzhar.yermekov13@university.example', 13),
(14, 'Zarina', 'Abdullina', 'PhD', '+7-701-1000014', 'zarina.abdullina14@university.example', 14),
(15, 'Ruslan', 'Kenzhebayev', 'MSc', '+7-701-1000015', 'ruslan.kenzhebayev15@university.example', 15);

INSERT INTO Courses (course_id, course_name, credits, semester, department_id) VALUES
(1, 'Database Systems', 5, 1, 1),
(2, 'Programming Fundamentals', 5, 1, 2),
(3, 'Discrete Mathematics', 4, 1, 3),
(4, 'Physics for IT', 3, 1, 4),
(5, 'Academic English', 3, 1, 5),
(6, 'Object-Oriented Programming', 5, 2, 6),
(7, 'Web Development', 4, 2, 2),
(8, 'Information Systems', 4, 2, 7),
(9, 'Network Security', 4, 3, 8),
(10, 'Data Analytics', 4, 3, 9),
(11, 'Software Testing', 3, 3, 6),
(12, 'Project Management', 3, 4, 12),
(13, 'Statistics', 4, 2, 13),
(14, 'Artificial Intelligence', 5, 4, 14),
(15, 'Engineering Basics', 3, 1, 10);

INSERT INTO Students (student_id, last_name, first_name, birth_date, gender, phone, email, group_id) VALUES
(1001, 'Nazerke', 'Akhmet', '2004-01-05', 'F', '+7-707-2000000', 'akhmet.nazerke@student.university.example', 1),
(1002, 'Baimukhan', 'Nursultan', '2005-02-06', 'M', '+7-707-2000001', 'nursultan.baimukhan@student.university.example', 2),
(1003, 'Suleimenova', 'Amina', '2006-03-07', 'F', '+7-707-2000002', 'amina.suleimenova@student.university.example', 3),
(1004, 'Kairatov', 'Dias', '2004-04-08', 'M', '+7-707-2000003', 'dias.kairatov@student.university.example', 4),
(1005, 'Zholdas', 'Madina', '2005-05-09', 'F', '+7-707-2000004', 'madina.zholdas@student.university.example', 5),
(1006, 'Tursyn', 'Alikhan', '2006-06-10', 'M', '+7-707-2000005', 'alikhan.tursyn@student.university.example', 6),
(1007, 'Mukhanova', 'Dana', '2004-07-11', 'F', '+7-707-2000006', 'dana.mukhanova@student.university.example', 7),
(1008, 'Yessen', 'Islam', '2005-08-12', 'M', '+7-707-2000007', 'islam.yessen@student.university.example', 8),
(1009, 'Beketova', 'Aigerim', '2006-09-13', 'F', '+7-707-2000008', 'aigerim.beketova@student.university.example', 9),
(1010, 'Ospan', 'Miras', '2004-10-14', 'M', '+7-707-2000009', 'miras.ospan@student.university.example', 10),
(1011, 'Zhakupova', 'Kamila', '2005-11-15', 'F', '+7-707-2000010', 'kamila.zhakupova@student.university.example', 11),
(1012, 'Abilov', 'Sanzhar', '2006-12-16', 'M', '+7-707-2000011', 'sanzhar.abilov@student.university.example', 12),
(1013, 'Kaliyeva', 'Zarina', '2004-01-17', 'F', '+7-707-2000012', 'zarina.kaliyeva@student.university.example', 13),
(1014, 'Amanzhol', 'Timur', '2005-02-18', 'M', '+7-707-2000013', 'timur.amanzhol@student.university.example', 14),
(1015, 'Serik', 'Ademi', '2006-03-19', 'F', '+7-707-2000014', 'ademi.serik@student.university.example', 15);

INSERT INTO Schedule (schedule_id, course_id, teacher_id, group_id, classroom_id, day_of_week, start_time, end_time) VALUES
(1, 1, 1, 1, 1, 'Monday', '08:00:00', '09:50:00'),
(2, 2, 2, 2, 2, 'Tuesday', '09:00:00', '10:50:00'),
(3, 3, 3, 3, 3, 'Wednesday', '10:00:00', '11:50:00'),
(4, 4, 4, 4, 4, 'Thursday', '11:00:00', '12:50:00'),
(5, 5, 5, 5, 5, 'Friday', '12:00:00', '13:50:00'),
(6, 6, 6, 6, 6, 'Monday', '13:00:00', '14:50:00'),
(7, 7, 7, 7, 7, 'Tuesday', '08:00:00', '09:50:00'),
(8, 8, 8, 8, 8, 'Wednesday', '09:00:00', '10:50:00'),
(9, 9, 9, 9, 9, 'Thursday', '10:00:00', '11:50:00'),
(10, 10, 10, 10, 10, 'Friday', '11:00:00', '12:50:00'),
(11, 11, 11, 11, 11, 'Monday', '12:00:00', '13:50:00'),
(12, 12, 12, 12, 12, 'Tuesday', '13:00:00', '14:50:00'),
(13, 13, 13, 13, 13, 'Wednesday', '08:00:00', '09:50:00'),
(14, 14, 14, 14, 14, 'Thursday', '09:00:00', '10:50:00'),
(15, 15, 15, 15, 15, 'Friday', '10:00:00', '11:50:00');

INSERT INTO Grades (grade_id, student_id, course_id, grade_value, grade_date) VALUES
(1, 1001, 1, 67, '2026-05-01'),
(2, 1002, 2, 74, '2026-05-02'),
(3, 1003, 3, 81, '2026-05-03'),
(4, 1004, 4, 88, '2026-05-04'),
(5, 1005, 5, 95, '2026-05-05'),
(6, 1006, 6, 61, '2026-05-06'),
(7, 1007, 7, 68, '2026-05-07'),
(8, 1008, 8, 75, '2026-05-08'),
(9, 1009, 9, 82, '2026-05-09'),
(10, 1010, 10, 89, '2026-05-10'),
(11, 1011, 11, 96, '2026-05-11'),
(12, 1012, 12, 62, '2026-05-12'),
(13, 1013, 13, 69, '2026-05-13'),
(14, 1014, 14, 76, '2026-05-14'),
(15, 1015, 15, 83, '2026-05-15');

-- ADJUST THIS INSERT. Then run the queries that read settings.
INSERT INTO settings (
    selected_group_id,
    search_last_name,
    search_student_id,
    filter_gender,
    filter_max_group_id,
    grade_below,
    free_day,
    free_start,
    free_end,
    selected_course_id,
    selected_teacher_id,
    selected_schedule_id,
    selected_department_id
) VALUES (
    1,  -- selected group
    'Nazerke',  -- search by last name
    1001,  -- search by student id
    'F',  -- two-condition filter: gender
    5,  -- two-condition filter: group_id <= this value
    70,  -- grades below this score
    'Monday',  -- day used for a free-classroom search
    '08:00:00',  -- free-classroom window starts
    '09:50:00',  -- free-classroom window ends
    1,  -- course used in the extra queries
    1,  -- teacher used in the extra queries
    1,  -- schedule row used as one class
    1  -- department used in the extra queries
);

------------------------------------------------------------------------
-- Part 2, Part 3 and Part 4
------------------------------------------------------------------------

-- Part 2. All records from Students
-- Every column and every student.
SELECT *
FROM Students;

-- Part 2. Student id, first name and last name
-- The task asks for these three columns only.
SELECT student_id, first_name, last_name
FROM Students;

-- Part 2. All records from Groups
-- Group number, name, year and specialty.
SELECT *
FROM Groups;

-- Part 2. Names of all subjects
-- Courses is the subjects table in this database.
SELECT course_name
FROM Courses;

-- Part 3. Students in the selected group
-- WHERE keeps only the rows that match.
SELECT *
FROM Students
WHERE group_id = 1;

-- Part 3. Students in alphabetical order
-- ORDER BY sorts the rows. It does not remove any.
SELECT *
FROM Students
ORDER BY last_name ASC;

-- Part 3. Total number of students
-- COUNT(*) counts the rows.
SELECT COUNT(*) AS student_count
FROM Students;

-- Part 3. Number of students in each group
-- GROUP BY makes COUNT return one row per group.
SELECT group_id, COUNT(*) AS student_count
FROM Students
GROUP BY group_id
ORDER BY group_id;

-- Part 3. Maximum grade
-- The grade column in this database is grade_value.
SELECT MAX(grade_value) AS maximum_grade
FROM Grades;

-- Part 3. Minimum grade
-- MIN returns the lowest grade_value.
SELECT MIN(grade_value) AS minimum_grade
FROM Grades;

-- Part 3. Average grade
-- AVG returns the mean of grade_value.
SELECT AVG(grade_value) AS average_grade
FROM Grades;

-- Part 4. Student name and group name
-- Connected by Students.group_id = Groups.group_id.
SELECT
    Students.student_id,
    Students.first_name,
    Students.last_name,
    Groups.group_name,
    Groups.specialty,
    Groups.year_of_study
FROM Students
INNER JOIN Groups
    ON Students.group_id = Groups.group_id
ORDER BY Students.last_name, Students.first_name;

-- Part 4. Students and their grades
-- Connected by Grades.student_id = Students.student_id.
SELECT
    Students.student_id,
    Students.first_name,
    Students.last_name,
    Grades.course_id,
    Grades.grade_value,
    Grades.grade_date
FROM Students
INNER JOIN Grades
    ON Students.student_id = Grades.student_id
ORDER BY Students.last_name, Students.first_name;

-- Part 4. Student name, subject and grade
-- Grades.course_id matches Courses.course_id. Courses stores the subject name.
SELECT
    Students.first_name,
    Students.last_name,
    Courses.course_name AS subject,
    Grades.grade_value,
    Grades.grade_date
FROM Students
INNER JOIN Grades
    ON Students.student_id = Grades.student_id
INNER JOIN Courses
    ON Grades.course_id = Courses.course_id
ORDER BY Students.last_name, Students.first_name;

-- Part 4. INNER JOIN: departments and courses
-- A department with no course does not appear.
SELECT
    Departments.department_name,
    Courses.course_name
FROM Departments
INNER JOIN Courses
    ON Departments.department_id = Courses.department_id
ORDER BY Departments.department_id, Courses.course_name;

-- Part 4. LEFT JOIN: every department
-- Every department stays. A missing course is NULL.
SELECT
    Departments.department_name,
    Courses.course_name
FROM Departments
LEFT JOIN Courses
    ON Departments.department_id = Courses.department_id
ORDER BY Departments.department_id, Courses.course_name;

-- Part 4. One student before and after the JOIN
-- The Students table stores the group id. The JOIN adds the group name.
SELECT
    'Students table' AS source_table,
    student_id,
    first_name,
    last_name,
    CAST(group_id AS TEXT) AS group_info
FROM Students
WHERE student_id = 1001
UNION ALL
SELECT
    'Students JOIN Groups' AS source_table,
    Students.student_id,
    Students.first_name,
    Students.last_name,
    Groups.group_name
FROM Students
INNER JOIN Groups
    ON Students.group_id = Groups.group_id
WHERE Students.student_id = 1001;

------------------------------------------------------------------------
-- Topic 7 as SQL. Same filters as the Excel result sheets
------------------------------------------------------------------------

-- Topic 7 as SQL. Sort students by last name
-- Same order as the Excel sheet 07_Sort_Last_Name.
SELECT *
FROM Students
ORDER BY last_name ASC, first_name ASC;

-- Topic 7 as SQL. Sort students by group
-- Same order as the Excel sheet 07_Sort_Group.
SELECT *
FROM Students
ORDER BY group_id ASC, last_name ASC;

-- Topic 7 as SQL. Filter one group
-- Same rows as the Excel sheet 07_Filter_One_Group.
SELECT *
FROM Students
WHERE group_id = 1
ORDER BY last_name;

-- Topic 7 as SQL. Search by student id
-- Same rows as the first table on 07_Search.
SELECT *
FROM Students
WHERE student_id = 1001;

-- Topic 7 as SQL. Search by last name
-- The search ignores capital letters.
SELECT *
FROM Students
WHERE last_name COLLATE NOCASE = 'Nazerke';

-- Topic 7 as SQL. Filter with two conditions
-- Both conditions must be true.
SELECT *
FROM Students
WHERE gender = 'F'
  AND group_id <= 5
ORDER BY group_id, last_name;

------------------------------------------------------------------------
-- Queries that read the settings table. Run these after you edit settings
------------------------------------------------------------------------

-- Part 3. Students in the selected group
-- WHERE keeps only the rows that match.
SELECT *
FROM Students
WHERE group_id = (SELECT selected_group_id FROM settings);

-- Part 3. Students in alphabetical order
-- ORDER BY sorts the rows. It does not remove any.
SELECT *
FROM Students
ORDER BY last_name ASC;

-- Part 3. Total number of students
-- COUNT(*) counts the rows.
SELECT COUNT(*) AS student_count
FROM Students;

-- Part 3. Number of students in each group
-- GROUP BY makes COUNT return one row per group.
SELECT group_id, COUNT(*) AS student_count
FROM Students
GROUP BY group_id
ORDER BY group_id;

-- Part 3. Maximum grade
-- The grade column in this database is grade_value.
SELECT MAX(grade_value) AS maximum_grade
FROM Grades;

-- Part 3. Minimum grade
-- MIN returns the lowest grade_value.
SELECT MIN(grade_value) AS minimum_grade
FROM Grades;

-- Part 3. Average grade
-- AVG returns the mean of grade_value.
SELECT AVG(grade_value) AS average_grade
FROM Grades;

-- Part 4. Student name and group name
-- Connected by Students.group_id = Groups.group_id.
SELECT
    Students.student_id,
    Students.first_name,
    Students.last_name,
    Groups.group_name,
    Groups.specialty,
    Groups.year_of_study
FROM Students
INNER JOIN Groups
    ON Students.group_id = Groups.group_id
ORDER BY Students.last_name, Students.first_name;

-- Part 4. Students and their grades
-- Connected by Grades.student_id = Students.student_id.
SELECT
    Students.student_id,
    Students.first_name,
    Students.last_name,
    Grades.course_id,
    Grades.grade_value,
    Grades.grade_date
FROM Students
INNER JOIN Grades
    ON Students.student_id = Grades.student_id
ORDER BY Students.last_name, Students.first_name;

-- Part 4. Student name, subject and grade
-- Grades.course_id matches Courses.course_id. Courses stores the subject name.
SELECT
    Students.first_name,
    Students.last_name,
    Courses.course_name AS subject,
    Grades.grade_value,
    Grades.grade_date
FROM Students
INNER JOIN Grades
    ON Students.student_id = Grades.student_id
INNER JOIN Courses
    ON Grades.course_id = Courses.course_id
ORDER BY Students.last_name, Students.first_name;

-- Part 4. INNER JOIN: departments and courses
-- A department with no course does not appear.
SELECT
    Departments.department_name,
    Courses.course_name
FROM Departments
INNER JOIN Courses
    ON Departments.department_id = Courses.department_id
ORDER BY Departments.department_id, Courses.course_name;

-- Part 4. LEFT JOIN: every department
-- Every department stays. A missing course is NULL.
SELECT
    Departments.department_name,
    Courses.course_name
FROM Departments
LEFT JOIN Courses
    ON Departments.department_id = Courses.department_id
ORDER BY Departments.department_id, Courses.course_name;

-- Part 4. One student before and after the JOIN
-- The Students table stores the group id. The JOIN adds the group name.
SELECT
    'Students table' AS source_table,
    student_id,
    first_name,
    last_name,
    CAST(group_id AS TEXT) AS group_info
FROM Students
WHERE student_id = (SELECT search_student_id FROM settings)
UNION ALL
SELECT
    'Students JOIN Groups' AS source_table,
    Students.student_id,
    Students.first_name,
    Students.last_name,
    Groups.group_name
FROM Students
INNER JOIN Groups
    ON Students.group_id = Groups.group_id
WHERE Students.student_id = (SELECT search_student_id FROM settings);

-- Topic 7 as SQL. Filter one group
-- Same rows as the Excel sheet 07_Filter_One_Group.
SELECT *
FROM Students
WHERE group_id = (SELECT selected_group_id FROM settings)
ORDER BY last_name;

-- Topic 7 as SQL. Search by student id
-- Same rows as the first table on 07_Search.
SELECT *
FROM Students
WHERE student_id = (SELECT search_student_id FROM settings);

-- Topic 7 as SQL. Search by last name
-- The search ignores capital letters.
SELECT *
FROM Students
WHERE last_name COLLATE NOCASE = (SELECT search_last_name FROM settings);

-- Topic 7 as SQL. Filter with two conditions
-- Both conditions must be true.
SELECT *
FROM Students
WHERE gender = (SELECT filter_gender FROM settings)
  AND group_id <= (SELECT filter_max_group_id FROM settings)
ORDER BY group_id, last_name;

------------------------------------------------------------------------
-- Extra queries from Practice Work 1
------------------------------------------------------------------------

-- Extra. Practice 1. Students in a selected group
SELECT student_id, last_name, first_name, group_id
FROM Students
WHERE group_id = (SELECT selected_group_id FROM settings)
ORDER BY last_name;

-- Extra. Practice 1. Group of a selected student
SELECT
    s.student_id, s.last_name, s.first_name,
    g.group_name, g.year_of_study, g.specialty
FROM Students s
INNER JOIN Groups g ON s.group_id = g.group_id
WHERE s.student_id = (SELECT search_student_id FROM settings);

-- Extra. Practice 1. Courses a student studies
-- A student's courses are the courses scheduled for that student's group.
SELECT s.last_name, s.first_name, c.course_name, c.credits, c.semester
FROM Students s
INNER JOIN Schedule sch ON sch.group_id = s.group_id
INNER JOIN Courses c ON c.course_id = sch.course_id
WHERE s.student_id = (SELECT search_student_id FROM settings)
ORDER BY c.course_name;

-- Extra. Practice 1. Grades of a selected student
SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date
FROM Students s
INNER JOIN Grades g ON g.student_id = s.student_id
INNER JOIN Courses c ON c.course_id = g.course_id
WHERE s.student_id = (SELECT search_student_id FROM settings)
ORDER BY g.grade_date;

-- Extra. Practice 1. Average grade of a selected student
SELECT
    s.last_name,
    s.first_name,
    ROUND(AVG(g.grade_value), 2) AS average_grade
FROM Students s
INNER JOIN Grades g ON g.student_id = s.student_id
WHERE s.student_id = (SELECT search_student_id FROM settings)
GROUP BY s.student_id, s.last_name, s.first_name;

-- Extra. Practice 1. Teacher of a selected course
SELECT c.course_name, t.first_name, t.last_name, t.academic_degree
FROM Courses c
INNER JOIN Schedule sch ON sch.course_id = c.course_id
INNER JOIN Teachers t ON t.teacher_id = sch.teacher_id
WHERE c.course_id = (SELECT selected_course_id FROM settings)
ORDER BY t.last_name;

-- Extra. Practice 1. Courses of a selected teacher
SELECT t.first_name, t.last_name, c.course_name
FROM Teachers t
INNER JOIN Schedule sch ON sch.teacher_id = t.teacher_id
INNER JOIN Courses c ON c.course_id = sch.course_id
WHERE t.teacher_id = (SELECT selected_teacher_id FROM settings)
ORDER BY c.course_name;

-- Extra. Practice 1. Schedule of a selected group
SELECT
    g.group_name,
    c.course_name,
    t.first_name || ' ' || t.last_name AS teacher,
    cl.room_number,
    cl.building,
    sch.day_of_week,
    sch.start_time,
    sch.end_time
FROM Schedule sch
INNER JOIN Groups g ON g.group_id = sch.group_id
INNER JOIN Courses c ON c.course_id = sch.course_id
INNER JOIN Teachers t ON t.teacher_id = sch.teacher_id
INNER JOIN Classrooms cl ON cl.classroom_id = sch.classroom_id
WHERE sch.group_id = (SELECT selected_group_id FROM settings)
ORDER BY sch.day_of_week, sch.start_time;

-- Extra. Practice 1. Schedule of a selected teacher
SELECT
    t.first_name || ' ' || t.last_name AS teacher,
    c.course_name,
    g.group_name,
    cl.room_number,
    cl.building,
    sch.day_of_week,
    sch.start_time,
    sch.end_time
FROM Schedule sch
INNER JOIN Teachers t ON t.teacher_id = sch.teacher_id
INNER JOIN Courses c ON c.course_id = sch.course_id
INNER JOIN Groups g ON g.group_id = sch.group_id
INNER JOIN Classrooms cl ON cl.classroom_id = sch.classroom_id
WHERE sch.teacher_id = (SELECT selected_teacher_id FROM settings)
ORDER BY sch.day_of_week, sch.start_time;

-- Extra. Practice 1. Classroom of a selected class
SELECT
    sch.schedule_id,
    c.course_name,
    cl.room_number,
    cl.building,
    cl.capacity,
    sch.day_of_week,
    sch.start_time,
    sch.end_time
FROM Schedule sch
INNER JOIN Courses c ON c.course_id = sch.course_id
INNER JOIN Classrooms cl ON cl.classroom_id = sch.classroom_id
WHERE sch.schedule_id = (SELECT selected_schedule_id FROM settings);

-- Extra. Practice 1. Courses of a selected department
SELECT d.department_name, c.course_name, c.credits, c.semester
FROM Departments d
INNER JOIN Courses c ON c.department_id = d.department_id
WHERE d.department_id = (SELECT selected_department_id FROM settings)
ORDER BY c.course_name;

-- Extra. Practice 1. How many students are in each group
-- LEFT JOIN keeps a group even when it has no students.
SELECT g.group_id, g.group_name, COUNT(s.student_id) AS student_count
FROM Groups g
LEFT JOIN Students s ON s.group_id = g.group_id
GROUP BY g.group_id, g.group_name
ORDER BY g.group_id;

-- Extra. Practice 1. Highest average grades
SELECT
    s.student_id,
    s.last_name,
    s.first_name,
    ROUND(AVG(g.grade_value), 2) AS average_grade
FROM Students s
INNER JOIN Grades g ON g.student_id = s.student_id
GROUP BY s.student_id, s.last_name, s.first_name
ORDER BY average_grade DESC, s.last_name
LIMIT 5;

-- Extra. Practice 1. Grades below a chosen score
SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date
FROM Grades g
INNER JOIN Students s ON s.student_id = g.student_id
INNER JOIN Courses c ON c.course_id = g.course_id
WHERE g.grade_value < (SELECT grade_below FROM settings)
ORDER BY g.grade_value, s.last_name;

-- Extra. Practice 1. Classrooms free at a chosen time
-- A room is busy when its class overlaps the chosen window.
SELECT cl.classroom_id, cl.room_number, cl.building, cl.capacity
FROM Classrooms cl
CROSS JOIN settings st
WHERE NOT EXISTS (
    SELECT 1
    FROM Schedule sch
    WHERE sch.classroom_id = cl.classroom_id
      AND sch.day_of_week = st.free_day
      AND sch.start_time < st.free_end
      AND sch.end_time > st.free_start
)
ORDER BY cl.classroom_id;

-- Extra. Who received the maximum grade
SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date
FROM Grades g
INNER JOIN Students s ON s.student_id = g.student_id
INNER JOIN Courses c ON c.course_id = g.course_id
WHERE g.grade_value = (SELECT MAX(grade_value) FROM Grades)
ORDER BY s.last_name;

-- Extra. Who received the minimum grade
SELECT s.last_name, s.first_name, c.course_name, g.grade_value, g.grade_date
FROM Grades g
INNER JOIN Students s ON s.student_id = g.student_id
INNER JOIN Courses c ON c.course_id = g.course_id
WHERE g.grade_value = (SELECT MIN(grade_value) FROM Grades)
ORDER BY s.last_name;
