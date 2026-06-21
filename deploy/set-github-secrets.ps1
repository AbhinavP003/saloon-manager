# Set GitHub Actions secrets for Saloon Manager CI/CD
# Requires: GitHub CLI (gh auth login)
# Run from repo root: .\deploy\set-github-secrets.ps1

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "Install GitHub CLI: https://cli.github.com/"
}

$BackendUrl = "https://saloon-backend-lj4j5kxljq-el.a.run.app"
$FrontendUrl = "https://saloon-frontend-lj4j5kxljq-el.a.run.app"

gh secret set GCP_PROJECT_ID --body "saloon-manager-beta-5640"
gh secret set CLOUD_SQL_CONNECTION --body "saloon-manager-beta-5640:asia-south1:saloon-db"
gh secret set BACKEND_URL --body $BackendUrl
gh secret set FRONTEND_URL --body $FrontendUrl

if (Test-Path "deploy/backend-env.yaml") {
    $envContent = Get-Content "deploy/backend-env.yaml" -Raw
    if ($envContent -match "DATABASE_URL:\s*'([^']+)'") {
        gh secret set DATABASE_URL --body $Matches[1]
    }
    if ($envContent -match "SECRET_KEY:\s*'([^']+)'") {
        gh secret set SECRET_KEY --body $Matches[1]
    }
}

if (Test-Path "sa-key.json") {
    gh secret set GCP_SA_KEY < sa-key.json
} else {
    Write-Warning "sa-key.json not found — set GCP_SA_KEY manually in GitHub Settings → Secrets"
}

Write-Host "Secrets updated. Verify at: https://github.com/AbhinavP003/saloon-manager/settings/secrets/actions"
