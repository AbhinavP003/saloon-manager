# Redeploy backend to Cloud Run using Neon (no Cloud SQL attachment).
# Prerequisites: deploy/backend-env-v2.yaml filled with Neon DATABASE_URL + CORS.
# Run from repo root: .\deploy\deploy-neon-cutover.ps1

$ErrorActionPreference = "Stop"
$Project = "saloon-manager-beta-5640"
$Region = "asia-south1"
$Image = "asia-south1-docker.pkg.dev/${Project}/saloon-repo/saloon-backend:v1"
$Sa = "saloon-run-sa@${Project}.iam.gserviceaccount.com"

function Require-File($path) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path (copy from deploy/backend-env.neon.yaml.example)"
    }
}

Require-File "deploy/backend-env-v2.yaml"
$content = Get-Content "deploy/backend-env-v2.yaml" -Raw
if ($content -match "/cloudsql/") {
    throw "deploy/backend-env-v2.yaml still uses Cloud SQL socket — set Neon DATABASE_URL first"
}

Write-Host "=== Build backend image ==="
gcloud builds submit --config deploy/cloudbuild-backend.yaml --project $Project .

Write-Host "=== Deploy backend (Neon, no Cloud SQL) ==="
gcloud run deploy saloon-backend `
    --image $Image `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --service-account $Sa `
    --env-vars-file deploy/backend-env-v2.yaml `
    --project $Project

$backendUrl = (gcloud run services describe saloon-backend --region $Region --project $Project --format="value(status.url)").Trim()
Write-Host "Backend: $backendUrl/health"
Write-Host "Next: run populate_preview.py if DB is empty, then delete Cloud SQL saloon-db to stop billing."
