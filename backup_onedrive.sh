#!/bin/bash

PROJECT_DIR="/root/adonis_site"
BACKUP_DIR="$PROJECT_DIR/backups"
ONEDRIVE_REMOTE="onedrive:adonis_backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_NAME="adonis_backup_$DATE"
KEEP_LOCAL_DAYS=7
KEEP_REMOTE_DAYS=30
LOG_FILE="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "===== Backup started ====="

TEMP_DIR=$(mktemp -d)
BACKUP_PATH="$TEMP_DIR/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"

log "Backing up database..."
cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_PATH/db.sqlite3"

log "Backing up media files..."
rsync -a --quiet "$PROJECT_DIR/media/" "$BACKUP_PATH/media/"

log "Backing up configuration files..."
cp "$PROJECT_DIR/.env" "$BACKUP_PATH/.env" 2>/dev/null
cp "$PROJECT_DIR/requirements.txt" "$BACKUP_PATH/requirements.txt" 2>/dev/null
cp "$PROJECT_DIR/manage.py" "$BACKUP_PATH/manage.py" 2>/dev/null

for app_dir in adonis core properties brochures; do
    if [ -d "$PROJECT_DIR/$app_dir" ]; then
        rsync -a --quiet \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            "$PROJECT_DIR/$app_dir/" "$BACKUP_PATH/$app_dir/"
    fi
done

log "Compressing backup..."
ARCHIVE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
tar -czf "$ARCHIVE" -C "$TEMP_DIR" "$BACKUP_NAME"
rm -rf "$TEMP_DIR"

ARCHIVE_SIZE=$(du -h "$ARCHIVE" | cut -f1)
log "Archive created: $ARCHIVE ($ARCHIVE_SIZE)"

log "Uploading to OneDrive..."
if rclone copy "$ARCHIVE" "$ONEDRIVE_REMOTE/" --progress 2>&1 | tee -a "$LOG_FILE"; then
    log "Upload successful!"
else
    log "ERROR: Upload to OneDrive failed!"
    exit 1
fi

log "Cleaning local backups older than $KEEP_LOCAL_DAYS days..."
find "$BACKUP_DIR" -name "adonis_backup_*.tar.gz" -mtime +$KEEP_LOCAL_DAYS -delete -print | while read f; do
    log "Deleted local: $f"
done

log "Cleaning remote backups older than $KEEP_REMOTE_DAYS days..."
rclone delete "$ONEDRIVE_REMOTE/" --min-age "${KEEP_REMOTE_DAYS}d" 2>&1 | tee -a "$LOG_FILE"

log "===== Backup completed successfully ====="
echo ""
