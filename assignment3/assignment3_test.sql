-- Assignment 3 test database
-- Student: Сахташева Райхан
-- SQLite 3.45.1

DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS apps;

CREATE TABLE students (
  id INTEGER PRIMARY KEY,
  full_name TEXT NOT NULL,
  topic TEXT NOT NULL,
  score INTEGER NOT NULL
);

CREATE TABLE apps (
  id INTEGER PRIMARY KEY,
  app_name TEXT NOT NULL,
  category TEXT NOT NULL,
  version TEXT NOT NULL,
  result TEXT NOT NULL
);

INSERT INTO students (id, full_name, topic, score) VALUES
  (1, 'Сахташева Райхан', '1.33 Web browser', 95),
  (2, 'Сахташева Райхан', '1.34 Communication', 90),
  (3, 'Сахташева Райхан', '1.36 Database', 92);

INSERT INTO apps (id, app_name, category, version, result) VALUES
  (1, 'Google Chrome', 'Web browser', '156.0.8078.47', 'configured'),
  (2, 'Telegram Desktop', 'Communication', '7.4', 'installed, sign-in requires a phone number'),
  (3, 'SQLite', 'Database', '3.45.1', 'verified');

SELECT * FROM students;
SELECT * FROM apps;
