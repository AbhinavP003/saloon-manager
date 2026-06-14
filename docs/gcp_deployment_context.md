# GCP Deployment Context & Next Steps

## Current State (fresh deploy 2026-06-14)

- **GCP Project**: `saloon-manager-beta-5640`
- **Region**: `asia-south1`
- **Artifact Registry**: `saloon-repo`
- **Cloud SQL**: PostgreSQL instance `saloon-db`, database `saloon`
- **Runtime service account**: `saloon-run-sa@saloon-manager-beta-5640.iam.gserviceaccount.com` (`roles/cloudsql.client`)
- **CI service account**: `github-actions-sa` (push images, deploy Cloud Run)
- **Migrations**: Applied via Cloud Run Job `saloon-migrate` (`alembic upgrade head`)

## Live URLs

| Service | URL |
|---------|-----|
| **Backend** | https://saloon-backend-247064166190.asia-south1.run.app |
| **Frontend** | https://saloon-frontend-247064166190.asia-south1.run.app |

Health check: `GET /health` on backend → `{"status":"ok","service":"saloon-manager"}`

## GitHub Secrets (for CI)

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | `saloon-manager-beta-5640` |
| `GCP_SA_KEY` | `github-actions-sa` JSON key |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:...@/saloon?host=/cloudsql/saloon-manager-beta-5640:asia-south1:saloon-db` |
| `SECRET_KEY` | Production JWT secret (see deploy/backend-env.yaml) |
| `CLOUD_SQL_CONNECTION` | `saloon-manager-beta-5640:asia-south1:saloon-db` |
| `BACKEND_URL` | https://saloon-backend-247064166190.asia-south1.run.app |
| `FRONTEND_URL` | https://saloon-frontend-247064166190.asia-south1.run.app |

## Manual redeploy

See [deploy/README.md](../deploy/README.md) for Cloud Build-based fresh deploy steps.

## Optional next steps

- Seed demo data: run `populate_preview.py` against Cloud SQL via proxy
- Add `/about` page (navbar link currently 404)
- Remove debug instrumentation in `app/core/debug_log.py` once stable
