#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$ROOT/backups"
STAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "[backup] Saving container logs..."
docker logs nexvion-web > "$BACKUP_DIR/nexvion-logs-$STAMP.log" 2>&1 || true

echo "[backup] Archiving configuration..."
tar -czf "$BACKUP_DIR/config-$STAMP.tar.gz" -C "$ROOT" docker kubernetes helm

echo "[backup] Backup saved in $BACKUP_DIR"
