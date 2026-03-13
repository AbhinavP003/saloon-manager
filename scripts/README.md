🛠️ Database Scripts
This directory contains utility scripts for managing the saloon-manager data environment.

🚀 Setup & Execution
Since this project uses uv for dependency management and Python's module system for imports, follow these steps from the project root directory (saloon-manager/).

1. Initialize Environment
If you haven't already, sync your dependencies and create the virtual environment:

Bash
uv sync
2. Prepare the Database
Ensure your Docker containers are running and your migrations are up to date:

Bash
# Start Docker (if not running)
docker-compose up -d

# Run migrations to create tables
uv run alembic upgrade head
3. Seed the Data
Populate the database with Kochi-based stores, business hours, and services:

Bash
uv run python -m scripts.seed_stores_services
📝 Troubleshooting
ModuleNotFoundError: No module named 'app'
This occurs if you try to run the script directly (e.g., python scripts/seed_stores_services.py).
Solution: Always run from the root using the -m (module) flag:
uv run python -m scripts.seed_stores_services