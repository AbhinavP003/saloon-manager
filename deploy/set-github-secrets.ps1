# Set GitHub Actions secrets for Saloon Manager CI/CD
# Requires: GitHub CLI (gh auth login), deploy/backend-env.yaml with Neon URL
# Run from repo root: .\deploy\set-github-secrets.ps1

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "Install GitHub CLI: https://cli.github.com/"
}

$BackendUrl = "https://saloon-backend-lj4j5kxljq-el.a.run.app"
$FrontendUrl = "https://saloon-frontend-lj4j5kxljq-el.a.run.app"

gh secret set GCP_PROJECT_ID --body "saloon-manager-beta-5640"
gh secret set BACKEND_URL --body $BackendUrl
gh secret set FRONTEND_URL --body $FrontendUrl

if (Test-Path "deploy/backend-env.yaml") {
    $envContent = Get-Content "deploy/backend-env.yaml" -Raw
    if ($envContent -match "DATABASE_URL:\s*'([^']+)'") {
        $dbUrl = $Matches[1]
        if ($dbUrl -match "/cloudsql/") {
            Write-Error "deploy/backend-env.yaml still uses Cloud SQL — set Neon URL first (docs/DATABASE_NEON.md)"
        }
        gh secret set DATABASE_URL --body $dbUrl
    }
    if ($envContent -match "SECRET_KEY:\s*'([^']+)'") {
        gh secret set SECRET_KEY --body $Matches[1]
    }
} else {
    Write-Warning "deploy/backend-env.yaml not found — set DATABASE_URL and SECRET_KEY manually"
}

if (Test-Path "sa-key.json") {
    gh secret set GCP_SA_KEY < sa-key.json
} else {
    Write-Warning "sa-key.json not found — set GCP_SA_KEY manually in GitHub Settings → Secrets"
}

Write-Host "Secrets updated (CLOUD_SQL_CONNECTION no longer required)."
Write-Host "Verify at: https://github.com/AbhinavP003/saloon-manager/settings/secrets/actions"
