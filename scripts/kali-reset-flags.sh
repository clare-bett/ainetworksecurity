#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo ./scripts/kali-reset-flags.sh" >&2
  exit 1
fi

ENV_FILE="/etc/aegisnet/aegisnet.env"
if [ ! -f "${ENV_FILE}" ]; then
  echo "Missing ${ENV_FILE}. Run scripts/kali-install.sh first." >&2
  exit 1
fi

if command -v openssl >/dev/null 2>&1; then
  SEED="$(openssl rand -hex 32)"
else
  SEED="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
fi

printf 'FLAG_SEED=%s\nAEGISNET_RUN_USER=aegisnet\n' "${SEED}" > "${ENV_FILE}"
chmod 0600 "${ENV_FILE}"

set -a
. "${ENV_FILE}"
set +a
python3 /opt/aegisnet/app/bootstrap.py
chown -R aegisnet:aegisnet /srv/aegisnet /var/lib/aegisnet /run/aegisnet

if command -v systemctl >/dev/null 2>&1; then
  systemctl restart aegisnet.service || true
fi

echo "Flags reset."
