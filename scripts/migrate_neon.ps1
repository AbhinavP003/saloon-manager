# Run Alembic migrations against Neon (or any DATABASE_URL in deploy/backend-env.yaml).
# Usage: .\scripts\migrate_neon.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$envFile = Join-Path $Root "deploy/backend-env.yaml"
if (-not $env:DATABASE_URL -and (Test-Path $envFile)) {
    $content = Get-Content $envFile -Raw
    if ($content -match "DATABASE_URL:\s*'([^']+)'") {
        $env:DATABASE_URL = $Matches[1]
    }
    if ($content -match "SECRET_KEY:\s*'([^']+)'") {
        $env:SECRET_KEY = $Matches[1]
    }
}

if (-not $env:DATABASE_URL) {
    Write-Error "Set DATABASE_URL or create deploy/backend-env.yaml from deploy/backend-env.neon.yaml.example"
}

if ($env:DATABASE_URL -match "/cloudsql/") {
    Write-Error "DATABASE_URL still points at Cloud SQL. Use Neon URL — see docs/DATABASE_NEON.md"
}

Write-Host "Running alembic upgrade head..."
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run alembic upgrade head
} elseif (Test-Path ".venv/Scripts/python.exe") {
    & .venv/Scripts/python.exe -m alembic upgrade head
} else {
    python -m alembic upgrade head
}

Write-Host "Done."
