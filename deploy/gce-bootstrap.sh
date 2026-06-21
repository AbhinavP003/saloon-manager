#!/bin/bash
# First deploy on GCE — run once via instance startup-script metadata.
# Expects metadata keys: deploy-env (multiline .env contents), repo-url (optional).
set -eux

export DEBIAN_FRONTEND=noninteractive
MARKER="/var/lib/saloon-deployed"

if [ -f "$MARKER" ]; then
  echo "[bootstrap] already deployed"
  exit 0
fi

# Docker + swap (same as gce-startup.sh)
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl gnupg git
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin python3 python3-pip
  systemctl enable docker
  systemctl start docker
fi

if ! swapon --show | grep -q '/swapfile'; then
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

get_metadata() {
  local key="$1"
  curl -sf -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/attributes/${key}" || true
}

REPO_URL="$(get_metadata repo-url)"
DEPLOY_ENV="$(get_metadata deploy-env)"

if [ -z "$REPO_URL" ]; then
  REPO_URL="https://github.com/AbhinavP003/saloon-manager.git"
fi

if [ -z "$DEPLOY_ENV" ]; then
  echo "[bootstrap] deploy-env metadata missing — skipping app deploy"
  exit 0
fi

APP_DIR="/opt/saloon-manager"
rm -rf "$APP_DIR"
git clone --depth 1 "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

mkdir -p deploy
printf '%s\n' "$DEPLOY_ENV" > deploy/.env

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env build
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d

# Seed demo data once backend is healthy
BASE_URL="$(grep NEXT_PUBLIC_API_URL deploy/.env | cut -d= -f2- | tr -d ' \"')"
for i in $(seq 1 30); do
  if curl -sf "${BASE_URL}/health" | grep -q '"status":"ok"'; then
    break
  fi
  sleep 5
done

if command -v pip3 >/dev/null 2>&1; then
  pip3 install --break-system-packages httpx 2>/dev/null || pip3 install httpx
fi
API_BASE_URL="$BASE_URL" python3 populate_preview.py || true

touch "$MARKER"
echo "[bootstrap] deploy complete at $BASE_URL"
