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
ENV PYTHONUNBUFFERED=1

# Cloud Run injects PORT env variable (default 8080)
ENV PORT=8080

COPY scripts/start.sh /app/start.sh
COPY scripts/start-with-migrate.sh /app/start-with-migrate.sh
RUN sed -i 's/\r$//' /app/start.sh /app/start-with-migrate.sh \
    && chmod +x /app/start.sh /app/start-with-migrate.sh

# Run uvicorn in production mode (no --reload)
CMD ["/app/start.sh"]
