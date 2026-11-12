# Query results

Results of `sql/queries.sql` against the 120-row sample dataset.

## 1. Students enrolled in group IT-21

| student_id | last_name | first_name | group_name |
| --- | --- | --- | --- |
| 1001 | Aliyeva | Aruzhan | IT-21 |

## 2. Group of student 1001 (Aruzhan Aliyeva)

| student_id | last_name | first_name | group_id | group_name | year_of_study | specialty |
| --- | --- | --- | --- | --- | --- | --- |
| 1001 | Aliyeva | Aruzhan | 1 | IT-21 | 1 | Software Engineering |

## 3. Courses studied by student 1001

| student_id | student_name | course_id | course_name | credits | semester |
| --- | --- | --- | --- | --- | --- |
| 1001 | Aruzhan Aliyeva | 1 | Database Systems | 5 | 1 |

## 4. Grades received by student 1001

| student_id | student_name | course_name | grade_value | grade_date |
| --- | --- | --- | --- | --- |
| 1001 | Aruzhan Aliyeva | Database Systems | 67 | 2026-05-01 |

## 5. Average grade of student 1001

| student_id | student_name | average_grade |
| --- | --- | --- |
| 1001 | Aruzhan Aliyeva | 67.0 |

## 6. Teacher of Database Systems

| course_id | course_name | teacher_id | teacher_name | academic_degree |
| --- | --- | --- | --- | --- |
| 1 | Database Systems | 1 | Ayan Saparov | MSc |

## 7. Courses taught by teacher 1 (Ayan Saparov)

| teacher_id | teacher_name | course_id | course_name | credits |
| --- | --- | --- | --- | --- |
| 1 | Ayan Saparov | 1 | Database Systems | 5 |

## 8. Schedule of group IT-21

| group_name | day_of_week | start_time | end_time | course_name | teacher_name | room_number | building |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IT-21 | Monday | 08:00:00 | 09:50:00 | Database Systems | Ayan Saparov | 101 | Building 1 |

## 9. Schedule of teacher Ayan Saparov

| teacher_name | day_of_week | start_time | end_time | course_name | group_name | room_number | building |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ayan Saparov | Monday | 08:00:00 | 09:50:00 | Database Systems | IT-21 | 101 | Building 1 |

## 10. Classroom for schedule record 1

| schedule_id | course_name | group_name | day_of_week | start_time | end_time | classroom_id | room_number | building |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Database Systems | IT-21 | Monday | 08:00:00 | 09:50:00 | 1 | 101 | Building 1 |

## 11. Courses offered by Computer Science

| department_name | course_id | course_name | credits | semester |
| --- | --- | --- | --- | --- |
| Computer Science | 1 | Database Systems | 5 | 1 |

## 12. Students enrolled in each group

| group_id | group_name | specialty | student_count |
| --- | --- | --- | --- |
| 1 | IT-21 | Software Engineering | 1 |
| 2 | IT-22 | Software Engineering | 1 |
| 3 | IT-23 | Software Engineering | 1 |
| 4 | IT-24 | Software Engineering | 1 |
| 5 | IT-25 | Software Engineering | 1 |
| 6 | IT-26 | Information Systems | 1 |
| 7 | IT-27 | Information Systems | 1 |
| 8 | IT-28 | Information Systems | 1 |
| 9 | IT-29 | Information Systems | 1 |
| 10 | IT-30 | Information Systems | 1 |
| 11 | IT-31 | Computer Science | 1 |
| 12 | IT-32 | Computer Science | 1 |
| 13 | IT-33 | Computer Science | 1 |
| 14 | IT-34 | Computer Science | 1 |
| 15 | IT-35 | Computer Science | 1 |

## 13. Students with the highest average grade

| student_id | last_name | first_name | average_grade |
| --- | --- | --- | --- |
| 1011 | Zhakupova | Kamila | 96.0 |

## 14. Students with a grade below 70

| student_id | last_name | first_name | course_name | grade_value | grade_date |
| --- | --- | --- | --- | --- | --- |
| 1006 | Tursyn | Alikhan | Object-Oriented Programming | 61 | 2026-05-06 |
| 1012 | Abilov | Sanzhar | Project Management | 62 | 2026-05-12 |
| 1001 | Aliyeva | Aruzhan | Database Systems | 67 | 2026-05-01 |
| 1007 | Mukhanova | Dana | Web Development | 68 | 2026-05-07 |
| 1013 | Kaliyeva | Zarina | Statistics | 69 | 2026-05-13 |

## 15. Classrooms free on Monday 08:00–09:50

| classroom_id | room_number | building | capacity |
| --- | --- | --- | --- |
| 6 | 106 | Building 1 | 30 |
| 11 | 111 | Building 1 | 35 |
| 2 | 102 | Building 2 | 30 |
| 7 | 107 | Building 2 | 35 |
| 12 | 112 | Building 2 | 20 |
| 3 | 103 | Building 3 | 35 |
| 8 | 108 | Building 3 | 20 |
| 13 | 113 | Building 3 | 25 |
| 4 | 104 | Building 4 | 20 |
| 9 | 109 | Building 4 | 25 |
| 14 | 114 | Building 4 | 30 |
| 5 | 105 | Building 5 | 25 |
| 10 | 110 | Building 5 | 30 |
| 15 | 115 | Building 5 | 35 |
