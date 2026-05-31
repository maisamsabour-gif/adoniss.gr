#!/usr/bin/env bash
#
# Adoniss (Persian site) — daily full backup wrapper.
# Runs the Django `backup_full` command (DB + .env locally, and incremental
# media sync to ArvanCloud Object Storage when configured) and logs the run.
#
# Scheduled by systemd timer: adoniss-backup.timer (see deploy/backup/systemd/).
#
set -euo pipefail

PROJECT_DIR="/root/adonis_site"
PYTHON="$PROJECT_DIR/venv/bin/python"
LOG_DIR="$PROJECT_DIR/backups"
LOG_FILE="$LOG_DIR/backup.log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "==== $(date -u +%Y-%m-%dT%H:%M:%SZ) backup start ====" >> "$LOG_FILE"
if "$PYTHON" manage.py backup_full --label daily >> "$LOG_FILE" 2>&1; then
    echo "==== $(date -u +%Y-%m-%dT%H:%M:%SZ) backup OK ====" >> "$LOG_FILE"
else
    echo "==== $(date -u +%Y-%m-%dT%H:%M:%SZ) backup FAILED (exit $?) ====" >> "$LOG_FILE"
    exit 1
fi
