#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash scripts/kali-start.sh" >&2
  exit 1
fi

if [ ! -x /opt/aegisnet/aegisnet-run ]; then
  echo "Missing /opt/aegisnet/aegisnet-run. Run scripts/kali-install.sh first." >&2
  exit 1
fi

install -d -o aegisnet -g aegisnet -m 0750 /var/log/aegisnet /run/aegisnet

if pgrep -u aegisnet -f "/opt/aegisnet/app/main.py" >/dev/null 2>&1; then
  echo "AegisNet is already running."
  exit 0
fi

nohup runuser -u aegisnet -- /opt/aegisnet/aegisnet-run > /var/log/aegisnet/aegisnet.log 2>&1 &
sleep 1

if pgrep -u aegisnet -f "/opt/aegisnet/app/main.py" >/dev/null 2>&1; then
  echo "AegisNet started on http://127.0.0.1:8080"
else
  echo "AegisNet did not stay running. Check /var/log/aegisnet/aegisnet.log" >&2
  exit 1
fi
