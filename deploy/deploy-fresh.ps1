# Fresh deployment helper — run from repo root after filling deploy/backend-env.yaml
# Requires: gcloud CLI, authenticated to saloon-manager-beta-5640

$ErrorActionPreference = "Stop"
$Project = "saloon-manager-beta-5640"
$Region = "asia-south1"
$Gcloud = "gcloud"

function Require-File($path) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path"
    }
}

Write-Host "=== Phase 2: Delete old Cloud Run services ==="
& $Gcloud run services delete saloon-backend --region $Region --quiet 2>$null
& $Gcloud run services delete saloon-frontend --region $Region --quiet 2>$null

Write-Host "=== Phase 3: Create saloon-run-sa (if missing) ==="
$sa = "saloon-run-sa@${Project}.iam.gserviceaccount.com"
$exists = & $Gcloud iam service-accounts list --filter="email:saloon-run-sa" --format="value(email)" 2>$null
if (-not $exists) {
    & $Gcloud iam service-accounts create saloon-run-sa --display-name="Saloon Cloud Run Runtime"
    & $Gcloud projects add-iam-policy-binding $Project `
        --member="serviceAccount:$sa" `
        --role="roles/cloudsql.client" `
        --quiet
}

Write-Host "=== Phase 5: Build backend image (Cloud Build) ==="
& $Gcloud builds submit --config deploy/cloudbuild-backend.yaml .

Write-Host "=== Phase 4: Run migrations (Cloud Run Job) ==="
$image = "asia-south1-docker.pkg.dev/${Project}/saloon-repo/saloon-backend:v1"
Require-File "deploy/backend-env.yaml"
& $Gcloud run jobs delete saloon-migrate --region $Region --quiet 2>$null
& $Gcloud run jobs create saloon-migrate `
    --image $image `
    --region $Region `
    --service-account $sa `
    --set-cloudsql-instances "${Project}:${Region}:saloon-db" `
    --env-vars-file deploy/backend-env.yaml `
    --command "alembic" `
    --args "upgrade,head" `
    --max-retries 0 `
    --task-timeout 10m
& $Gcloud run jobs execute saloon-migrate --region $Region --wait

Write-Host "=== Phase 6: Deploy backend ==="
& $Gcloud run deploy saloon-backend `
    --image $image `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --service-account $sa `
    --add-cloudsql-instances "${Project}:${Region}:saloon-db" `
    --env-vars-file deploy/backend-env.yaml

$backendUrl = (& $Gcloud run services describe saloon-backend --region $Region --format="value(status.url)").Trim()
Write-Host "BACKEND_URL=$backendUrl"

Write-Host "=== Phase 7: Build and deploy frontend ==="
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

Write-Host "=== Phase 8: Update backend CORS ==="
Require-File "deploy/backend-env-v2.yaml"
& $Gcloud run deploy saloon-backend `
    --image $image `
    --region $Region `
    --service-account $sa `
    --add-cloudsql-instances "${Project}:${Region}:saloon-db" `
    --env-vars-file deploy/backend-env-v2.yaml

Write-Host "=== Done ==="
Write-Host "Backend:  $backendUrl/health"
Write-Host "Frontend: $frontendUrl"
