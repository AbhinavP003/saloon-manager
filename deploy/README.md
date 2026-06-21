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

## Live URLs (canonical)

| Service | URL |
|---------|-----|
| Backend | https://saloon-backend-lj4j5kxljq-el.a.run.app |
| Frontend | https://saloon-frontend-lj4j5kxljq-el.a.run.app |

## Seed demo data (production API)

```powershell
$env:API_BASE_URL = "https://saloon-backend-lj4j5kxljq-el.a.run.app"
uv run python populate_preview.py
```

## GitHub Actions secrets

Set in repo Settings → Secrets → Actions (or run `deploy/set-github-secrets.ps1` with `gh` CLI):

- `GCP_PROJECT_ID`, `GCP_SA_KEY`, `DATABASE_URL`, `SECRET_KEY`, `CLOUD_SQL_CONNECTION`
- `BACKEND_URL`, `FRONTEND_URL` = live URLs above

Runtime service account `saloon-run-sa` is configured in `.github/workflows/deploy.yml`.
