#!/bin/sh
set -e

PORT="${PORT:-8080}"

echo "[startup] saloon-backend container starting"
echo "[startup] PORT=${PORT}"
echo "[startup] DATABASE_URL set=$([ -n "$DATABASE_URL" ] && echo yes || echo no)"
echo "[startup] SECRET_KEY set=$([ -n "$SECRET_KEY" ] && echo yes || echo no)"

python -c "
from app.main import app
print('[startup] app import succeeded')
" || {
  echo "[startup] FATAL: app import failed"
  exit 1
}

echo "[startup] launching uvicorn on 0.0.0.0:${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
