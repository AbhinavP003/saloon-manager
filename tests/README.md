🧪 Testing Suite
This directory contains the automated test suite for the Saloon Manager API. We use pytest for unit and integration testing.

🚀 How to Run Tests
Ensure your virtual environment is active and dependencies are synced before running tests.

1. Run All Tests
To execute every test in the suite:

Bash
uv run pytest
2. Run Specific Test Files
If you only want to test the booking logic:

Bash
uv run pytest tests/test_bookings.py
3. See Print Statements (Verbose Mode)
To see print() outputs and detailed pass/fail logs:

Bash
uv run pytest -v -s
🛠️ Test Architecture
Framework: pytest

Async Support: pytest-asyncio (required for FastAPI + SQLAlchemy)

HTTP Client: httpx (used to make requests to the app during testing)

Core Test Cases:
Valid Bookings: Confirms that a standard 30-minute service calculates the correct end_time.

Overlap Prevention: Ensures the database blocks two people from booking the same slot.

Business Hours: Validates that bookings are rejected if the store is closed (e.g., late night or days off).

Data Integrity: Checks that a service cannot be booked at a store it doesn't belong to.

⚠️ Database Note
Currently, these tests run against the active database defined in your .env.

Warning: Running tests may modify your seeded data. In a future update, we will implement a conftest.py to use a temporary "in-memory" or "test-only" database.