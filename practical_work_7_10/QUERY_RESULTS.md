# Query results reference

## Part 2 — All Students

```sql
SELECT * FROM Students;
```

| student_id | first_name | last_name | email | birth_date | group_id |
| --- | --- | --- | --- | --- | --- |
| 1 | Aigerim | Abayeva | a.abayeva@uni.edu | 2005-03-12 | 1 |
| 2 | Bekzat | Alimov | b.alimov@uni.edu | 2004-11-02 | 1 |
| 3 | Camila | Bekturova | c.bekturova@uni.edu | 2005-07-21 | 1 |
| 4 | Daniyar | Erzhanov | d.erzhanov@uni.edu | 2004-09-15 | 2 |
| 5 | Emily | Foster | e.foster@uni.edu | 2005-01-30 | 2 |
| 6 | Fariza | Gabdulova | f.gabdulova@uni.edu | 2004-05-08 | 2 |
| 7 | Gani | Iskakov | g.iskakov@uni.edu | 2003-12-19 | 3 |
| 8 | Hassan | Jumabekov | h.jumabekov@uni.edu | 2003-08-04 | 3 |
| 9 | Indira | Karimova | i.karimova@uni.edu | 2003-04-27 | 3 |
| 10 | Jasmin | Lee | j.lee@uni.edu | 2004-02-14 | 4 |
| 11 | Kanat | Mukhametov | k.mukhametov@uni.edu | 2003-10-09 | 4 |
| 12 | Laura | Nurzhanova | l.nurzhanova@uni.edu | 2004-06-18 | 4 |
| 13 | Madina | Omarova | m.omarova@uni.edu | 2005-08-25 | 1 |
| 14 | Nursultan | Petrov | n.petrov@uni.edu | 2004-12-03 | 2 |
| 15 | Olzhas | Rakhimov | o.rakhimov@uni.edu | 2003-03-11 | 3 |

## Part 2 — Student IDs and Names

```sql
SELECT student_id, first_name, last_name FROM Students;
```

| student_id | first_name | last_name |
| --- | --- | --- |
| 1 | Aigerim | Abayeva |
| 2 | Bekzat | Alimov |
| 3 | Camila | Bekturova |
| 4 | Daniyar | Erzhanov |
| 5 | Emily | Foster |
| 6 | Fariza | Gabdulova |
| 7 | Gani | Iskakov |
| 8 | Hassan | Jumabekov |
| 9 | Indira | Karimova |
| 10 | Jasmin | Lee |
| 11 | Kanat | Mukhametov |
| 12 | Laura | Nurzhanova |
| 13 | Madina | Omarova |
| 14 | Nursultan | Petrov |
| 15 | Olzhas | Rakhimov |

## Part 2 — All Groups

```sql
SELECT * FROM Groups;
```

| group_id | group_name | specialty | year |
| --- | --- | --- | --- |
| 1 | CS-101 | Computer Science | 2024 |
| 2 | IS-102 | Information Systems | 2024 |
| 3 | SE-201 | Software Engineering | 2023 |
| 4 | DS-202 | Data Science | 2023 |

## Part 2 — Subject Names

```sql
SELECT subject_name FROM Subjects;
```

| subject_name |
| --- |
| Introduction to Databases |
| Programming Fundamentals |
| Discrete Mathematics |
| Computer Networks |
| Algorithms and Data Structures |
| SQL and Data Processing |

## Part 3 — WHERE group_id = 1

```sql
SELECT * FROM Students WHERE group_id = 1;
```

| student_id | first_name | last_name | email | birth_date | group_id |
| --- | --- | --- | --- | --- | --- |
| 1 | Aigerim | Abayeva | a.abayeva@uni.edu | 2005-03-12 | 1 |
| 2 | Bekzat | Alimov | b.alimov@uni.edu | 2004-11-02 | 1 |
| 3 | Camila | Bekturova | c.bekturova@uni.edu | 2005-07-21 | 1 |
| 13 | Madina | Omarova | m.omarova@uni.edu | 2005-08-25 | 1 |

## Part 3 — ORDER BY last_name

```sql
SELECT * FROM Students ORDER BY last_name ASC;
```

| student_id | first_name | last_name | email | birth_date | group_id |
| --- | --- | --- | --- | --- | --- |
| 1 | Aigerim | Abayeva | a.abayeva@uni.edu | 2005-03-12 | 1 |
| 2 | Bekzat | Alimov | b.alimov@uni.edu | 2004-11-02 | 1 |
| 3 | Camila | Bekturova | c.bekturova@uni.edu | 2005-07-21 | 1 |
| 4 | Daniyar | Erzhanov | d.erzhanov@uni.edu | 2004-09-15 | 2 |
| 5 | Emily | Foster | e.foster@uni.edu | 2005-01-30 | 2 |
| 6 | Fariza | Gabdulova | f.gabdulova@uni.edu | 2004-05-08 | 2 |
| 7 | Gani | Iskakov | g.iskakov@uni.edu | 2003-12-19 | 3 |
| 8 | Hassan | Jumabekov | h.jumabekov@uni.edu | 2003-08-04 | 3 |
| 9 | Indira | Karimova | i.karimova@uni.edu | 2003-04-27 | 3 |
| 10 | Jasmin | Lee | j.lee@uni.edu | 2004-02-14 | 4 |
| 11 | Kanat | Mukhametov | k.mukhametov@uni.edu | 2003-10-09 | 4 |
| 12 | Laura | Nurzhanova | l.nurzhanova@uni.edu | 2004-06-18 | 4 |
| 13 | Madina | Omarova | m.omarova@uni.edu | 2005-08-25 | 1 |
| 14 | Nursultan | Petrov | n.petrov@uni.edu | 2004-12-03 | 2 |
| 15 | Olzhas | Rakhimov | o.rakhimov@uni.edu | 2003-03-11 | 3 |

## Part 3 — COUNT(*) total students

```sql
SELECT COUNT(*) AS total_students FROM Students;
```

| total_students |
| --- |
| 15 |

## Part 3 — GROUP BY student count

```sql
SELECT group_id, COUNT(*) AS student_count FROM Students GROUP BY group_id;
```

| group_id | student_count |
| --- | --- |
| 1 | 4 |
| 2 | 4 |
| 3 | 4 |
| 4 | 3 |

## Part 3 — MAX(grade)

```sql
SELECT MAX(grade) AS max_grade FROM Grades;
```

| max_grade |
| --- |
| 98 |

## Part 3 — MIN(grade)

```sql
SELECT MIN(grade) AS min_grade FROM Grades;
```

| min_grade |
| --- |
| 69 |

## Part 3 — AVG(grade)

```sql
SELECT ROUND(AVG(grade), 2) AS average_grade FROM Grades;
```

| average_grade |
| --- |
| 84.0 |

## Part 4 — INNER JOIN Students + Groups

```sql
SELECT Students.first_name, Students.last_name, Groups.group_name
FROM Students
INNER JOIN Groups ON Students.group_id = Groups.group_id
ORDER BY Groups.group_name, Students.last_name;
```

| first_name | last_name | group_name |
| --- | --- | --- |
| Aigerim | Abayeva | CS-101 |
| Bekzat | Alimov | CS-101 |
| Camila | Bekturova | CS-101 |
| Madina | Omarova | CS-101 |
| Jasmin | Lee | DS-202 |
| Kanat | Mukhametov | DS-202 |
| Laura | Nurzhanova | DS-202 |
| Daniyar | Erzhanov | IS-102 |
| Emily | Foster | IS-102 |
| Fariza | Gabdulova | IS-102 |
| Nursultan | Petrov | IS-102 |
| Gani | Iskakov | SE-201 |
| Hassan | Jumabekov | SE-201 |
| Indira | Karimova | SE-201 |
| Olzhas | Rakhimov | SE-201 |

## Part 4 — INNER JOIN Students + Grades

```sql
SELECT Students.first_name, Students.last_name, Grades.grade
FROM Students
INNER JOIN Grades ON Students.student_id = Grades.student_id
ORDER BY Students.last_name, Grades.grade DESC;
```

| first_name | last_name | grade |
| --- | --- | --- |
| Aigerim | Abayeva | 95 |
| Aigerim | Abayeva | 88 |
| Bekzat | Alimov | 82 |
| Bekzat | Alimov | 78 |
| Camila | Bekturova | 91 |
| Camila | Bekturova | 87 |
| Daniyar | Erzhanov | 80 |
| Daniyar | Erzhanov | 74 |
| Emily | Foster | 96 |
| Emily | Foster | 92 |
| Fariza | Gabdulova | 75 |
| Fariza | Gabdulova | 69 |
| Gani | Iskakov | 90 |
| Gani | Iskakov | 85 |
| Hassan | Jumabekov | 77 |
| Hassan | Jumabekov | 71 |
| Indira | Karimova | 98 |
| Indira | Karimova | 94 |
| Jasmin | Lee | 86 |
| Jasmin | Lee | 83 |
| Kanat | Mukhametov | 79 |
| Kanat | Mukhametov | 70 |
| Laura | Nurzhanova | 93 |
| Laura | Nurzhanova | 89 |
| Madina | Omarova | 84 |
| Madina | Omarova | 81 |
| Nursultan | Petrov | 76 |
| Nursultan | Petrov | 72 |
| Olzhas | Rakhimov | 97 |
| Olzhas | Rakhimov | 88 |

## Part 4 — JOIN Students + Grades + Subjects

```sql
SELECT Students.first_name, Students.last_name, Subjects.subject_name, Grades.grade
FROM Students
INNER JOIN Grades ON Students.student_id = Grades.student_id
INNER JOIN Exams ON Grades.exam_id = Exams.exam_id
INNER JOIN Subjects ON Exams.subject_id = Subjects.subject_id
ORDER BY Students.last_name, Subjects.subject_name;
```

| first_name | last_name | subject_name | grade |
| --- | --- | --- | --- |
| Aigerim | Abayeva | Introduction to Databases | 95 |
| Aigerim | Abayeva | SQL and Data Processing | 88 |
| Bekzat | Alimov | Introduction to Databases | 78 |
| Bekzat | Alimov | Programming Fundamentals | 82 |
| Camila | Bekturova | Introduction to Databases | 91 |
| Camila | Bekturova | SQL and Data Processing | 87 |
| Daniyar | Erzhanov | Computer Networks | 80 |
| Daniyar | Erzhanov | Programming Fundamentals | 74 |
| Emily | Foster | Programming Fundamentals | 96 |
| Emily | Foster | SQL and Data Processing | 92 |
| Fariza | Gabdulova | Discrete Mathematics | 75 |
| Fariza | Gabdulova | Introduction to Databases | 69 |
| Gani | Iskakov | Algorithms and Data Structures | 90 |
| Gani | Iskakov | Programming Fundamentals | 85 |
| Hassan | Jumabekov | Computer Networks | 77 |
| Hassan | Jumabekov | Discrete Mathematics | 71 |
| Indira | Karimova | Algorithms and Data Structures | 98 |
| Indira | Karimova | SQL and Data Processing | 94 |
| Jasmin | Lee | Algorithms and Data Structures | 86 |
| Jasmin | Lee | Discrete Mathematics | 83 |
| Kanat | Mukhametov | Algorithms and Data Structures | 79 |
| Kanat | Mukhametov | Computer Networks | 70 |
| Laura | Nurzhanova | Introduction to Databases | 93 |
| Laura | Nurzhanova | SQL and Data Processing | 89 |
| Madina | Omarova | Programming Fundamentals | 84 |
| Madina | Omarova | SQL and Data Processing | 81 |
| Nursultan | Petrov | Computer Networks | 72 |
| Nursultan | Petrov | Discrete Mathematics | 76 |
| Olzhas | Rakhimov | Algorithms and Data Structures | 97 |
| Olzhas | Rakhimov | Programming Fundamentals | 88 |

## Part 4 — LEFT JOIN Students + Grades

```sql
SELECT Students.first_name, Students.last_name, Grades.grade
FROM Students
LEFT JOIN Grades ON Students.student_id = Grades.student_id
ORDER BY Students.last_name;
```

| first_name | last_name | grade |
| --- | --- | --- |
| Aigerim | Abayeva | 88 |
| Aigerim | Abayeva | 95 |
| Bekzat | Alimov | 78 |
| Bekzat | Alimov | 82 |
| Camila | Bekturova | 87 |
| Camila | Bekturova | 91 |
| Daniyar | Erzhanov | 74 |
| Daniyar | Erzhanov | 80 |
| Emily | Foster | 92 |
| Emily | Foster | 96 |
| Fariza | Gabdulova | 69 |
| Fariza | Gabdulova | 75 |
| Gani | Iskakov | 85 |
| Gani | Iskakov | 90 |
| Hassan | Jumabekov | 71 |
| Hassan | Jumabekov | 77 |
| Indira | Karimova | 94 |
| Indira | Karimova | 98 |
| Jasmin | Lee | 83 |
| Jasmin | Lee | 86 |
| Kanat | Mukhametov | 70 |
| Kanat | Mukhametov | 79 |
| Laura | Nurzhanova | 89 |
| Laura | Nurzhanova | 93 |
| Madina | Omarova | 81 |
| Madina | Omarova | 84 |
| Nursultan | Petrov | 72 |
| Nursultan | Petrov | 76 |
| Olzhas | Rakhimov | 88 |
| Olzhas | Rakhimov | 97 |
