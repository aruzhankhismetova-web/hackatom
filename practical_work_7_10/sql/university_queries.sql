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

BEGIN TRANSACTION;
INSERT INTO Groups VALUES (1, 'CS-101', 'Computer Science', 2024);
INSERT INTO Groups VALUES (2, 'IS-102', 'Information Systems', 2024);
INSERT INTO Groups VALUES (3, 'SE-201', 'Software Engineering', 2023);
INSERT INTO Groups VALUES (4, 'DS-202', 'Data Science', 2023);
INSERT INTO Teachers VALUES (1, 'Elena', 'Morozova', 'Professor', 'Databases');
INSERT INTO Teachers VALUES (2, 'Arman', 'Suleimenov', 'Associate Professor', 'Programming');
INSERT INTO Teachers VALUES (3, 'Sara', 'Kim', 'Senior Lecturer', 'Mathematics');
INSERT INTO Teachers VALUES (4, 'Dias', 'Nurpeisov', 'Lecturer', 'Networks');
INSERT INTO Teachers VALUES (5, 'Amina', 'Bekova', 'Professor', 'Algorithms');
INSERT INTO Subjects VALUES (1, 'Introduction to Databases', 1, 4);
INSERT INTO Subjects VALUES (2, 'Programming Fundamentals', 2, 5);
INSERT INTO Subjects VALUES (3, 'Discrete Mathematics', 3, 4);
INSERT INTO Subjects VALUES (4, 'Computer Networks', 4, 3);
INSERT INTO Subjects VALUES (5, 'Algorithms and Data Structures', 5, 5);
INSERT INTO Subjects VALUES (6, 'SQL and Data Processing', 1, 4);
INSERT INTO Students VALUES (1, 'Aigerim', 'Abayeva', 'a.abayeva@uni.edu', '2005-03-12', 1);
INSERT INTO Students VALUES (2, 'Bekzat', 'Alimov', 'b.alimov@uni.edu', '2004-11-02', 1);
INSERT INTO Students VALUES (3, 'Camila', 'Bekturova', 'c.bekturova@uni.edu', '2005-07-21', 1);
INSERT INTO Students VALUES (4, 'Daniyar', 'Erzhanov', 'd.erzhanov@uni.edu', '2004-09-15', 2);
INSERT INTO Students VALUES (5, 'Emily', 'Foster', 'e.foster@uni.edu', '2005-01-30', 2);
INSERT INTO Students VALUES (6, 'Fariza', 'Gabdulova', 'f.gabdulova@uni.edu', '2004-05-08', 2);
INSERT INTO Students VALUES (7, 'Gani', 'Iskakov', 'g.iskakov@uni.edu', '2003-12-19', 3);
INSERT INTO Students VALUES (8, 'Hassan', 'Jumabekov', 'h.jumabekov@uni.edu', '2003-08-04', 3);
INSERT INTO Students VALUES (9, 'Indira', 'Karimova', 'i.karimova@uni.edu', '2003-04-27', 3);
INSERT INTO Students VALUES (10, 'Jasmin', 'Lee', 'j.lee@uni.edu', '2004-02-14', 4);
INSERT INTO Students VALUES (11, 'Kanat', 'Mukhametov', 'k.mukhametov@uni.edu', '2003-10-09', 4);
INSERT INTO Students VALUES (12, 'Laura', 'Nurzhanova', 'l.nurzhanova@uni.edu', '2004-06-18', 4);
INSERT INTO Students VALUES (13, 'Madina', 'Omarova', 'm.omarova@uni.edu', '2005-08-25', 1);
INSERT INTO Students VALUES (14, 'Nursultan', 'Petrov', 'n.petrov@uni.edu', '2004-12-03', 2);
INSERT INTO Students VALUES (15, 'Olzhas', 'Rakhimov', 'o.rakhimov@uni.edu', '2003-03-11', 3);
INSERT INTO Exams VALUES (1, 1, '2025-01-15', 'Midterm');
INSERT INTO Exams VALUES (2, 2, '2025-01-17', 'Midterm');
INSERT INTO Exams VALUES (3, 3, '2025-01-20', 'Final');
INSERT INTO Exams VALUES (4, 4, '2025-01-22', 'Final');
INSERT INTO Exams VALUES (5, 5, '2025-01-24', 'Final');
INSERT INTO Exams VALUES (6, 6, '2025-01-27', 'Final');
INSERT INTO Grades VALUES (1, 1, 1, 95);
INSERT INTO Grades VALUES (2, 1, 6, 88);
INSERT INTO Grades VALUES (3, 2, 1, 78);
INSERT INTO Grades VALUES (4, 2, 2, 82);
INSERT INTO Grades VALUES (5, 3, 1, 91);
INSERT INTO Grades VALUES (6, 3, 6, 87);
INSERT INTO Grades VALUES (7, 4, 2, 74);
INSERT INTO Grades VALUES (8, 4, 4, 80);
INSERT INTO Grades VALUES (9, 5, 2, 96);
INSERT INTO Grades VALUES (10, 5, 6, 92);
INSERT INTO Grades VALUES (11, 6, 1, 69);
INSERT INTO Grades VALUES (12, 6, 3, 75);
INSERT INTO Grades VALUES (13, 7, 2, 85);
INSERT INTO Grades VALUES (14, 7, 5, 90);
INSERT INTO Grades VALUES (15, 8, 3, 71);
INSERT INTO Grades VALUES (16, 8, 4, 77);
INSERT INTO Grades VALUES (17, 9, 5, 98);
INSERT INTO Grades VALUES (18, 9, 6, 94);
INSERT INTO Grades VALUES (19, 10, 3, 83);
INSERT INTO Grades VALUES (20, 10, 5, 86);
INSERT INTO Grades VALUES (21, 11, 4, 70);
INSERT INTO Grades VALUES (22, 11, 5, 79);
INSERT INTO Grades VALUES (23, 12, 1, 93);
INSERT INTO Grades VALUES (24, 12, 6, 89);
INSERT INTO Grades VALUES (25, 13, 2, 84);
INSERT INTO Grades VALUES (26, 13, 6, 81);
INSERT INTO Grades VALUES (27, 14, 3, 76);
INSERT INTO Grades VALUES (28, 14, 4, 72);
INSERT INTO Grades VALUES (29, 15, 5, 97);
INSERT INTO Grades VALUES (30, 15, 2, 88);
COMMIT;

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
