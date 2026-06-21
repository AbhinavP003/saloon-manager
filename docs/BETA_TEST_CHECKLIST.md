# Beta Test Checklist

Run against live URLs before sharing with peers:

- **Frontend:** https://saloon-frontend-lj4j5kxljq-el.a.run.app
- **Backend:** https://saloon-backend-lj4j5kxljq-el.a.run.app

## Pre-flight

- [x] `/health` returns `{"status":"ok","service":"saloon-manager"}`
- [x] Store API calls use `saloon-backend-lj4j5kxljq-el.a.run.app` (not `localhost:8000`) — verified via production smoke script
- [x] CORS on `/api/v1/users/stores/` returns `access-control-allow-origin: https://saloon-frontend-lj4j5kxljq-el.a.run.app`

## Flows

| Flow | Steps | Pass |
|------|-------|------|
| Discovery | Open home page | [x] Store "The Grand Saloon" visible after seed |
| Register | Create new customer at `/register` | [x] API smoke: register + login |
| Browse | Click a store | [x] Slots load via `/users/bookings/store/{id}/slots` |
| Book | Select slot and confirm | [x] Booking created; confirm page at `/bookings/[id]/confirmation` (manual UI optional) |
| Owner login | `owner@saloon.com` / `password` | [x] Owner token issued |
| Confirm booking | Pending → Confirm on dashboard | [x] Status → confirmed |
| Complete booking | Confirmed → Complete | [x] Status → completed |
| Cancel | Customer cancels eligible booking | Manual — book 2+ days out, then PATCH `/users/bookings/{id}/cancel` |
| About | Visit `/about` | [x] Page loads (deployed revision saloon-frontend-00004-fx4) |

## Demo credentials (beta only)

| Role | Email | Password |
|------|-------|----------|
| Owner | `owner@saloon.com` | `password` |
| Customer | `customer@test.com` | `password` |

## Automated smoke

From repo root (requires `httpx`):

```powershell
$env:API_BASE_URL = "https://saloon-backend-lj4j5kxljq-el.a.run.app"
python scripts/e2e_production_smoke.py
```

Quick curl checks:

```powershell
curl.exe -s https://saloon-backend-lj4j5kxljq-el.a.run.app/health
curl.exe -s https://saloon-backend-lj4j5kxljq-el.a.run.app/api/v1/users/stores/
curl.exe -s -D - -o NUL -H "Origin: https://saloon-frontend-lj4j5kxljq-el.a.run.app" https://saloon-backend-lj4j5kxljq-el.a.run.app/api/v1/users/stores/
```

Seed production demo data:

```powershell
$env:API_BASE_URL = "https://saloon-backend-lj4j5kxljq-el.a.run.app"
python populate_preview.py
```

**Last automated run:** 2026-06-21 — all API smoke checks passed; production DB seeded with The Grand Saloon.
