# Deployment

## GCE single-VM beta (~$0) — recommended

One Always Free e2-micro in `us-central1` runs Postgres + backend + frontend + nginx.

See **[docs/DEPLOY_GCE.md](../docs/DEPLOY_GCE.md)** for full guide.

```powershell
.\deploy\gce-setup.ps1                    # one-time VM create
# SSH to VM, clone repo, copy deploy/.env.gce.example → deploy/.env
.\deploy\gce-deploy.ps1                   # on VM
.\deploy\gce-cutover.ps1 -VmIp "..." -VerifyOnly   # after deploy
.\deploy\gce-cutover.ps1 -VmIp "..." -Teardown     # delete Cloud SQL + Cloud Run
```

CI (`.github/workflows/deploy.yml`) runs **tests only**; deploy manually for beta.

## Neon + Cloud Run (alternative)

Lower ops, Mumbai-friendly Cloud Run region. See [docs/DATABASE_NEON.md](../docs/DATABASE_NEON.md).

```powershell
.\scripts\migrate_neon.ps1
.\deploy\deploy-fresh.ps1
```

## Seed demo data

```powershell
$env:API_BASE_URL = "http://YOUR_VM_IP"   # GCE
# or
$env:API_BASE_URL = "https://saloon-backend-....run.app"   # Cloud Run
python populate_preview.py
```

Demo: `owner@saloon.com` / `password`
