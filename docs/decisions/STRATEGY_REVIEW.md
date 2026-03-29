# 🏛️ Strategic Review: Architecture & Deployment

## 1. Identity & Security (Phase 4 Focus)
How we handle users (Customers vs. Owners) is the most critical decision for this phase.

### Option A: Custom OAuth2 with JWT (Recommended)
- **Pros**: Zero external cost, full control over the database schema, total control over Role-Based Access Control (RBAC). 
- **Cons**: Requires manually building the login, register, and password reset flows.
- **Decision Factor**: Best if we want to stay "lightweight" and own our data entirely.

### Option B: FastAPI Users (Framework)
- **Pros**: Plug-and-play. Handles registration, email verification, and database persistence out of the box.
- **Cons**: Rigid architecture; customizing the "User" model can sometimes be cumbersome.
- **Decision Factor**: Best if we want to move extremely fast and don't mind following a specific framework pattern.

### Option C: External Provider (Clerk / Auth0)
- **Pros**: Highest security, social logins (Google/Apple) in minutes, beautiful pre-built UIs.
- **Cons**: Financial cost at scale, external dependency (third-party downtime).
- **Decision Factor**: Best if we want the "Premium" feel with minimal backend code.

---

## 2. Deployment Architecture
Where will the saloon marketplace live?

### Option 1: The "Solopreneur" Stack (VPS)
- **Stack**: DigitalOcean / Vultr + Docker Compose.
- **Description**: We deploy the exact same setup we have locally to a cloud server. 
- **Cost**: ~$5-10/month.
- **Verdict**: Best for early-stage startups and keeping costs low.

### Option 2: The "Serverless" PaaS (Platform as a Service)
- **Stack**: Render / Fly.io / Railway.
- **Description**: Connect our GitHub repo; it automatically builds and deploys. 
- **Cost**: Free tier available, then scales by usage.
- **Verdict**: Best for zero-maintenance dev-ops.

---

## 3. Database Strategy
- **Current**: Local PostgreSQL in Docker.
- **Future Recommendation**: Use a **Managed PostgreSQL** (like Neon or AWS RDS) for production. It handles backups and point-in-time recovery automatically so no customer data is ever lost.

---

## 4. Frontend Strategy
- **Vercel**: The undisputed king for Next.js. We should deploy the `frontend/` folder to Vercel for the best speed and SEO (Server-Side Rendering).

---

## ✅ Record of Decisions
*This section is updated as we finalize decisions.*

- **Date**: 2026-03-29
- **Topic**: Phase 4 Strategy
- **Status**: **Decided**
- **Decision**: 🟢 **Custom JWT & OAuth2 (Full Ownership)**.
- **Consensus**: We prioritize data sovereignty and zero external costs for the MVP.
