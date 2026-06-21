# GCP Deployment Context

## Current State (beta — stabilized 2026-06)

- **GCP Project**: `saloon-manager-beta-5640`
- **Region**: `asia-south1`
- **Artifact Registry**: `saloon-repo`
- **Cloud SQL**: PostgreSQL instance `saloon-db`, database `saloon`
- **Runtime service account**: `saloon-run-sa@saloon-manager-beta-5640.iam.gserviceaccount.com` (`roles/cloudsql.client`)
- **CI service account**: `github-actions-sa` (push images, deploy Cloud Run)
- **Migrations**: Applied (`alembic upgrade head`)

## Live URLs (canonical)

| Service | URL |
|---------|-----|
| **Backend** | https://saloon-backend-lj4j5kxljq-el.a.run.app |
| **Frontend** | https://saloon-frontend-lj4j5kxljq-el.a.run.app |

Health check: `GET /health` on backend → `{"status":"ok","service":"saloon-manager"}`

## GitHub Secrets (required for CI)

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | `saloon-manager-beta-5640` |
| `GCP_SA_KEY` | `github-actions-sa` JSON key |
| `DATABASE_URL` | Cloud SQL socket URL (see deploy/backend-env.yaml) |
| `SECRET_KEY` | Production JWT secret |
| `CLOUD_SQL_CONNECTION` | `saloon-manager-beta-5640:asia-south1:saloon-db` |
| `BACKEND_URL` | https://saloon-backend-lj4j5kxljq-el.a.run.app |
| `FRONTEND_URL` | https://saloon-frontend-lj4j5kxljq-el.a.run.app |

CI fails if `BACKEND_URL` or `FRONTEND_URL` is missing.

## Beta demo accounts

Created by `populate_preview.py` (beta only — rotate before public launch):

| Role | Email | Password |
|------|-------|----------|
| Owner | `owner@saloon.com` | `password` |
| Customer | `customer@test.com` | `password` |

## Manual redeploy

See [deploy/README.md](../deploy/README.md).

## Beta testing

See [BETA_TEST_CHECKLIST.md](./BETA_TEST_CHECKLIST.md).
