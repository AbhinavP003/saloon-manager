#!/bin/sh
set -e

PORT="${PORT:-8080}"
PYTHON="/app/.venv/bin/python"

echo "[startup] saloon-backend container starting"
echo "[startup] PORT=${PORT}"
echo "[startup] python=${PYTHON}"
echo "[startup] DATABASE_URL set=$([ -n "$DATABASE_URL" ] && echo yes || echo no)"
echo "[startup] SECRET_KEY set=$([ -n "$SECRET_KEY" ] && echo yes || echo no)"

if [ -n "$DATABASE_URL" ]; then
  echo "[startup] DATABASE_URL scheme=$(printf '%s' "$DATABASE_URL" | cut -d: -f1)"
fi

"$PYTHON" -c "
import traceback, sys
try:
    from app.main import app
    print('[startup] app import succeeded')
except Exception:
    traceback.print_exc()
    sys.exit(1)
" || {
  echo "[startup] FATAL: app import failed"
  exit 1
}

echo "[startup] launching uvicorn on 0.0.0.0:${PORT}"
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
