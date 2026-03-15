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

## 🎨 PHASE 2: Frontend Discovery & Integration (Active)
- [x] **Environment Setup**: Next.js + Tailwind CSS project initialization.
- [x] **Store Discovery UI**: Grid view of saloons with dynamic routing.
- [x] **Service Selection**: Interactive "Menu" view per saloon.
- [x] **Time-Picker Engine**: Visual grid fetching real-time slots from backend.
- [x] **Handshake**: Successful API integration between Next.js and FastAPI.
- [ ] **UX Feedback**: Success/Error "Toasts" and Modal confirmations.
- [ ] **Booking Summary**: Post-booking confirmation screen for customers.

---

## 🚧 PHASE 3: The Booking Life Cycle (In Progress)
- [x] **Availability Logic**: Validation against Store Opening Hours.
- [x] **Slot Discovery Engine**: `GET /slots` logic with 30-min window slicing.
- [x] **Concurrency Control**: SQL-level overlap prevention.
- [x] **Service Integration**: Automatic `end_time` calculation.
- [ ] **Status Workflow (PINNED)**: Transitions (Pending -> Confirmed -> Completed).
- [ ] **Cancellation Policy (PINNED)**: 2-hour buffer logic for user cancellations.
- [ ] **Owner Dashboard UI**: Visualizing daily/weekly schedules for the salon owner.

---

## 🚀 PHASE 4: Identity & Security (Next)
- [ ] **Authentication**: JWT-based Auth (FastAPI Users or Custom OAuth2).
- [ ] **RBAC (Role-Based Access Control)**:
    - **Customer**: View personal booking history.
    - **Store Owner**: Manage services and view private dashboard.
- [ ] **CORS Configuration**: Finalize production security headers.

---

## 💎 PHASE 5: Professional Polish (Future)
- [ ] **Background Tasks**: Email/WhatsApp notifications via Celery/Redis.
- [ ] **Analytics**: Monthly revenue and busy-hour reports for owners.
- [ ] **Image Support**: Upload photos via S3/Cloudinary.
- [ ] **Deployment**: CI/CD pipeline and cloud hosting.