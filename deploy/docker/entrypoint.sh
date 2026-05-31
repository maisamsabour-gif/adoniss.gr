#!/usr/bin/env sh
set -e

echo "[entrypoint] waiting for postgres ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
until nc -z "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}"; do
  sleep 1
done
echo "[entrypoint] postgres is up."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn adonis.wsgi:application -c /app/deploy/gunicorn/gunicorn.conf.py
