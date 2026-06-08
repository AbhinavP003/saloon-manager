# GCP Deployment Guide

Step-by-step instructions to deploy Saloon Manager to Google Cloud Run. The CI/CD pipeline in [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) automates builds on every push to `main` once secrets are configured.

## Prerequisites

- A [Google Cloud](https://cloud.google.com/) account (free tier + $300 trial credit)
- `gcloud` CLI installed locally
- GitHub repository with Actions enabled
- Docker installed locally (optional, for manual builds)

## 1. Create GCP Project

```bash
gcloud projects create saloon-manager-beta --name="Saloon Manager Beta"
gcloud config set project saloon-manager-beta
```

Enable required APIs:

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

## 2. Artifact Registry

```bash
gcloud artifacts repositories create saloon-repo \
  --repository-format=docker \
  --location=asia-south1 \
  --description="Saloon Manager Docker images"
```

## 3. Cloud SQL (PostgreSQL)

```bash
gcloud sql instances create saloon-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=asia-south1

gcloud sql databases create saloon --instance=saloon-db
gcloud sql users create saloon_user \
  --instance=saloon-db \
  --password=YOUR_SECURE_PASSWORD
```

Note the connection name:

```bash
gcloud sql instances describe saloon-db --format="value(connectionName)"
# e.g. saloon-manager-beta:asia-south1:saloon-db
```

## 4. Service Account for GitHub Actions

```bash
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Deployer"

# Grant deploy permissions
gcloud projects add-iam-policy-binding saloon-manager-beta \
  --member="serviceAccount:github-actions-sa@saloon-manager-beta.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding saloon-manager-beta \
  --member="serviceAccount:github-actions-sa@saloon-manager-beta.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding saloon-manager-beta \
  --member="serviceAccount:github-actions-sa@saloon-manager-beta.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key (store securely — add to GitHub Secrets)
gcloud iam service-accounts keys create gcp-sa-key.json \
  --iam-account=github-actions-sa@saloon-manager-beta.iam.gserviceaccount.com
```

## 5. GitHub Secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | Full JSON contents of `gcp-sa-key.json` |
| `DATABASE_URL` | `postgresql+asyncpg://saloon_user:PASSWORD@/saloon?host=/cloudsql/PROJECT:REGION:saloon-db` |
| `SECRET_KEY` | Generate with `openssl rand -hex 32` |
| `CLOUD_SQL_CONNECTION` | `PROJECT:REGION:saloon-db` |
| `BACKEND_URL` | Set after first backend deploy (e.g. `https://saloon-backend-xxx.a.run.app`) |
| `FRONTEND_URL` | Frontend Cloud Run URL for CORS (e.g. `https://saloon-frontend-xxx.a.run.app`) |

After the first backend deploy, update `BACKEND_URL` so the frontend build bakes in the correct API URL via `NEXT_PUBLIC_API_URL`.

## 6. Run Database Migrations (Production)

Cloud SQL starts empty. Run migrations before the app can serve traffic.

### Option A: Cloud SQL Auth Proxy (recommended)

```bash
# Download proxy: https://cloud.google.com/sql/docs/postgres/sql-proxy
cloud-sql-proxy PROJECT:REGION:saloon-db --port 5433
```

In another terminal:

```bash
export DATABASE_URL="postgresql+asyncpg://saloon_user:PASSWORD@127.0.0.1:5433/saloon"
uv run alembic upgrade head

# Optional: seed demo data
uv run python populate_preview.py
```

### Option B: One-off Cloud Run Job

Build a migration image from the backend Dockerfile and run `alembic upgrade head` as a Cloud Run Job with the Cloud SQL socket mounted.

## 7. Configure CORS for Production

Update the backend Cloud Run service to allow your frontend origin:

```bash
gcloud run services update saloon-backend \
  --region asia-south1 \
  --set-env-vars "BACKEND_CORS_ORIGINS=https://saloon-frontend-xxx.a.run.app"
```

The backend reads `BACKEND_CORS_ORIGINS` as a comma-separated list (see [`app/core/config.py`](../app/core/config.py)).

## 8. Verify Deployment

After pushing to `main`:

1. GitHub Actions runs `pytest` then deploys backend and frontend
2. Open the frontend Cloud Run URL
3. Confirm store discovery loads data from the backend
4. Test login, booking, and owner dashboard flows

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Container failed to start on PORT 8080 | Ensure all env vars are set together (`DATABASE_URL`, `SECRET_KEY`, `BACKEND_CORS_ORIGINS`). Do **not** pass multiple `--set-env-vars` flags — gcloud keeps only the last one. Use `--env-vars-file` instead. |
| Frontend calls `localhost:8000` | Rebuild frontend with `BACKEND_URL` secret set; `NEXT_PUBLIC_API_URL` is baked at build time |
| CORS errors | Add frontend URL to `BACKEND_CORS_ORIGINS` on backend |
| 500 errors on API | Run `alembic upgrade head` against production DB |
| Auth failures | Ensure `SECRET_KEY` is set consistently on backend |

## Current Infrastructure Notes

See [`docs/gcp_deployment_context.md`](./gcp_deployment_context.md) for the live beta environment (project `saloon-manager-beta-5640`) and pending migration step.
