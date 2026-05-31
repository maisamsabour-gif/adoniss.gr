#!/usr/bin/env sh
set -e

mkdir -p /backups

echo "[backup] loop started (daily dump at ${BACKUP_HOUR_UTC:-00}:00 UTC)"

while true; do
  NOW_HOUR="$(date -u +%H)"
  if [ "$NOW_HOUR" = "${BACKUP_HOUR_UTC:-00}" ]; then
    TS="$(date -u +%Y%m%dT%H%M%SZ)"
    FILE="/backups/${POSTGRES_DB}_${TS}.sql.gz"
    echo "[backup] creating $FILE"
    pg_dump -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "$FILE"

    find /backups -type f -name "*.sql.gz" -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
    echo "[backup] done."

    sleep 3600
  fi
  sleep 60
done
