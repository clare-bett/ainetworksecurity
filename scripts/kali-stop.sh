#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash scripts/kali-stop.sh" >&2
  exit 1
fi

if pgrep -u aegisnet -f "/opt/aegisnet/app/main.py" >/dev/null 2>&1; then
  pkill -u aegisnet -f "/opt/aegisnet/app/main.py"
  echo "AegisNet stopped."
else
  echo "AegisNet is not running."
fi
