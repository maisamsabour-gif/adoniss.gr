#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/adoniss/adonis_site}"
BRANCH="${BRANCH:-main}"

cd "$APP_DIR"

echo "[deploy] fetching latest code..."
git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "[deploy] building images..."
docker compose build web

echo "[deploy] running database migrations in one-off container..."
docker compose run --rm web python manage.py migrate --noinput

echo "[deploy] collecting static..."
docker compose run --rm web python manage.py collectstatic --noinput

echo "[deploy] zero-downtime-ish web rollout..."
docker compose up -d --no-deps web

echo "[deploy] reloading nginx..."
docker compose up -d --no-deps nginx

echo "[deploy] done."
