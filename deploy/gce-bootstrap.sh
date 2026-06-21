#!/bin/bash
# GCE bootstrap — pull pre-built images from Artifact Registry (no on-VM build).
# Metadata: deploy-env (required), repo-url (optional), force-redeploy=1 (optional)
set -eux

export DEBIAN_FRONTEND=noninteractive
MARKER="/var/lib/saloon-deployed"
REGISTRY="asia-south1-docker.pkg.dev/saloon-manager-beta-5640/saloon-repo"

get_metadata() {
  curl -sf -H "Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/attributes/${1}" || true
}

FORCE="$(get_metadata force-redeploy)"
if [ -f "$MARKER" ] && [ "$FORCE" != "1" ]; then
  echo "[bootstrap] already deployed (set force-redeploy=1 to rerun)"
  exit 0
fi
rm -f "$MARKER"

# Swap + Docker
if ! swapon --show | grep -q '/swapfile'; then
  fallocate -l 4G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=4096
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl gnupg git python3 python3-pip
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  systemctl enable docker
  systemctl start docker
fi

# Artifact Registry auth (same-project GCE SA)
if ! command -v gcloud >/dev/null 2>&1; then
  apt-get install -y apt-transport-https
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list
  apt-get update
  apt-get install -y google-cloud-cli
fi
gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet

DEPLOY_ENV="$(get_metadata deploy-env)"
if [ -z "$DEPLOY_ENV" ]; then
  echo "[bootstrap] deploy-env metadata missing"
  exit 1
fi

REPO_URL="$(get_metadata repo-url)"
REPO_URL="${REPO_URL%% *}"
[ -z "$REPO_URL" ] && REPO_URL="https://github.com/AbhinavP003/saloon-manager.git"

APP_DIR="/opt/saloon-manager"
rm -rf "$APP_DIR"
git clone --depth 1 "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

mkdir -p deploy
printf '%s\n' "$DEPLOY_ENV" > deploy/.env

# Docker creates deploy/nginx.conf as a directory if the file is missing during first up.
if [ -d deploy/nginx.conf ]; then rm -rf deploy/nginx.conf; fi
if [ ! -f deploy/nginx.conf ]; then
  echo "[bootstrap] deploy/nginx.conf missing after clone"
  ls -la deploy/ || true
  exit 1
fi

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env down --remove-orphans 2>/dev/null || true

export COMPOSE_PARALLEL_LIMIT=1
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env pull
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d --no-build

BASE_URL="$(grep NEXT_PUBLIC_API_URL deploy/.env | cut -d= -f2- | tr -d ' \"')"
for i in $(seq 1 60); do
  if curl -sf "${BASE_URL}/health" | grep -q '"status":"ok"'; then
    echo "[bootstrap] health OK"
    break
  fi
  sleep 5
done

pip3 install --break-system-packages httpx 2>/dev/null || pip3 install httpx
API_BASE_URL="$BASE_URL" python3 populate_preview.py || true

touch "$MARKER"
echo "[bootstrap] deploy complete at $BASE_URL"
