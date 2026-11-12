# University educational process

Practice Work 1 records the subject area. Practice Work 2 turns that model into a dataset of 15 rows in each table.

## What the database stores

The database holds the educational process: students, academic groups, teachers, departments, courses, classrooms, the class schedule, and grades. It is used to enroll students, offer courses, assign teachers, book rooms, and record results.

## Entities

| Entity | Primary key | Attributes |
| --- | --- | --- |
| Students | `student_id` | last_name, first_name, birth_date, gender, phone, email, group_id |
| Groups | `group_id` | group_name, year_of_study, specialty |
| Teachers | `teacher_id` | first_name, last_name, academic_degree, phone, email, department_id |
| Departments | `department_id` | department_name, building |
| Courses | `course_id` | course_name, credits, semester, department_id |
| Classrooms | `classroom_id` | room_number, building, capacity |
| Schedule | `schedule_id` | course_id, teacher_id, group_id, classroom_id, day_of_week, start_time, end_time |
| Grades | `grade_id` | student_id, course_id, grade_value, grade_date |

The Teachers column order follows the Practice Work 2 table (`first_name`, then `last_name`). Students follow the entity list (`last_name`, then `first_name`).

## Relationships

Every relationship is one-to-many. Each entity takes part in at least one relationship.

| From | To | Meaning |
| --- | --- | --- |
| Groups | Students | A student is in one group. A group has many students. |
| Groups | Schedule | A group has many classes. A class belongs to one group. |
| Departments | Teachers | A teacher works in one department. A department has many teachers. |
| Departments | Courses | A department offers many courses. A course belongs to one department. |
| Courses | Schedule | A course appears in many classes. A class refers to one course. |
| Teachers | Schedule | A teacher teaches many classes. A class has one teacher. |
| Classrooms | Schedule | A room is used for many classes at different times. A class uses one room. |
| Students | Grades | A student has many grades. A grade belongs to one student. |
| Courses | Grades | A course has many grades. A grade is for one course. |

## Constraints

1. Each student, group, teacher, department, course, classroom, schedule row, and grade has a unique id.
2. A date of birth cannot be in the future.
3. A student belongs to an existing group, a teacher to an existing department, and a course to an existing department.
4. Credits and classroom capacity are greater than 0.
5. A grade is from 0 to 100.
6. A class ends after it starts.
7. Student email addresses are unique.
8. A classroom cannot hold two classes that overlap on the same day. A later class may start when the earlier one ends.
9. A student cannot receive two grades for the same course on the same date.
10. Required text, including student name, course name, and group name, cannot be blank.

## Access

| User group | Rights |
| --- | --- |
| University administration | View, add, update, and manage all educational information |
| Teachers | View students and courses, add and update grades, view their schedules |
| Students | View their own information, schedule, courses, and grades |
| Department staff | Manage teachers, courses, groups, and schedules inside their department |
| Database administrator | Full access, including tables and user accounts |

Students do not change grades. A teacher changes grades only for courses that teacher teaches.

SQLite, used for the sample file in this project, has no user accounts. The rules above are the access design for a hosted database. `sql/queries.sql` is the read side of that design: students, teachers, and staff can answer the questions that match their role.

## Questions the database answers

1. Which students are in a given group?
2. Which group does a given student belong to?
3. Which courses does a student study?
4. Which grades has a student received?
5. What is a student's average grade?
6. Which teacher teaches a given course?
7. Which courses does a given teacher teach?
8. What is a group's schedule?
9. What is a teacher's schedule?
10. Which classroom is used for a given class?
11. Which courses does a department offer?
12. How many students are in each group?
13. Which students have the highest average grade?
14. Which students have a grade below a chosen value?
15. Which classrooms are free at a chosen time?

A student studies a course when that course is on the schedule of the student's group. A course's teacher is the teacher on that schedule.
