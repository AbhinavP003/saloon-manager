# Testing Suite

This directory contains the automated test suite for the Saloon Manager API. We use `pytest` for unit and integration testing.

## How to Run Tests

Ensure dependencies are synced before running tests:

```bash
uv sync
```

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test Files

```bash
uv run pytest tests/test_bookings.py
```

### Verbose Mode

```bash
uv run pytest -v -s
```

## Test Architecture

- **Framework**: pytest
- **Async support**: pytest-asyncio (required for FastAPI + SQLAlchemy)
- **HTTP client**: httpx via `ASGITransport` (no real network required)
- **Database**: In-memory SQLite via `conftest.py` — tests are isolated and do not touch your local `.env` database

## Core Test Cases

- **Valid bookings**: Confirms that a standard 30-minute service calculates the correct `end_time`
- **Overlap prevention**: Ensures the database blocks two people from booking the same slot
- **Business hours**: Validates that bookings are rejected if the store is closed
- **Data integrity**: Checks that a service cannot be booked at a store it doesn't belong to
- **Auth & RBAC**: JWT login, role checks, and owner-only route protection
- **Status transitions**: Booking lifecycle state machine and cancellation policy
