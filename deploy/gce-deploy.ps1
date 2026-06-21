# Deploy Saloon Manager to the GCE VM via Docker Compose.
# Run from repo root on the VM (or locally with -Remote via gcloud ssh).
#
# Usage (on VM):
#   cp deploy/.env.gce.example deploy/.env   # first time only
#   .\deploy\gce-deploy.ps1
#
# Usage (from local machine):
#   .\deploy\gce-deploy.ps1 -Remote -VmName saloon-beta-vm -Zone us-central1-a

param(
    [switch]$Remote,
    [string]$VmName = "saloon-beta-vm",
    [string]$Zone = "us-central1-a",
    [string]$Project = "saloon-manager-beta-5640",
    [switch]$Seed,
    [switch]$SkipPull
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$EnvFile = Join-Path $RepoRoot "deploy\.env"
$ComposeFile = Join-Path $RepoRoot "deploy\docker-compose.prod.yml"

function Require-File($path, $hint) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path — $hint"
    }
}

function Get-PublicBaseUrl {
    param([hashtable]$Vars)
    $url = $Vars["NEXT_PUBLIC_API_URL"]
    if (-not $url) {
        throw "NEXT_PUBLIC_API_URL not set in deploy/.env"
    }
    return $url.Trim().TrimEnd("/")
}

function Invoke-DeployOnHost {
    param([string]$WorkDir)

    Push-Location $WorkDir
    try {
        if (-not $SkipPull) {
            if (Test-Path ".git") {
                Write-Host "=== git pull ==="
                git pull --ff-only
            }
        }

        Require-File "deploy\.env" "copy deploy/.env.gce.example to deploy/.env and fill secrets"
        Require-File "deploy\docker-compose.prod.yml" "ensure deploy files exist"

        Write-Host "=== docker compose build & up ==="
        docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env build
        docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d

        Write-Host "=== wait for health ==="
        $baseUrl = $null
        Get-Content "deploy\.env" | ForEach-Object {
            if ($_ -match '^\s*NEXT_PUBLIC_API_URL\s*=\s*(.+)\s*$') {
                $baseUrl = $Matches[1].Trim().Trim('"').Trim("'").TrimEnd("/")
            }
        }
        if (-not $baseUrl) { throw "Could not read NEXT_PUBLIC_API_URL from deploy/.env" }

        $healthUrl = "$baseUrl/health"
        $ok = $false
        for ($i = 1; $i -le 30; $i++) {
            try {
                $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
                if ($resp.StatusCode -eq 200 -and $resp.Content -match '"status"\s*:\s*"ok"') {
                    $ok = $true
                    break
                }
            } catch {
                Start-Sleep -Seconds 3
            }
        }
        if (-not $ok) {
            Write-Host "Health check failed at $healthUrl — recent logs:"
            docker compose -f deploy/docker-compose.prod.yml logs --tail 80 backend nginx
            throw "Backend health check failed"
        }
        Write-Host "Health OK: $healthUrl"

        if ($Seed) {
            Write-Host "=== seed demo data ==="
            $env:API_BASE_URL = $baseUrl
            if (Get-Command python -ErrorAction SilentlyContinue) {
                python populate_preview.py
            } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
                python3 populate_preview.py
            } else {
                Write-Host "python not found — run manually: API_BASE_URL=$baseUrl python populate_preview.py"
            }
        }

        Write-Host "=== Deploy complete ==="
        Write-Host "App URL: $baseUrl"
    } finally {
        Pop-Location
    }
}

if ($Remote) {
    $remoteCmd = @"
set -e
cd ~/saloon-manager 2>/dev/null || cd /opt/saloon-manager 2>/dev/null || { echo 'Clone repo to ~/saloon-manager first'; exit 1; }
git pull --ff-only || true
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env build
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d
curl -sf "\$(grep NEXT_PUBLIC_API_URL deploy/.env | cut -d= -f2 | tr -d '\"')/health"
"@
    Write-Host "=== Remote deploy via gcloud ssh ==="
    gcloud compute ssh $VmName --zone $Zone --project $Project --command $remoteCmd
    if ($Seed) {
        $seedCmd = 'cd ~/saloon-manager || cd /opt/saloon-manager; export API_BASE_URL=$(grep NEXT_PUBLIC_API_URL deploy/.env | cut -d= -f2 | tr -d "\""); python3 populate_preview.py || python populate_preview.py'
        gcloud compute ssh $VmName --zone $Zone --project $Project --command $seedCmd
    }
    exit 0
}

Invoke-DeployOnHost -WorkDir $RepoRoot
