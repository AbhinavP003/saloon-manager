# GCP Deployment Context & Next Steps

## Current State
- **GCP Project**: `saloon-manager-beta-5640`
- **APIs Enabled**: Cloud Run, Cloud SQL, Artifact Registry, Cloud Build.
- **Artifact Registry**: `saloon-repo` created in `asia-south1`.
- **Database**: 
  - Managed PostgreSQL 15 instance: `saloon-db`.
  - Application database: `saloon` created inside it.
- **Service Account**: `github-actions-sa`. It has been granted all roles required to push Docker images and deploy to Cloud Run securely.
- **GitHub Secrets**: Added dummy variables for tests in `deploy.yml`. Ensured strict quoting for image tags to prevent parsing errors due to trailing spaces in secrets.
- **Live URLs**:
  - **Frontend**: https://saloon-frontend-lj4j5kxljq-el.a.run.app
  - **Backend**: https://saloon-backend-lj4j5kxljq-el.a.run.app

## Pending Action

The infrastructure is deployed, but the Cloud SQL database may be **empty** (no schema) until migrations run.

**Next step:** Follow [GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md) §6 to run `alembic upgrade head` against production.

**Frontend fix (2026-06):** The frontend now reads `NEXT_PUBLIC_API_URL` at build time. Re-deploy the frontend after setting the `BACKEND_URL` GitHub secret so API calls target the live backend instead of `localhost:8000`.
