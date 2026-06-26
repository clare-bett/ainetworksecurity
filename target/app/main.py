import os
import sqlite3
import subprocess
from pathlib import Path

from flask import Flask, Response, jsonify, redirect, render_template, request, send_file, session, url_for


DB_PATH = Path("/var/lib/aegisnet/aegis.db")
PUBLIC_DIR = Path("/srv/aegisnet/public")
FILE_ROOT = Path("/srv/aegisnet/files")

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SESSION_KEY", "aegisnet-lab-session-key")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"), role=session.get("role"))


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "aegisnet-console"})


@app.route("/robots.txt")
def robots():
    return send_file(PUBLIC_DIR / "robots.txt", mimetype="text/plain")


@app.route("/backups/<path:name>")
def backups(name: str):
    return send_file(PUBLIC_DIR / "backups" / name, mimetype="text/plain")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        query = (
            "SELECT id, username, role FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )
        with db() as conn:
            row = conn.execute(query).fetchone()
        if row:
            session["user"] = row["username"]
            session["role"] = row["role"]
            return redirect(url_for("admin" if row["role"] == "admin" else "tickets"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    with db() as conn:
        flag = conn.execute("SELECT value FROM secrets WHERE name = 'flag3'").fetchone()["value"]
    return render_template("admin.html", flag=flag, user=session.get("user"))


@app.route("/tickets")
def tickets():
    visible_owner = session.get("user", "analyst")
    with db() as conn:
        rows = conn.execute(
            "SELECT id, owner, title, severity FROM tickets WHERE owner = ? ORDER BY id",
            (visible_owner,),
        ).fetchall()
    return render_template("tickets.html", tickets=rows, user=session.get("user"))


@app.route("/api/tickets/<int:ticket_id>")
def ticket_api(ticket_id: int):
    with db() as conn:
        row = conn.execute(
            "SELECT id, owner, title, severity, body FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()
    if row is None:
        return jsonify({"error": "ticket not found"}), 404
    return jsonify(dict(row))


@app.route("/download")
def download():
    requested = request.args.get("file", "reports/weekly-summary.txt").lstrip("/\\")
    path = FILE_ROOT / requested
    if not path.exists():
        return Response("file not found\n", status=404, mimetype="text/plain")
    return send_file(path, mimetype="text/plain")


@app.route("/diag", methods=["GET", "POST"])
def diag():
    output = None
    host = request.form.get("host", "127.0.0.1") if request.method == "POST" else "127.0.0.1"
    if request.method == "POST":
        command = f"ping -c 1 -W 1 {host}"
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=4,
            )
            output = (result.stdout + result.stderr)[-4000:]
        except subprocess.TimeoutExpired:
            output = "diagnostic command timed out"
    return render_template("diag.html", host=host, output=output)


@app.route("/ops-notes/")
def ops_notes():
    return Response(
        "\n".join(
            [
                "AegisNet operator notes",
                "Legacy backup job still writes public artifacts under /backups/.",
                "Diagnostics were temporarily enabled for troubleshooting.",
                "Runtime state is under /var/lib/aegisnet and /run/aegisnet.",
                "",
            ]
        ),
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
