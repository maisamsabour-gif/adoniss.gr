#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/adoniss/adonis_site}"
TARGET_COMMIT="${1:-}"

if [ -z "$TARGET_COMMIT" ]; then
  echo "Usage: ./deploy/scripts/rollback.sh <git-commit-sha>"
  exit 1
fi

cd "$APP_DIR"

echo "[rollback] switching to $TARGET_COMMIT"
git fetch --all
git checkout "$TARGET_COMMIT"

echo "[rollback] rebuilding app image"
docker compose build web

echo "[rollback] starting rolled-back version"
docker compose up -d --no-deps web nginx

echo "[rollback] completed. Consider DB restore if migrations were destructive."
