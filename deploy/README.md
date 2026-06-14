# Fresh deployment (manual)

Scripts and configs for redeploying Saloon Manager to GCP Cloud Run.

## Prerequisites

- `gcloud` CLI authenticated to `saloon-manager-beta-5640`
- Fill `deploy/secrets.worksheet` from `secrets.worksheet.example`
- Copy and fill `deploy/backend-env.yaml` from `backend-env.yaml.example`

## Quick deploy (PowerShell)

From repo root, after filling env files:

```powershell
.\deploy\deploy-fresh.ps1
```

## Step-by-step (Cloud Build — no local Docker required)

```powershell
# 1. Build backend
gcloud builds submit --config deploy/cloudbuild-backend.yaml .

# 2. Migrations (Cloud Run Job)
gcloud run jobs create saloon-migrate `
  --image asia-south1-docker.pkg.dev/saloon-manager-beta-5640/saloon-repo/saloon-backend:v1 `
  --region asia-south1 `
  --service-account saloon-run-sa@saloon-manager-beta-5640.iam.gserviceaccount.com `
  --set-cloudsql-instances saloon-manager-beta-5640:asia-south1:saloon-db `
  --env-vars-file deploy/backend-env.yaml `
  --command alembic --args upgrade,head
gcloud run jobs execute saloon-migrate --region asia-south1 --wait

# 3. Deploy backend
gcloud run deploy saloon-backend ...  # see deploy-fresh.ps1

# 4. Build frontend (set _BACKEND_URL to live backend URL)
gcloud builds submit --config deploy/cloudbuild-frontend.yaml --substitutions=_BACKEND_URL=https://YOUR_BACKEND_URL .

# 5. Deploy frontend, then redeploy backend with deploy/backend-env-v2.yaml (CORS)
```

## Live URLs (2026-06-14 fresh deploy)

| Service | URL |
|---------|-----|
| Backend | https://saloon-backend-247064166190.asia-south1.run.app |
| Frontend | https://saloon-frontend-247064166190.asia-south1.run.app |

## GitHub Actions secrets

Set in repo Settings → Secrets → Actions:

- `GCP_PROJECT_ID` = `saloon-manager-beta-5640`
- `GCP_SA_KEY` = JSON key for `github-actions-sa`
- `DATABASE_URL`, `SECRET_KEY`, `CLOUD_SQL_CONNECTION`
- `BACKEND_URL`, `FRONTEND_URL` = live URLs above

Runtime service account `saloon-run-sa` is configured in `.github/workflows/deploy.yml`.
