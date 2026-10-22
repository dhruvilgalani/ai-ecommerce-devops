#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"

for path in "healthz" "" "products.html" "payment.html"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$path")
  if [ "$code" -eq 200 ]; then
    echo "[OK]   $BASE_URL/$path"
  else
    echo "[FAIL] $BASE_URL/$path returned $code"
    exit 1
  fi
done
echo "[health] All checks passed."
