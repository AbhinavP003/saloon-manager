# Saloon Manager App

A professional FastAPI application for managing saloon bookings, stores, and services.

## 🚀 Overview
Saloon Manager provides a comprehensive platform for:
- Users to discover saloons and book slots autonomously.
- Store Owners to manage their services, hours, and appointments.
- System Admins to manage the entire platform.

---

## 🏗️ Architecture & Development
For a deep dive into our development journey and technical decisions, please refer to our documentation:

### [📜 Development Log](./docs/DEVELOPMENT_LOG.md)
*Chronological history of major changes, features, and fixes.*

### [🏗️ Architecture Decision Records (ADRs)](./docs/decisions/)
*Rationale behind technical choices, major transitions, and design patterns.*

---

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLAlchemy (Async) with SQLite (Testing) and PostgreSQL (Planned)
- **Security**: OAuth2 with JWT, Pydantic-based Role Management
- **Management**: `uv` for dependencies, `alembic` for migrations

## 🛂 Development Guidelines
This project follows strict development rules defined in [`.agent/rules`](./.agent/rules).
Key highlights:
- `uv` is mandatory for dependency management.
- All major decisions must be documented in `docs/decisions/`.
- Tests must maintain high coverage using `pytest`.

---
*Maintained by the Antigravity developer.*
