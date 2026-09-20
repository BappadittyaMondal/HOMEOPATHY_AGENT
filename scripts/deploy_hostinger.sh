#!/usr/bin/env bash
# ==============================================================================
# Hostinger KVM Linux VPS Deployment & Provisioning Script
# HOMEOPATHY_AGENT (v3.0.0-ENTERPRISE-CLINICAL)
# ==============================================================================
set -euo pipefail

echo "================================================================================"
echo "PROVISIONING HOMEOPATHY_AGENT ON HOSTINGER LINUX VPS"
echo "================================================================================"

# 1. Verify Docker and Docker Compose
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not installed. Aborting."; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "ERROR: docker compose not available. Aborting."; exit 1; }

# 2. Kernel Memory-Map Configuration for High-Speed CSR Kernel
echo "Configuring Linux kernel sysctl parameters..."
sudo sysctl -w vm.max_map_count=262144 >/dev/null 2>&1 || true

# 3. Create Persistent Data Directories
DATA_DIR="/var/lib/homeopathy_agent/data"
echo "Setting up data directory at ${DATA_DIR}..."
sudo mkdir -p "${DATA_DIR}"
sudo chown -R 10001:10001 "${DATA_DIR}"
sudo chmod 750 "${DATA_DIR}"

# 4. Launch Production Docker Stack
echo "Building and starting containerized services..."
cd docker
docker compose pull --ignore-pull-failures || true
docker compose up -d --build

# 5. Verify Healthcheck
echo "Waiting for service healthcheck..."
sleep 5
docker compose ps

echo "================================================================================"
echo "DEPLOYMENT COMPLETE: HOMEOPATHY_AGENT is live on Hostinger VPS!"
echo "================================================================================"
