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

## Pending Action (Next Conversation)
The infrastructure is successfully deployed, but the newly provisioned Cloud SQL database is **completely empty** (no schema).

**The immediate next step is to run Database Migrations against the Production Database.**

### Technical Requirements for the Next Step:
1. Connect to the Cloud SQL instance locally (typically via the [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy)).
2. Set the local `DATABASE_URL` environment variable to point to the proxy port using the production credentials.
3. Run `alembic upgrade head` to build the schemas (Users, Stores, Bookings, Services, etc.).
4. Optionally, run the `populate_preview.py` script against production to seed some initial services, hours, or admin accounts for beta testers.
