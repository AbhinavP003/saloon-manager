# Full GCE cutover: ensure VM, Cloud Build images, bootstrap deploy, verify, optional teardown.
#
# Usage:
#   .\deploy\gce-redeploy.ps1
#   .\deploy\gce-redeploy.ps1 -Teardown -ConfirmDelete

param(
    [string]$Project = "saloon-manager-beta-5640",
    [string]$Zone = "us-central1-a",
    [string]$VmName = "saloon-beta-vm",
    [string]$Region = "asia-south1",
    [string]$VmIp = "34.29.107.247",
    [switch]$SkipBuild,
    [switch]$Teardown,
    [switch]$ConfirmDelete
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$Registry = "asia-south1-docker.pkg.dev/${Project}/saloon-repo"
$BackendImage = "${Registry}/saloon-backend:gce"
$FrontendImage = "${Registry}/saloon-frontend:gce"
$BaseUrl = "http://$($VmIp.Trim().TrimEnd('/'))"
$EnvBootstrap = Join-Path $PSScriptRoot ".env.gce.bootstrap"
$BootstrapLf = Join-Path $PSScriptRoot "gce-bootstrap.lf.sh"

function Write-Step($msg) { Write-Host ""; Write-Host "=== $msg ===" -ForegroundColor Cyan }

Write-Step "Ensure VM exists"
& (Join-Path $PSScriptRoot "gce-setup.ps1") -Project $Project -Zone $Zone -VmName $VmName

Write-Step "Grant Artifact Registry read to Compute Engine SA"
$projectNumber = (& gcloud projects describe $Project --format="value(projectNumber)").Trim()
$computeSa = "${projectNumber}-compute@developer.gserviceaccount.com"
& gcloud projects add-iam-policy-binding $Project `
    --member="serviceAccount:$computeSa" `
    --role="roles/artifactregistry.reader" `
    --quiet 2>$null | Out-Null

if (-not $SkipBuild) {
    Write-Step "Cloud Build backend image"
    & gcloud builds submit --project $Project --config (Join-Path $PSScriptRoot "cloudbuild-backend.yaml") `
        --substitutions="_IMAGE=$BackendImage" $RepoRoot

    Write-Step "Cloud Build frontend image (NEXT_PUBLIC_API_URL=$BaseUrl)"
    & gcloud builds submit --project $Project --config (Join-Path $PSScriptRoot "cloudbuild-frontend.yaml") `
        --substitutions="_BACKEND_URL=$BaseUrl,_IMAGE=$FrontendImage" $RepoRoot
}

if (-not (Test-Path $EnvBootstrap)) {
    @"
POSTGRES_USER=admin
POSTGRES_PASSWORD=SaloonBeta2026Gce!
POSTGRES_DB=saloon_db
DATABASE_URL=postgresql+asyncpg://admin:SaloonBeta2026Gce!@db:5432/saloon_db
SECRET_KEY=26a9bf0e63eb7aea4299e55d0b90be05642c122c8b39003405fd0aa607aa0f4d
BACKEND_CORS_ORIGINS=$BaseUrl
NEXT_PUBLIC_API_URL=$BaseUrl
BACKEND_IMAGE=$BackendImage
FRONTEND_IMAGE=$FrontendImage
"@ | Set-Content -Path $EnvBootstrap -Encoding UTF8
} else {
    $content = Get-Content $EnvBootstrap -Raw
    if ($content -notmatch "BACKEND_IMAGE=") {
        Add-Content $EnvBootstrap "`nBACKEND_IMAGE=$BackendImage`nFRONTEND_IMAGE=$FrontendImage"
    }
}

Write-Step "Update VM metadata and reset (bootstrap pull + up)"
$bootstrap = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot "gce-bootstrap.sh")).Replace("`r`n", "`n")
[System.IO.File]::WriteAllText($BootstrapLf, $bootstrap)

& gcloud compute instances add-metadata $VmName --zone $Zone --project $Project `
    --metadata-from-file=startup-script=$BootstrapLf,deploy-env=$EnvBootstrap `
    --metadata=repo-url=https://github.com/AbhinavP003/saloon-manager.git,force-redeploy=1

& gcloud compute instances reset $VmName --zone $Zone --project $Project --quiet

Write-Step "Wait for health at $BaseUrl/health"
$healthy = $false
for ($i = 1; $i -le 40; $i++) {
    Start-Sleep -Seconds 15
    try {
        $r = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 20
        if ($r.StatusCode -eq 200 -and $r.Content -match '"status"\s*:\s*"ok"') {
            Write-Host "Health OK (attempt $i)"
            $healthy = $true
            break
        }
    } catch {
        Write-Host "Attempt $i/40: not ready yet..."
    }
}
if (-not $healthy) {
    throw "GCE stack did not become healthy within timeout. Check: gcloud compute instances get-serial-port-output $VmName --zone $Zone"
}

Write-Step "Verify flows"
$home = Invoke-WebRequest -Uri $BaseUrl -UseBasicParsing -TimeoutSec 20
Write-Host "  home: $($home.StatusCode)"
$stores = Invoke-WebRequest -Uri "$BaseUrl/api/v1/users/stores/" -UseBasicParsing -TimeoutSec 20
Write-Host "  stores API: $($stores.StatusCode), bytes=$($stores.Content.Length)"
if ($stores.Content.Length -lt 10) { throw "Stores list empty — seed may have failed" }

$loginBody = "username=owner@saloon.com&password=password"
$login = Invoke-WebRequest -Uri "$BaseUrl/api/v1/auth/login" -Method POST `
    -ContentType "application/x-www-form-urlencoded" -Body $loginBody -UseBasicParsing -TimeoutSec 20
Write-Host "  owner login: $($login.StatusCode)"

if ($Teardown) {
    if (-not $ConfirmDelete) {
        throw "Pass -ConfirmDelete to delete saloon-db and Cloud Run services"
    }
    Write-Step "Teardown Cloud SQL and Cloud Run"
    & gcloud sql instances delete saloon-db --project $Project --quiet
    & gcloud run services delete saloon-backend saloon-frontend --region $Region --project $Project --quiet
    Write-Host "Billable services deleted."
}

Write-Step "Cutover complete"
Write-Host "Beta URL: $BaseUrl"
Write-Host "Demo login: owner@saloon.com / password"
