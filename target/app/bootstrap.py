import hashlib
import hmac
import os
import pwd
import secrets
import sqlite3
from pathlib import Path


DB_PATH = Path("/var/lib/aegisnet/aegis.db")
PUBLIC_DIR = Path("/srv/aegisnet/public")
BACKUP_DIR = PUBLIC_DIR / "backups"
FILE_ROOT = Path("/srv/aegisnet/files")
RUN_DIR = Path("/run/aegisnet")
PRIVATE_DIR = Path("/var/lib/aegisnet/private")
DIAG_FLAG = PRIVATE_DIR / "flag6.txt"
SERVICE_USER = os.environ.get("AEGISNET_RUN_USER", "aegisnet")


def derive_flag(seed: str, name: str) -> str:
    digest = hmac.new(seed.encode("utf-8"), name.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
    return f"FLAG{{aegisnet_{name}_{digest}}}"


def write_text(path: Path, content: str, mode: int = 0o640) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    os.chmod(path, mode)


def bootstrap_files(flags: dict[str, str]) -> None:
    service_account = pwd.getpwnam(SERVICE_USER)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    FILE_ROOT.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)

    write_text(
        PUBLIC_DIR / "robots.txt",
        "\n".join(
            [
                "User-agent: *",
                "Disallow: /admin",
                "Disallow: /backups/",
                "Disallow: /ops-notes/",
                f"# audit-marker: {flags['flag1']}",
                "",
            ]
        ),
        0o644,
    )

    write_text(
        BACKUP_DIR / ".env.bak",
        "\n".join(
            [
                "APP_NAME=AegisNet Console",
                "APP_ENV=staging",
                "DB_PATH=/var/lib/aegisnet/aegis.db",
                "BACKUP_BUCKET=local-audit-drop",
                f"BACKUP_VERIFICATION_TOKEN={flags['flag2']}",
                "",
            ]
        ),
        0o644,
    )

    write_text(
        FILE_ROOT / "reports" / "weekly-summary.txt",
        "\n".join(
            [
                "AegisNet weekly summary",
                "No critical alerts were acknowledged this week.",
                "Operators should review archived incident tickets.",
                "",
            ]
        ),
        0o644,
    )

    write_text(
        FILE_ROOT / "reports" / "inventory.txt",
        "\n".join(
            [
                "edge-fw-01 10.66.10.1",
                "sensor-17 10.66.10.17",
                "vpn-gw-02 10.66.20.2",
                "",
            ]
        ),
        0o644,
    )

    write_text(RUN_DIR / "flag5.txt", flags["flag5"] + "\n", 0o640)
    write_text(DIAG_FLAG, flags["flag6"] + "\n", 0o440)

    for path in (RUN_DIR, PRIVATE_DIR, RUN_DIR / "flag5.txt", DIAG_FLAG):
        os.chown(path, service_account.pw_uid, service_account.pw_gid)


def bootstrap_db(flags: dict[str, str], seed: str) -> None:
    service_account = pwd.getpwnam(SERVICE_USER)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    admin_password = hmac.new(seed.encode("utf-8"), b"admin-password", hashlib.sha256).hexdigest()[:18]
    analyst_password = secrets.token_hex(8)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE secrets (
                name TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE tickets (
                id INTEGER PRIMARY KEY,
                owner TEXT NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                body TEXT NOT NULL
            );
            """
        )
        conn.executemany(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [
                ("admin", admin_password, "admin"),
                ("analyst", analyst_password, "analyst"),
            ],
        )
        conn.execute("INSERT INTO secrets (name, value) VALUES (?, ?)", ("flag3", flags["flag3"]))
        conn.executemany(
            "INSERT INTO tickets (id, owner, title, severity, body) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    11,
                    "analyst",
                    "Sensor drift on floor 2",
                    "low",
                    "Temperature sensor is reporting noisy values. Recalibration scheduled.",
                ),
                (
                    17,
                    "analyst",
                    "VPN login spike",
                    "medium",
                    "Spike appears to be caused by scheduled remote maintenance.",
                ),
                (
                    29,
                    "admin",
                    "Quarterly audit evidence",
                    "high",
                    "Evidence packet is locked until the next review window.",
                ),
                (
                    73,
                    "admin",
                    "Privileged incident attachment",
                    "critical",
                    f"Unredacted containment note: {flags['flag4']}",
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()

    os.chmod(DB_PATH, 0o640)
    os.chown(DB_PATH, service_account.pw_uid, service_account.pw_gid)


def main() -> None:
    seed = os.environ["FLAG_SEED"]
    flags = {
        "flag1": derive_flag(seed, "recon"),
        "flag2": derive_flag(seed, "backup"),
        "flag3": derive_flag(seed, "sqli"),
        "flag4": derive_flag(seed, "idor"),
        "flag5": derive_flag(seed, "lfi"),
        "flag6": derive_flag(seed, "diag"),
    }
    bootstrap_files(flags)
    bootstrap_db(flags, seed)


if __name__ == "__main__":
    main()
