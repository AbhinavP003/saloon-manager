# GCE single-VM beta deployment (~$0/month)

Run Saloon Manager on one **Always Free e2-micro** VM in `us-central1` with Postgres, backend, frontend, and nginx in Docker Compose. Replaces Cloud Run + Cloud SQL (~$75/mo) for beta traffic.

## Cost comparison

| Approach | Monthly cost (beta) |
|----------|---------------------|
| Cloud Run + Cloud SQL `db-custom-1-3840` | ~$75 |
| Two GCE VMs (app + DB) | ~$12–25+ (only one e2-micro is Always Free) |
| Cloud SQL `db-f1-micro` + compute | ~$7–15+ (no Always Free tier) |
| **One e2-micro + Postgres in Docker** | **~$0** (Always Free in us-central1) |
| Cloud Run + Neon (see [DATABASE_NEON.md](./DATABASE_NEON.md)) | ~$0–8 |

**Always Free (relevant):**

- 1× e2-micro/month in `us-west1`, `us-central1`, or `us-east1`
- 30 GB standard persistent disk
- 1 GB/month egress (North America)

**Not free:** second VM, Cloud SQL, unused reserved static IPs, heavy egress.

**Trade-off:** US region latency for India testers; manual ops vs managed Cloud Run.

## Architecture

```
Browser → nginx:80 → frontend:3000
                  → /api/* → backend:8080 → postgres:5432 (Docker network)
```

Files:

| File | Purpose |
|------|---------|
| [deploy/docker-compose.prod.yml](../deploy/docker-compose.prod.yml) | Production stack |
| [deploy/nginx.conf](../deploy/nginx.conf) | Reverse proxy |
| [deploy/.env.gce.example](../deploy/.env.gce.example) | Env template (copy to `deploy/.env`) |
| [deploy/gce-setup.ps1](../deploy/gce-setup.ps1) | One-time VM provisioning |
| [deploy/gce-deploy.ps1](../deploy/gce-deploy.ps1) | Build & release on VM |
| [scripts/start-with-migrate.sh](../scripts/start-with-migrate.sh) | Alembic on backend boot |

## RAM on e2-micro (1 GB)

Postgres + FastAPI + Next.js can exceed 1 GB. Mitigations included in setup:

1. **2 GB swap** on the VM ([deploy/gce-startup.sh](../deploy/gce-startup.sh))
2. Postgres tuned low (`shared_buffers=128MB`, `max_connections=20`)
3. Docker `mem_limit` on services in compose
4. Fallback: **e2-small (~$12/mo)** if OOM persists

## First-time setup

### 1. Provision VM (local machine with `gcloud`)

```powershell
# Optional: restrict SSH to your IP
.\deploy\gce-setup.ps1 -MyIp "YOUR.PUBLIC.IP/32"
```

Note the **static external IP** printed at the end.

### 2. SSH and clone repo

```powershell
gcloud compute ssh saloon-beta-vm --zone us-central1-a --project saloon-manager-beta-5640
```

On the VM:

```bash
git clone https://github.com/YOUR_ORG/saloon-manager.git ~/saloon-manager
cd ~/saloon-manager
cp deploy/.env.gce.example deploy/.env
```

Edit `deploy/.env`:

- Set `POSTGRES_PASSWORD` and matching password in `DATABASE_URL`
- Set `SECRET_KEY` (`openssl rand -hex 32`)
- Replace `YOUR_VM_IP` with the VM static IP in `BACKEND_CORS_ORIGINS` and `NEXT_PUBLIC_API_URL`

Example:

```
BACKEND_CORS_ORIGINS=http://34.123.45.67
NEXT_PUBLIC_API_URL=http://34.123.45.67
```

`NEXT_PUBLIC_API_URL` is the **base URL only** — the frontend appends `/api/v1`.

### 3. Deploy

On the VM (install PowerShell if needed, or use docker directly):

```powershell
.\deploy\gce-deploy.ps1
```

Or manually:

```bash
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d --build
```

Migrations run automatically via `start-with-migrate.sh` on backend start.

### 4. Seed demo data

```powershell
$env:API_BASE_URL = "http://YOUR_VM_IP"
python populate_preview.py
```

Or:

```powershell
.\deploy\gce-deploy.ps1 -Seed
```

Demo login: `owner@saloon.com` / `password`

### 5. Verify

- Home: `http://YOUR_VM_IP`
- Health: `http://YOUR_VM_IP/health`
- Stores API: `http://YOUR_VM_IP/api/v1/users/stores/`
- Book a service, owner dashboard, booking confirmation

## Release deploys

On the VM after `git pull`:

```powershell
.\deploy\gce-deploy.ps1
```

From your laptop (repo already on VM):

```powershell
.\deploy\gce-deploy.ps1 -Remote
```

CI runs **tests only** on push to `main`; deploy manually for beta (see [.github/workflows/deploy.yml](../.github/workflows/deploy.yml)).

## Cutover from Cloud Run + Cloud SQL

Execute **after** GCE stack is verified:

### 1. Confirm GCE works

- Frontend loads at VM IP
- Booking flow works end-to-end
- Owner login works

### 2. Stop billable GCP services

```powershell
$Project = "saloon-manager-beta-5640"
$Region = "asia-south1"

# Cloud SQL (~$70/mo)
gcloud sql instances delete saloon-db --project $Project --quiet

# Cloud Run services
gcloud run services delete saloon-backend saloon-frontend --region $Region --project $Project --quiet
```

Optional cleanup (if no longer needed):

```powershell
gcloud artifacts repositories delete saloon-repo --location $Region --project $Project --quiet
```

### 3. Update docs / bookmarks

Point beta testers to `http://YOUR_VM_IP` (or your domain). HTTPS requires Caddy/Let's Encrypt or Cloudflare — HTTP-only is fine for closed beta.

## HTTPS (optional)

For production-like beta, add Caddy in front or replace nginx with Caddy for automatic Let's Encrypt. Not required for initial cutover.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| OOM / containers restarting | Check `free -h` and swap; consider e2-small |
| 502 from nginx | `docker compose -f deploy/docker-compose.prod.yml logs backend frontend` |
| CORS errors | `BACKEND_CORS_ORIGINS` must match browser origin exactly |
| Empty stores | Run `populate_preview.py` with `API_BASE_URL=http://VM_IP` |
| Migrations failed | `docker compose exec backend alembic upgrade head` |

## Alternatives

- **[DATABASE_NEON.md](./DATABASE_NEON.md)** — Neon + Cloud Run (~$0, Mumbai-friendly, less ops)
- **[GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md)** — Original Cloud Run docs (legacy)

Both paths can coexist in the repo; GCE single-VM is the default for **all-in-GCP ~$0 beta**.
