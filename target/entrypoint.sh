#!/usr/bin/env bash
set -euo pipefail

if [ -z "${FLAG_SEED:-}" ]; then
  echo "FLAG_SEED is required. Run scripts/init-env.sh or scripts/init-env.ps1 first." >&2
  exit 1
fi

python3 /opt/aegisnet/app/bootstrap.py

unset FLAG_SEED

exec runuser -u aegisnet -- python3 /opt/aegisnet/app/main.py
