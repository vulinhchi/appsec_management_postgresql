#!/bin/bash

# Backup PostgreSQL running in Docker

# cách dùng:
# chmod +x backup_db.sh
# ./backup_db.sh



CONTAINER_NAME="django_db_v2"
DB_NAME="taskdb"
DB_USER="taskuser"
BACKUP_FILE="taskdb_$(date +%Y%m%d_%H%M%S).backup"

# Run backup inside container
docker exec -e PGPASSWORD=taskpassword $CONTAINER_NAME pg_dump -U $DB_USER -F c -d $DB_NAME -f /tmp/$BACKUP_FILE

# Copy backup file from container to host
docker cp $CONTAINER_NAME:/tmp/$BACKUP_FILE ./backups/

# Optional: Clean up inside container
docker exec $CONTAINER_NAME rm /tmp/$BACKUP_FILE

echo "✅ Backup saved to ./backups/$BACKUP_FILE"
