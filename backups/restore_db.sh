#!/bin/bash

# Usage:
# ./restore_db.sh path/to/your/file.backup
# hoặc
# ./restore_db.sh ./backups/taskdb_xxx.backup

CONTAINER_NAME="django_db_v3"
DB_NAME="taskdb"
DB_USER="taskuser"
DB_PASSWORD="taskpassword"

INPUT_FILE="$1"

if [ -z "$INPUT_FILE" ]; then
  echo "❌ Vui lòng truyền file backup (.backup)"
  echo "▶ Ví dụ: ./restore_db.sh ./backups/taskdb_20240524_153000.backup"
  exit 1
fi

# Extract filename only (không bao gồm path) để copy vào container
FILENAME=$(basename "$INPUT_FILE")

echo "📦 Copying $FILENAME vào container..."
docker cp "$INPUT_FILE" "$CONTAINER_NAME:/tmp/$FILENAME"

echo "🧨 Disconnect all active sessions from DB..."
docker exec -e PGPASSWORD=$DB_PASSWORD $CONTAINER_NAME psql -U $DB_USER -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
"

echo "🔁 Dropping and recreating DB..."
docker exec -e PGPASSWORD=$DB_PASSWORD $CONTAINER_NAME psql -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec -e PGPASSWORD=$DB_PASSWORD $CONTAINER_NAME psql -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

echo "📥 Restoring from $FILENAME..."
docker exec -e PGPASSWORD=$DB_PASSWORD $CONTAINER_NAME pg_restore -U $DB_USER -d $DB_NAME -c "/tmp/$FILENAME"

echo "🧹 Cleaning up..."
docker exec $CONTAINER_NAME rm "/tmp/$FILENAME"

echo "✅ Restore thành công database $DB_NAME từ $INPUT_FILE"
