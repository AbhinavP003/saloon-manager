# Database: Neon (free-tier Postgres)

Production beta uses **Neon** instead of Cloud SQL (~$0/month vs ~$70/month).

- **Compute:** Cloud Run (backend + frontend) on GCP
- **Database:** Neon PostgreSQL over TLS (no Cloud SQL socket)

## 1. Create Neon project

1. Sign up at [https://neon.tech](https://neon.tech) (free plan, no credit card).
2. Create a project — pick a region close to `asia-south1` (e.g. **AWS Singapore** `ap-southeast-1`).
3. Open **Connection details** → copy the **pooled** connection string (host contains `-pooler`).

Convert to async SQLAlchemy format:

```
postgresql+asyncpg://USER:PASSWORD@ep-xxxx-pooler.ap-southeast-1.aws.neon.tech/neondb?ssl=require
```

Neon may give `postgresql://` — the app auto-converts to `postgresql+asyncpg://`.

## 2. Local env files (gitignored)

Copy examples and paste your Neon URL:

```powershell
Copy-Item deploy/backend-env.neon.yaml.example deploy/backend-env.yaml
# Edit DATABASE_URL, SECRET_KEY, BACKEND_CORS_ORIGINS
Copy-Item deploy/backend-env.neon.yaml.example deploy/backend-env-v2.yaml
# Set BACKEND_CORS_ORIGINS to your live frontend URL
```

## 3. Migrate schema

From repo root:

```powershell
.\scripts\migrate_neon.ps1
```

Or manually:

```powershell
$env:DATABASE_URL = "postgresql+asyncpg://...@ep-xxx-pooler.../neondb?ssl=require"
$env:SECRET_KEY = "your-secret"
uv run alembic upgrade head
```

## 4. Seed demo data

```powershell
$env:API_BASE_URL = "https://saloon-backend-lj4j5kxljq-el.a.run.app"  # after backend redeploy
# Or against local backend:
# $env:API_BASE_URL = "http://localhost:8000"
python populate_preview.py
```

## 5. GitHub Actions secrets

Update in **Settings → Secrets → Actions** (or `.\deploy\set-github-secrets.ps1` after filling `deploy/backend-env.yaml`):

| Secret | Value |
|--------|-------|
| `DATABASE_URL` | Neon pooled URL with `?ssl=require` |
| `SECRET_KEY` | Same as backend env |
| `BACKEND_URL` / `FRONTEND_URL` | Cloud Run URLs (unchanged) |
| ~~`CLOUD_SQL_CONNECTION`~~ | **Remove** — no longer used |

## 6. Redeploy backend

Push to `main` (CI deploys without `--add-cloudsql-instances`) or run:

```powershell
.\deploy\deploy-neon-cutover.ps1
```

## 7. Stop Cloud SQL billing

After verifying `/health` and store list on production:

```powershell
gcloud sql instances delete saloon-db --project saloon-manager-beta-5640
```

Confirm in [GCP Billing](https://console.cloud.google.com/billing) that Cloud SQL charges stop.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `SSL required` | Add `?ssl=require` to `DATABASE_URL` |
| Cold start ~500ms | Normal — Neon scales to zero after idle |
| CI fails on Cloud SQL URL | Update `DATABASE_URL` secret to Neon URL |
| Empty store list | Run `populate_preview.py` against production API |

## Free tier limits (Neon)

- 0.5 GB storage per project
- 100 compute-hours/month (enough for sporadic beta testing)
- Scales to zero after ~5 minutes idle

See [Neon pricing](https://neon.com/pricing) for limits and upgrades.
