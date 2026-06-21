# One-time GCE e2-micro provisioning for Saloon Manager beta (~$0 Always Free).
# Run from repo root on a machine with gcloud CLI authenticated.
#
# Usage:
#   .\deploy\gce-setup.ps1
#   .\deploy\gce-setup.ps1 -MyIp "203.0.113.10/32"   # restrict SSH to your IP
#
# After VM is ready, SSH in, clone the repo, copy deploy/.env.gce.example → deploy/.env,
# then run .\deploy\gce-deploy.ps1 on the VM (or from local via -VmName).

param(
    [string]$Project = "saloon-manager-beta-5640",
    [string]$Zone = "us-central1-a",
    [string]$VmName = "saloon-beta-vm",
    [string]$MachineType = "e2-micro",
    [int]$BootDiskGb = 30,
    [string]$MyIp = "0.0.0.0/0"
)

$ErrorActionPreference = "Stop"
$Gcloud = "gcloud"
$StartupScriptPath = Join-Path $PSScriptRoot "gce-startup.sh"

function Invoke-Gcloud {
    param([string[]]$GcloudArgs)
    & $Gcloud @GcloudArgs
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud failed: gcloud $($GcloudArgs -join ' ')"
    }
}

Write-Host "=== GCE single-VM beta setup ==="
Write-Host "Project: $Project  Zone: $Zone  VM: $VmName"

Invoke-Gcloud @("config", "set", "project", $Project)

Write-Host "=== Enable Compute Engine API (if needed) ==="
Invoke-Gcloud @("services", "enable", "compute.googleapis.com", "--quiet")

Write-Host "=== Firewall: HTTP/HTTPS (public) ==="
$httpRule = "saloon-beta-allow-http"
$existsHttp = $null
try {
    $existsHttp = (& $Gcloud compute firewall-rules describe $httpRule --format="value(name)" 2>$null)
} catch { }
if (-not $existsHttp) {
    Invoke-Gcloud @(
        "compute", "firewall-rules", "create", $httpRule,
        "--allow", "tcp:80,tcp:443",
        "--target-tags", "saloon-beta",
        "--description", "Saloon beta HTTP/HTTPS"
    )
} else {
    Write-Host "Firewall rule $httpRule already exists"
}

Write-Host "=== Firewall: SSH (restricted) ==="
$sshRule = "saloon-beta-allow-ssh"
$existsSsh = $null
try {
    $existsSsh = (& $Gcloud compute firewall-rules describe $sshRule --format="value(name)" 2>$null)
} catch { }
if (-not $existsSsh) {
    Invoke-Gcloud @(
        "compute", "firewall-rules", "create", $sshRule,
        "--allow", "tcp:22",
        "--target-tags", "saloon-beta",
        "--source-ranges", $MyIp,
        "--description", "Saloon beta SSH"
    )
} else {
    Write-Host "Updating SSH source range on $sshRule to $MyIp"
    Invoke-Gcloud @(
        "compute", "firewall-rules", "update", $sshRule,
        "--source-ranges", $MyIp
    )
}

if (-not (Test-Path $StartupScriptPath)) {
    throw "Missing startup script: $StartupScriptPath"
}

Write-Host "=== Create VM (or skip if exists) ==="
$vmExists = $null
try {
    $vmExists = (& $Gcloud compute instances describe $VmName --zone $Zone --format="value(name)" 2>$null)
} catch { }
if ($vmExists) {
    Write-Host "VM $VmName already exists in $Zone"
} else {
    Invoke-Gcloud @(
        "compute", "instances", "create", $VmName,
        "--zone", $Zone,
        "--machine-type", $MachineType,
        "--boot-disk-size", "${BootDiskGb}GB",
        "--boot-disk-type", "pd-standard",
        "--image-family", "debian-12",
        "--image-project", "debian-cloud",
        "--tags", "saloon-beta",
        "--metadata-from-file", "startup-script=$StartupScriptPath",
        "--scopes", "default"
    )
}

Write-Host "=== Reserve static external IP (free while VM is running) ==="
$ipName = "${VmName}-ip"
$ipExists = $null
try {
    $ipExists = (& $Gcloud compute addresses describe $ipName --region "us-central1" --format="value(name)" 2>$null)
} catch { }
if (-not $ipExists) {
    Invoke-Gcloud @(
        "compute", "addresses", "create", $ipName,
        "--region", "us-central1"
    )
}

$staticIp = (& $Gcloud compute addresses describe $ipName --region "us-central1" --format="value(address)").Trim()
Write-Host "Static IP: $staticIp"

$currentNat = (& $Gcloud compute instances describe $VmName --zone $Zone --format="value(networkInterfaces[0].accessConfigs[0].natIP)").Trim()
if ($currentNat -ne $staticIp) {
    Write-Host "=== Attach static IP to VM ==="
    Invoke-Gcloud @(
        "compute", "instances", "delete-access-config", $VmName,
        "--zone", $Zone,
        "--access-config-name", "external-nat"
    )
    Invoke-Gcloud @(
        "compute", "instances", "add-access-config", $VmName,
        "--zone", $Zone,
        "--access-config-name", "external-nat",
        "--address", $staticIp
    )
}

Write-Host ""
Write-Host "=== VM ready ==="
Write-Host "External IP: $staticIp"
Write-Host "SSH: gcloud compute ssh $VmName --zone $Zone --project $Project"
Write-Host ""
Write-Host "Next steps:"
Write-Host '  1. SSH to the VM and clone this repo (or scp deploy files)'
Write-Host "  2. cp deploy/.env.gce.example deploy/.env - set secrets, VM IP=$staticIp"
Write-Host '  3. Run deploy/gce-deploy.ps1 on the VM'
Write-Host "  4. Seed: API_BASE_URL=http://$staticIp python populate_preview.py"
Write-Host "  5. Open http://$staticIp"
Write-Host ""
Write-Host 'See docs/DEPLOY_GCE.md for cutover and Cloud SQL / Cloud Run teardown.'
