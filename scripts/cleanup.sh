#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../docker"
echo "[cleanup] Stopping containers..."
docker compose down
echo "[cleanup] Removing unused Docker data..."
docker system prune -f
echo "[cleanup] Done."
