# Cutover helper — verify GCE stack, then delete Cloud SQL and Cloud Run.
# Run AFTER deploy/gce-setup.ps1, gce-deploy.ps1, and manual verification.
#
# Usage:
#   .\deploy\gce-cutover.ps1 -VmIp "34.123.45.67" -VerifyOnly
#   .\deploy\gce-cutover.ps1 -VmIp "34.123.45.67" -Teardown

param(
    [Parameter(Mandatory = $true)]
    [string]$VmIp,
    [switch]$VerifyOnly,
    [switch]$Teardown,
    [string]$Project = "saloon-manager-beta-5640",
    [string]$Region = "asia-south1"
)

$ErrorActionPreference = "Stop"
$BaseUrl = "http://$($VmIp.Trim().TrimEnd('/'))"

function Test-Endpoint {
    param([string]$Url, [string]$Label)
    Write-Host "Checking $Label : $Url"
    $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
    if ($resp.StatusCode -ne 200) {
        throw "$Label returned $($resp.StatusCode)"
    }
    Write-Host "  OK ($($resp.StatusCode))"
}

Write-Host "=== GCE cutover verification ==="
Write-Host "Base URL: $BaseUrl"

Test-Endpoint "$BaseUrl/health" "health"
Test-Endpoint "$BaseUrl/" "frontend home"
Test-Endpoint "$BaseUrl/api/v1/users/stores/" "stores API"

if ($VerifyOnly -or -not $Teardown) {
    Write-Host ""
    Write-Host "Verification passed. To tear down Cloud SQL and Cloud Run:"
    Write-Host "  .\deploy\gce-cutover.ps1 -VmIp `"$VmIp`" -Teardown"
    if (-not $Teardown) { exit 0 }
}

Write-Host ""
Write-Host "=== Teardown billable services (Cloud SQL + Cloud Run) ==="
Write-Host "Project: $Project  Region: $Region"
$confirm = Read-Host "Type DELETE to confirm teardown of saloon-db, saloon-backend, saloon-frontend"
if ($confirm -ne "DELETE") {
    Write-Host "Aborted."
    exit 1
}

gcloud sql instances delete saloon-db --project $Project --quiet
gcloud run services delete saloon-backend saloon-frontend --region $Region --project $Project --quiet

Write-Host ""
Write-Host "=== Cutover complete ==="
Write-Host "Beta URL: $BaseUrl"
Write-Host "Seed if needed: `$env:API_BASE_URL='$BaseUrl'; python populate_preview.py"
