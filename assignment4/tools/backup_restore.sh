#!/bin/bash
# Create a SQLite maintenance note, back it up, and restore the copy.
# Safe demonstration only: files stay under /workspace/assignment4.
set -euo pipefail
ROOT=/workspace/assignment4
LIVE=$ROOT/data/maintenance.db
BACKUP=$ROOT/backups/maintenance_2026-11-06.db
SQL=$ROOT/backups/maintenance_2026-11-06.sql
RESTORED=$ROOT/recovery/maintenance_restored.db
mkdir -p "$ROOT/data" "$ROOT/backups" "$ROOT/recovery"
rm -f "$LIVE" "$BACKUP" "$RESTORED" "$SQL"
sqlite3 "$LIVE" << 'SQL'
CREATE TABLE maintenance (
  id INTEGER PRIMARY KEY,
  item TEXT NOT NULL,
  detail TEXT NOT NULL
);
INSERT INTO maintenance(item, detail) VALUES
 ('student', 'Сахташева Райхан'),
 ('date', '6 ноября 2026'),
 ('os', 'Ubuntu 24.04.5 LTS x86_64'),
 ('chrome_before', '156.0.8078.47'),
 ('chrome_after', '157.0.8103.38'),
 ('sqlitebrowser', '3.12.2'),
 ('note', 'backup created with sqlite3 .backup');
SQL
sqlite3 "$LIVE" "PRAGMA integrity_check;"
sqlite3 "$LIVE" ".backup '$BACKUP'"
sqlite3 "$LIVE" ".dump" > "$SQL"
sqlite3 "$RESTORED" ".restore '$BACKUP'"
sqlite3 -header -column "$RESTORED" "SELECT id, item, detail FROM maintenance;"
sqlite3 "$BACKUP" "PRAGMA integrity_check;"
sqlite3 "$RESTORED" "PRAGMA integrity_check;"
sha256sum "$LIVE" "$BACKUP" "$SQL" "$RESTORED" | tee "$ROOT/backups/SHA256SUMS"
ls -l "$LIVE" "$BACKUP" "$SQL" "$RESTORED"
