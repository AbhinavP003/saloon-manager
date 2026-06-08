# 🗺️ Saloon Manager Roadmap

A high-concurrency full-stack application built with FastAPI and Next.js, designed for local saloon marketplaces.

---

## ✅ PHASE 1: Core Infrastructure (Completed)
- [x] **Project Scaffolding**: FastAPI + `uv` for dependency management.
- [x] **Containerization**: Docker-compose setup for PostgreSQL.
- [x] **Database Architecture**: SQLAlchemy 2.0 with Async drivers and Audit Mixins.
- [x] **Migrations**: Alembic integration for version-controlled schema changes.
- [x] **Geospatial Logic**: Store proximity search (Haversine formula).
- [x] **Data Relations**: Store -> Services (One-to-Many) relationship.
- [x] **Seeding System**: Automated scripts for local test environments.
- [x] **Quality Assurance**: Unit testing suite with `pytest` for core logic.

---

## ✅ PHASE 2: Frontend Discovery & Integration (Completed)
- [x] **Environment Setup**: Next.js + Tailwind CSS project initialization.
- [x] **Store Discovery UI**: Grid view of saloons with dynamic routing.
- [x] **Service Selection**: Interactive "Menu" view per saloon.
- [x] **Time-Picker Engine**: Visual grid fetching real-time slots from backend.
- [x] **Handshake**: Successful API integration between Next.js and FastAPI.
- [x] **UX Feedback**: Success/Error toasts via `sonner` across auth, booking, and owner flows.
- [x] **Booking Summary**: Post-booking confirmation screen at `/bookings/[id]/confirmation`.

---

## ✅ PHASE 3: The Booking Life Cycle (Completed)
- [x] **Availability Logic**: Validation against Store Opening Hours.
- [x] **Slot Discovery Engine**: `GET /slots` logic with 30-min window slicing.
- [x] **Concurrency Control**: SQL-level overlap prevention.
- [x] **Service Integration**: Automatic `end_time` calculation.
- [x] **Status Workflow**: Backend logic & transitions (Pending -> Confirmed -> Completed).
- [x] **Cancellation Policy**: 2-hour buffer logic for user cancellations.
- [x] **Owner Dashboard UI**: Premium visual dashboard for salon owners.

---

## ✅ PHASE 4: Identity & Security (Completed)
- [x] **User Models & RBAC**: Database schema and role-based logic.
- [x] **Authentication Core**: JWT-based token issuance and verification backend.
- [x] **Frontend Auth Integration**: Login/Register pages and protected routes.
- [x] **Account Management**: Customer profile and booking history views.
- [x] **CORS Configuration**: Finalize production security headers.

---

## 💎 PHASE 5: Professional Polish (In Progress)
- [ ] **Background Tasks**: Email/WhatsApp notifications via Celery/Redis.
- [x] **Analytics**: Monthly revenue and busy-hour reports for owners.
- [ ] **Image Support**: Upload photos via S3/Cloudinary.
- [x] **Deployment**: CI/CD pipeline (GitHub Actions → GCP Cloud Run). Live deploy pending secrets/migrations — see [docs/GCP_DEPLOYMENT.md](docs/GCP_DEPLOYMENT.md).