# 🛡️ Phase 4: Custom Auth Implementation Plan

## Objective
Implement a secure, scalable authentication system using FastAPI and JWT (JSON Web Tokens). This will protect the Store Owner's dashboard and prepare for Customer profiles.

---

## 🛠️ Task 1: Security Foundation
- **Password Hashing**: Use `passlib` with the Argon2 or bcrypt algorithm. **Rule**: Never store a raw password.
- **JWT Provider**: Create a utility to generate tokens with an expiration window (e.g., 30 days).
- **Core Security**: Implement the `OAuth2PasswordBearer` scheme.

## 👥 Task 2: Refined User Model
We will expand our `User` model to support:
- `hashed_password`: Securely stored credentials.
- `role`: (`CUSTOMER`, `OWNER`, `ADMIN`) - This is the key for RBAC.
- `is_active`: For account verification/suspension.
## 🔐 Task 3: RBAC (Role-Based Access Control)
We need custom dependencies to gate specific endpoints:
- `get_current_active_user`: Validates the JWT and ensures the user exists.
- `RoleChecker(["OWNER"])`: Ensures only authorized owners can access `/api/v1/owner/*`.

## 🖥️ Task 4: Frontend Integration
- **Auth Store**: Use `Zustand` or a simple context to store the JWT.
- **Cookies vs LocalStorage**: We will use **HTTP-Only Cookies** for maximum security against XSS (Cross-Site Scripting).
- **Protected Routes**: Next.js middleware to redirect unauthenticated users away from dashboards.

---

## ✅ Deliverables
1. `POST /auth/register`: Signup for owners and customers.
2. `POST /auth/login`: Issue the JWT.
3. `GET /auth/me`: Fetch the profile of the current authenticated user.
