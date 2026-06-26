#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [ -f "${ENV_FILE}" ]; then
  echo ".env already exists: ${ENV_FILE}"
  exit 0
fi

if command -v openssl >/dev/null 2>&1; then
  SEED="$(openssl rand -hex 32)"
else
  SEED="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
fi

cat > "${ENV_FILE}" <<EOF
FLAG_SEED=${SEED}
EOF

chmod 0600 "${ENV_FILE}"
echo "Created ${ENV_FILE}"
