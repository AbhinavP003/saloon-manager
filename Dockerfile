# ============================================================
# Stage 1: Builder — Install dependencies with uv
# ============================================================
FROM python:3.12-slim AS builder

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (Docker layer caching)
COPY pyproject.toml uv.lock ./

# Install production dependencies only (no dev group)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application source code
COPY app/ app/
COPY alembic.ini ./
COPY migrations/ migrations/

# ============================================================
# Stage 2: Runtime — Lean production image
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/app /app/app
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/migrations /app/migrations

# Put the venv's bin directory on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Cloud Run injects PORT env variable (default 8080)
ENV PORT=8080

# Run uvicorn in production mode (no --reload)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
