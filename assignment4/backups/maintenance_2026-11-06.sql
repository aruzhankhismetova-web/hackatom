PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE maintenance (
  id INTEGER PRIMARY KEY,
  item TEXT NOT NULL,
  detail TEXT NOT NULL
);
INSERT INTO maintenance VALUES(1,'student','Сахташева Райхан');
INSERT INTO maintenance VALUES(2,'date','6 ноября 2026');
INSERT INTO maintenance VALUES(3,'os','Ubuntu 24.04.5 LTS x86_64');
INSERT INTO maintenance VALUES(4,'chrome_before','156.0.8078.47');
INSERT INTO maintenance VALUES(5,'chrome_after','157.0.8103.38');
INSERT INTO maintenance VALUES(6,'sqlitebrowser','3.12.2');
INSERT INTO maintenance VALUES(7,'note','backup created with sqlite3 .backup');
COMMIT;
