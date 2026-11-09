-- Questions the university database must answer.
-- Each statement uses one concrete example from the sample dataset.
-- Change the literal in the WHERE clause to ask about another group,
-- student, course, teacher, department, grade threshold, or time.

-- name: students_in_group
-- 1. What students are enrolled in a particular group? (IT-21, group_id = 1)
SELECT
    s.student_id,
    s.last_name,
    s.first_name,
    g.group_name
FROM students AS s
JOIN groups AS g ON g.group_id = s.group_id
WHERE g.group_id = 1
ORDER BY s.last_name, s.first_name;

-- name: group_of_student
-- 2. Which group does a particular student belong to? (Aruzhan Aliyeva, 1001)
SELECT
    s.student_id,
    s.last_name,
    s.first_name,
    g.group_id,
    g.group_name,
    g.year_of_study,
    g.specialty
FROM students AS s
JOIN groups AS g ON g.group_id = s.group_id
WHERE s.student_id = 1001;

-- name: courses_of_student
-- 3. What courses does a particular student study?
-- A student studies the courses scheduled for their group.
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_id,
    c.course_name,
    c.credits,
    c.semester
FROM students AS s
JOIN schedule AS sch ON sch.group_id = s.group_id
JOIN courses AS c ON c.course_id = sch.course_id
WHERE s.student_id = 1001
ORDER BY c.course_name;

-- name: grades_of_student
-- 4. What grades has a particular student received?
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_name,
    g.grade_value,
    g.grade_date
FROM grades AS g
JOIN students AS s ON s.student_id = g.student_id
JOIN courses AS c ON c.course_id = g.course_id
WHERE s.student_id = 1001
ORDER BY g.grade_date, c.course_name;

-- name: average_grade_of_student
-- 5. What is the average grade of a particular student?
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    ROUND(AVG(g.grade_value), 2) AS average_grade
FROM students AS s
JOIN grades AS g ON g.student_id = s.student_id
WHERE s.student_id = 1001
GROUP BY s.student_id;

-- name: teachers_of_course
-- 6. Which teacher teaches a particular course? (Database Systems, course_id = 1)
SELECT DISTINCT
    c.course_id,
    c.course_name,
    t.teacher_id,
    t.first_name || ' ' || t.last_name AS teacher_name,
    t.academic_degree
FROM schedule AS sch
JOIN courses AS c ON c.course_id = sch.course_id
JOIN teachers AS t ON t.teacher_id = sch.teacher_id
WHERE c.course_id = 1
ORDER BY t.last_name, t.first_name;

-- name: courses_of_teacher
-- 7. What courses does a particular teacher teach? (Ayan Saparov, teacher_id = 1)
SELECT DISTINCT
    t.teacher_id,
    t.first_name || ' ' || t.last_name AS teacher_name,
    c.course_id,
    c.course_name,
    c.credits
FROM schedule AS sch
JOIN teachers AS t ON t.teacher_id = sch.teacher_id
JOIN courses AS c ON c.course_id = sch.course_id
WHERE t.teacher_id = 1
ORDER BY c.course_name;

-- name: schedule_of_group
-- 8. What is the schedule for a particular group? (IT-21)
SELECT
    g.group_name,
    sch.day_of_week,
    sch.start_time,
    sch.end_time,
    c.course_name,
    t.first_name || ' ' || t.last_name AS teacher_name,
    cl.room_number,
    cl.building
FROM schedule AS sch
JOIN groups AS g ON g.group_id = sch.group_id
JOIN courses AS c ON c.course_id = sch.course_id
JOIN teachers AS t ON t.teacher_id = sch.teacher_id
JOIN classrooms AS cl ON cl.classroom_id = sch.classroom_id
WHERE g.group_id = 1
ORDER BY
    CASE sch.day_of_week
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END,
    sch.start_time;

-- name: schedule_of_teacher
-- 9. What is the schedule for a particular teacher? (Ayan Saparov)
SELECT
    t.first_name || ' ' || t.last_name AS teacher_name,
    sch.day_of_week,
    sch.start_time,
    sch.end_time,
    c.course_name,
    g.group_name,
    cl.room_number,
    cl.building
FROM schedule AS sch
JOIN teachers AS t ON t.teacher_id = sch.teacher_id
JOIN courses AS c ON c.course_id = sch.course_id
JOIN groups AS g ON g.group_id = sch.group_id
JOIN classrooms AS cl ON cl.classroom_id = sch.classroom_id
WHERE t.teacher_id = 1
ORDER BY
    CASE sch.day_of_week
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END,
    sch.start_time;

-- name: classroom_of_class
-- 10. Which classroom is used for a particular class? (schedule_id = 1)
SELECT
    sch.schedule_id,
    c.course_name,
    g.group_name,
    sch.day_of_week,
    sch.start_time,
    sch.end_time,
    cl.classroom_id,
    cl.room_number,
    cl.building
FROM schedule AS sch
JOIN courses AS c ON c.course_id = sch.course_id
JOIN groups AS g ON g.group_id = sch.group_id
JOIN classrooms AS cl ON cl.classroom_id = sch.classroom_id
WHERE sch.schedule_id = 1;

-- name: courses_of_department
-- 11. Which courses are offered by a particular department? (Computer Science)
SELECT
    d.department_name,
    c.course_id,
    c.course_name,
    c.credits,
    c.semester
FROM courses AS c
JOIN departments AS d ON d.department_id = c.department_id
WHERE d.department_id = 1
ORDER BY c.course_name;

-- name: students_per_group
-- 12. How many students are enrolled in each group?
SELECT
    g.group_id,
    g.group_name,
    g.specialty,
    COUNT(s.student_id) AS student_count
FROM groups AS g
LEFT JOIN students AS s ON s.group_id = g.group_id
GROUP BY g.group_id
ORDER BY g.group_id;

-- name: students_with_highest_average
-- 13. Which students have the highest average grades?
SELECT
    s.student_id,
    s.last_name,
    s.first_name,
    ROUND(AVG(g.grade_value), 2) AS average_grade
FROM students AS s
JOIN grades AS g ON g.student_id = s.student_id
GROUP BY s.student_id
HAVING AVG(g.grade_value) = (
    SELECT MAX(student_average)
    FROM (
        SELECT AVG(grade_value) AS student_average
        FROM grades
        GROUP BY student_id
    )
)
ORDER BY s.last_name, s.first_name;

-- name: students_below_grade
-- 14. Which students have grades below a specified value? (below 70)
SELECT
    s.student_id,
    s.last_name,
    s.first_name,
    c.course_name,
    g.grade_value,
    g.grade_date
FROM grades AS g
JOIN students AS s ON s.student_id = g.student_id
JOIN courses AS c ON c.course_id = g.course_id
WHERE g.grade_value < 70
ORDER BY g.grade_value, s.last_name;

-- name: available_classrooms
-- 15. Which classrooms are available at a particular time?
-- Example: Monday 08:00–09:50. Room 101 is busy; the other rooms are free.
-- A room is free when no class on that day overlaps the requested interval.
SELECT
    cl.classroom_id,
    cl.room_number,
    cl.building,
    cl.capacity
FROM classrooms AS cl
WHERE NOT EXISTS (
    SELECT 1
    FROM schedule AS sch
    WHERE sch.classroom_id = cl.classroom_id
      AND sch.day_of_week = 'Monday'
      AND sch.start_time < '09:50:00'
      AND sch.end_time > '08:00:00'
)
ORDER BY cl.building, cl.room_number;
