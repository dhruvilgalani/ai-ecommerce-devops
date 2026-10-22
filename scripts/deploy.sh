#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../docker"
echo "[deploy] Building and starting the application..."
docker compose up -d --build
echo "[deploy] Application is running at http://localhost:8080"
