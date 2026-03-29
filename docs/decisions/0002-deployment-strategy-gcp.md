# ADR 0002: Deployment Strategy — GCP Cloud Run (Beta)

## Status
**Proposed** (Pending GCP Account Creation)

## Date
2026-03-29

## Context
The Saloon Manager application has completed Phase 4 (Identity & Security) with all 22 tests passing. The team wants to deploy a **beta version** for the developer and peers to test externally, rather than running everything locally.

### Key Discussion Points

**1. Why GCP Cloud Run?**
- Scale-to-zero = $0 when idle (perfect for beta testing)
- Auto-HTTPS with no SSL certificate management
- Google offers $300 free credit for new accounts
- Simple container-based deployment (no Kubernetes complexity)

**2. Frontend Docker Image**
The user asked: *"Shouldn't I create a Docker image for the application as well?"*
- **Answer**: Yes! We need **two** Docker images:
  - `saloon-backend` — FastAPI app (this is what the Dockerfile in Phase 1 covers)
  - `saloon-frontend` — Next.js app (needs its own Dockerfile in `frontend/`)
- Both will be deployed as separate Cloud Run services and communicate via API calls.

**3. Uvicorn in Production — Is It Slow?**
The user asked: *"Isn't uvicorn a dev thing? Won't it slow down production?"*
- **Answer**: Uvicorn is **production-grade**. It's the recommended ASGI server for FastAPI.
  - In **development** mode (`--reload`), it watches for file changes — this is slow.
  - In **production** mode (no `--reload`), it's highly performant.
  - For Cloud Run specifically, we use **single-worker uvicorn** because Cloud Run handles horizontal scaling by spinning up multiple *container instances*, not multiple workers inside one container.
  - If we ever move away from Cloud Run to a VM or Kubernetes, we'd add `gunicorn` with uvicorn workers for multi-core usage.
- **Decision**: Use `uvicorn` directly in the Dockerfile with no `--reload` flag.

**4. Beta Testing Scope**
- This deployment is for beta testing only — developer + peers
- No need for custom domains yet (use the default `*.run.app` URL)
- Cloud SQL `db-f1-micro` tier is sufficient (shared CPU, minimal cost)
- Auth tokens will use a production-grade `SECRET_KEY` (generated, not hardcoded)

**5. GCP Account**
- The user does not have a GCP account yet
- Step-by-step account creation will be provided before deployment

## Decision
1. Deploy backend and frontend as **separate Cloud Run services**
2. Use **Cloud SQL (PostgreSQL 16)** for the database
3. Use **Artifact Registry** for Docker image storage
4. Use **uvicorn** (single worker, no reload) as the production server
5. Start with the free tier / $300 credit for beta testing
6. CI/CD via GitHub Actions (automated on push to `main`)

## Consequences
- **Cost**: Effectively $0 during beta (free tier + credits)
- **Complexity**: Two Docker images to maintain (backend + frontend)
- **Scalability**: Cloud Run auto-scales, no manual intervention needed
- **Security**: Environment variables via Cloud Run (DATABASE_URL, SECRET_KEY)
