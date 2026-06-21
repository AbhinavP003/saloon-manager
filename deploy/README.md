# Fresh deployment (manual)

Scripts and configs for redeploying Saloon Manager to GCP Cloud Run with **Neon Postgres**.

## Prerequisites

- `gcloud` CLI authenticated to `saloon-manager-beta-5640`
- Neon database — see [docs/DATABASE_NEON.md](../docs/DATABASE_NEON.md)
- Copy `deploy/backend-env.neon.yaml.example` → `deploy/backend-env.yaml` (gitignored) and fill in

## Quick deploy (PowerShell)

From repo root, after filling env files:

```powershell
.\scripts\migrate_neon.ps1          # schema on Neon
.\deploy\deploy-fresh.ps1           # full stack
# or after backend-env-v2.yaml is ready:
.\deploy\deploy-neon-cutover.ps1    # backend only (Neon cutover)
```

## Live URLs (canonical)

| Service | URL |
|---------|-----|
| Backend | https://saloon-backend-lj4j5kxljq-el.a.run.app |
| Frontend | https://saloon-frontend-lj4j5kxljq-el.a.run.app |

## Seed demo data (production API)

```powershell
$env:API_BASE_URL = "https://saloon-backend-lj4j5kxljq-el.a.run.app"
python populate_preview.py
```

## GitHub Actions secrets

Set in repo Settings → Secrets → Actions (or run `deploy/set-github-secrets.ps1` with `gh` CLI):

- `GCP_PROJECT_ID`, `GCP_SA_KEY`, `DATABASE_URL` (Neon pooled URL), `SECRET_KEY`
- `BACKEND_URL`, `FRONTEND_URL` = live URLs above

`CLOUD_SQL_CONNECTION` is **not used** anymore.

Runtime service account `saloon-run-sa` is configured in `.github/workflows/deploy.yml` (no Cloud SQL attachment).
