# 🗺️ Saloon Manager Roadmap

A high-concurrency backend built with FastAPI, PostgreSQL, and Docker, specifically designed for local saloon marketplaces.

---

## ✅ PHASE 1: Core Infrastructure (Completed)
- [x] **Project Scaffolding**: FastAPI + `uv` for dependency management.
- [x] **Containerization**: Docker-compose setup for PostgreSQL.
- [x] **Database Architecture**: SQLAlchemy 2.0 with Async drivers and Audit Mixins.
- [x] **Migrations**: Alembic integration for version-controlled schema changes.
- [x] **Geospatial Logic**: Store proximity search (Haversine formula) for Kochi/Kakkanad.
- [x] **Data Relations**: Store -> Services (One-to-Many) relationship implementation.
- [x] **Seeding System**: Automated scripts to populate local test environments.
- [x] **Quality Assurance**: Unit testing suite with `pytest` for booking logic.

---

## 🚧 PHASE 2: The Booking Life Cycle (In Progress)
- [x] **Availability Logic**: Validation against Store Opening Hours.
- [x] **Concurrency Control**: SQL-level overlap prevention for time slots.
- [x] **Service Integration**: Automatic `end_time` calculation based on service duration.
- [ ] **Booking Management**: Implement `PATCH` (Reschedule) and `DELETE` (Cancel) endpoints.
- [ ] **Status Workflow**: Transitions from `Pending` -> `Confirmed` -> `Completed`.

---

## 🚀 PHASE 3: Identity & Security (Next)
- [ ] **Authentication**: JWT-based Auth (FastAPI Users or Custom OAuth2).
- [ ] **RBAC (Role-Based Access Control)**:
    - **Customer**: Can book and view their own history.
    - **Store Owner**: Can manage their own services and view dashboard.
    - **Admin**: Can verify new saloons.
- [ ] **CORS Configuration**: Secure the API for frontend (Next.js) integration.

---

## 💎 PHASE 4: Professional Polish (Future)
- [ ] **Background Tasks**: Email/WhatsApp notifications for booking confirmations (using Celery/Redis).
- [ ] **Analytics**: Monthly revenue reports for store owners.
- [ ] **Image Support**: Upload saloon and service photos to S3/Cloudinary.
- [ ] **Deployment**: CI/CD pipeline to Vercel/GCP.

---

## 🛠️ Tech Stack Recap
- **Language**: Python 3.12+
- **Framework**: FastAPI (Asynchronous)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (AsyncSession)
- **Validation**: Pydantic v2
- **Tooling**: `uv`, `ruff`, `alembic`, `pytest`