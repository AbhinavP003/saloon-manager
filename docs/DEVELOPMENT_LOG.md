# Development Log

## 2026-03-29: Security Migration & Test Stabilization
- **Feature**: Completed Phase 4 (Identity & Security).
- **Core Changes**:
    - Implemented JWT authentication and SQLAlchemy-based user storage.
    - Created `RoleChecker` for authorization on store/booking status routes.
    - Updated `Booking` model to link to `User` accounts (optional).
- **Friction Points & Resolutions**:
    - **Pydantic Validation Bugs**: Fixed `ResponseValidationError` by separating nested "Short" schemas from full schemas to prevent circular lazy-loading in SQLAlchemy.
    - **Test Regressions**: Migrated all Phase 3 tests to use the new `Authorization` headers and `conftest.py` fixtures.
    - **Environment Issues**: Added `pydantic[email]` (email-validator) to handle `EmailStr` fields.
- **Architectural Decisions**:
    - Defined a clear separation between Public, User, Owner, and Admin namespaces in the API.
    - Chose to use `expire_on_commit=False` globally to improve compatibility with async Pydantic serialization.
- **Next steps**: Phase 5 (Professional Polish) – Background Tasks (Celery/Redis) and Notifications.

---
*Created by [Antigravity] as per project guidelines.*
