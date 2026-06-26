#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo ./scripts/kali-install.sh" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_SRC="${ROOT_DIR}/target/app"
APP_DIR="/opt/aegisnet/app"
ENV_DIR="/etc/aegisnet"
ENV_FILE="${ENV_DIR}/aegisnet.env"
RUN_SCRIPT="/opt/aegisnet/aegisnet-run"
SERVICE_FILE="/etc/systemd/system/aegisnet.service"
LOCAL_SBIN="/usr/local/sbin"

if [ ! -d "${APP_SRC}" ]; then
  echo "Missing app source directory: ${APP_SRC}" >&2
  exit 1
fi

apt-get update
apt-get install -y --no-install-recommends python3 python3-flask sqlite3 iputils-ping util-linux procps

if ! id aegisnet >/dev/null 2>&1; then
  useradd -m -s /bin/bash aegisnet
fi

if command -v systemctl >/dev/null 2>&1; then
  systemctl stop aegisnet.service >/dev/null 2>&1 || true
fi

install -d -o root -g root -m 0700 "${ENV_DIR}"
if [ ! -f "${ENV_FILE}" ]; then
  if command -v openssl >/dev/null 2>&1; then
    SEED="$(openssl rand -hex 32)"
  else
    SEED="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  fi
  printf 'FLAG_SEED=%s\nAEGISNET_RUN_USER=aegisnet\n' "${SEED}" > "${ENV_FILE}"
  chmod 0600 "${ENV_FILE}"
fi

rm -rf "${APP_DIR}"
install -d -o root -g aegisnet -m 0750 /opt/aegisnet
install -d -o root -g aegisnet -m 0750 "${APP_DIR}"
cp -a "${APP_SRC}/." "${APP_DIR}/"
chown -R root:aegisnet "${APP_DIR}"
find "${APP_DIR}" -type d -exec chmod 0750 {} +
find "${APP_DIR}" -type f -exec chmod 0640 {} +

install -d -o aegisnet -g aegisnet -m 0750 /srv/aegisnet /srv/aegisnet/files /srv/aegisnet/public /var/lib/aegisnet /run/aegisnet

set -a
. "${ENV_FILE}"
set +a
python3 "${APP_DIR}/bootstrap.py"
chown -R aegisnet:aegisnet /srv/aegisnet /var/lib/aegisnet /run/aegisnet

cat > "${RUN_SCRIPT}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd /opt/aegisnet
exec python3 /opt/aegisnet/app/main.py
EOF
chown root:aegisnet "${RUN_SCRIPT}"
chmod 0750 "${RUN_SCRIPT}"

install -d -o root -g root -m 0755 "${LOCAL_SBIN}"
install -o root -g root -m 0750 "${ROOT_DIR}/scripts/kali-start.sh" "${LOCAL_SBIN}/aegisnet-start"
install -o root -g root -m 0750 "${ROOT_DIR}/scripts/kali-stop.sh" "${LOCAL_SBIN}/aegisnet-stop"
install -o root -g root -m 0750 "${ROOT_DIR}/scripts/kali-reset-flags.sh" "${LOCAL_SBIN}/aegisnet-reset-flags"

cat > "${SERVICE_FILE}" <<'EOF'
[Unit]
Description=AegisNet Kali CTF target
After=network.target

[Service]
Type=simple
User=aegisnet
Group=aegisnet
WorkingDirectory=/opt/aegisnet
Environment=APP_SESSION_KEY=aegisnet-local-lab-session
ExecStart=/opt/aegisnet/aegisnet-run
Restart=on-failure
RestartSec=2
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

if command -v systemctl >/dev/null 2>&1; then
  systemctl daemon-reload || true
  systemctl enable aegisnet.service || true
fi

cat <<EOF
AegisNet installed.

Start with:
  systemctl start aegisnet

If systemd is unavailable:
  aegisnet-start

Target URL from the existing Kali/MCP environment:
  http://127.0.0.1:8080

For a fair black-box run, remove or lock down the Git checkout after install.
If kali-mcp runs as root on this same Kali, it can read any local file; use a separate container/VM or restrict the MCP command tool for true black-box isolation.
EOF
