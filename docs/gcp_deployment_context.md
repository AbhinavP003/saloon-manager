# GCP Deployment Context

## Current State (beta — Neon Postgres)

- **GCP Project**: `saloon-manager-beta-5640`
- **Region**: `asia-south1`
- **Artifact Registry**: `saloon-repo`
- **Database**: [Neon](https://neon.tech) PostgreSQL (free tier) — see [DATABASE_NEON.md](./DATABASE_NEON.md)
- **Runtime service account**: `saloon-run-sa@saloon-manager-beta-5640.iam.gserviceaccount.com`
- **CI service account**: `github-actions-sa` (push images, deploy Cloud Run)
- **Legacy Cloud SQL** (`saloon-db`): delete after Neon cutover to stop ~$70/mo billing

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
| `DATABASE_URL` | Neon pooled URL with `?ssl=require` |
| `SECRET_KEY` | Production JWT secret |
| `BACKEND_URL` | https://saloon-backend-lj4j5kxljq-el.a.run.app |
| `FRONTEND_URL` | https://saloon-frontend-lj4j5kxljq-el.a.run.app |

CI fails if `BACKEND_URL`, `FRONTEND_URL`, or Cloud SQL-style `DATABASE_URL` is set.

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
