#!/bin/sh
set -e

PORT="${PORT:-8080}"
PYTHON="/app/.venv/bin/python"

echo "[startup] saloon-backend container starting (with migrations)"
echo "[startup] PORT=${PORT}"

if [ -n "$DATABASE_URL" ]; then
  echo "[startup] running alembic upgrade head"
  /app/.venv/bin/alembic upgrade head
else
  echo "[startup] WARNING: DATABASE_URL not set — skipping migrations"
fi

exec /app/start.sh
