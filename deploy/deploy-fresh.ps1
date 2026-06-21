# Fresh deployment helper — run from repo root after filling deploy/backend-env.yaml
# Requires: gcloud CLI, Neon DATABASE_URL in deploy/backend-env.yaml
# See docs/DATABASE_NEON.md

$ErrorActionPreference = "Stop"
$Project = "saloon-manager-beta-5640"
$Region = "asia-south1"
$Gcloud = "gcloud"

function Require-File($path) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path"
    }
}

Require-File "deploy/backend-env.yaml"
$envContent = Get-Content "deploy/backend-env.yaml" -Raw
if ($envContent -match "/cloudsql/") {
    throw "Use Neon DATABASE_URL in deploy/backend-env.yaml — see docs/DATABASE_NEON.md"
}

Write-Host "=== Create saloon-run-sa (if missing) ==="
$sa = "saloon-run-sa@${Project}.iam.gserviceaccount.com"
$exists = & $Gcloud iam service-accounts list --filter="email:saloon-run-sa" --format="value(email)" 2>$null
if (-not $exists) {
    & $Gcloud iam service-accounts create saloon-run-sa --display-name="Saloon Cloud Run Runtime"
}

Write-Host "=== Build backend image (Cloud Build) ==="
& $Gcloud builds submit --config deploy/cloudbuild-backend.yaml .

Write-Host "=== Run migrations (Cloud Run Job, Neon URL) ==="
$image = "asia-south1-docker.pkg.dev/${Project}/saloon-repo/saloon-backend:v1"
& $Gcloud run jobs delete saloon-migrate --region $Region --quiet 2>$null
& $Gcloud run jobs create saloon-migrate `
    --image $image `
    --region $Region `
    --service-account $sa `
    --env-vars-file deploy/backend-env.yaml `
    --command "alembic" `
    --args "upgrade,head" `
    --max-retries 0 `
    --task-timeout 10m
& $Gcloud run jobs execute saloon-migrate --region $Region --wait

Write-Host "=== Deploy backend ==="
& $Gcloud run deploy saloon-backend `
    --image $image `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --service-account $sa `
    --env-vars-file deploy/backend-env.yaml

$backendUrl = (& $Gcloud run services describe saloon-backend --region $Region --format="value(status.url)").Trim()
Write-Host "BACKEND_URL=$backendUrl"

Write-Host "=== Build and deploy frontend ==="
& $Gcloud builds submit --config deploy/cloudbuild-frontend.yaml --substitutions="_BACKEND_URL=$backendUrl" .
$frontendImage = "asia-south1-docker.pkg.dev/${Project}/saloon-repo/saloon-frontend:v1"
& $Gcloud run deploy saloon-frontend `
    --image $frontendImage `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 3000

$frontendUrl = (& $Gcloud run services describe saloon-frontend --region $Region --format="value(status.url)").Trim()
Write-Host "FRONTEND_URL=$frontendUrl"

Write-Host "=== Update backend CORS ==="
Require-File "deploy/backend-env-v2.yaml"
& $Gcloud run deploy saloon-backend `
    --image $image `
    --region $Region `
    --service-account $sa `
    --env-vars-file deploy/backend-env-v2.yaml

Write-Host "=== Done ==="
Write-Host "Backend:  $backendUrl/health"
Write-Host "Frontend: $frontendUrl"
Write-Host "Seed: `$env:API_BASE_URL='$backendUrl'; python populate_preview.py"
