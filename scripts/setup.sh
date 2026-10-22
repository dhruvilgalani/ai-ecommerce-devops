#!/usr/bin/env bash
set -euo pipefail

echo "[setup] Updating packages..."
sudo apt update -y
sudo apt install -y git curl unzip wget docker.io docker-compose-v2

echo "[setup] Starting Docker..."
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

echo "[setup] Done. Log out and back in so Docker group changes apply."
