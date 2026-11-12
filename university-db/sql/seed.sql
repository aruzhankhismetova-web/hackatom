-- Sample dataset: 15 records in each of the 8 tables (120 rows).
-- Fictional records for the university educational process.
-- Insert parents before children so foreign keys resolve.

PRAGMA foreign_keys = ON;

INSERT INTO groups (group_id, group_name, year_of_study, specialty) VALUES
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

INSERT INTO departments (department_id, department_name, building) VALUES
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

INSERT INTO classrooms (classroom_id, room_number, building, capacity) VALUES
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

INSERT INTO students (
    student_id, last_name, first_name, birth_date, gender, phone, email, group_id
) VALUES
    (1001, 'Aliyeva', 'Aruzhan', '2004-01-05', 'F', '+7-707-2000000', 'aruzhan.aliyeva@student.university.example', 1),
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

INSERT INTO teachers (
    teacher_id, first_name, last_name, academic_degree, phone, email, department_id
) VALUES
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

INSERT INTO courses (course_id, course_name, credits, semester, department_id) VALUES
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

INSERT INTO schedule (
    schedule_id, course_id, teacher_id, group_id, classroom_id,
    day_of_week, start_time, end_time
) VALUES
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

INSERT INTO grades (grade_id, student_id, course_id, grade_value, grade_date) VALUES
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
