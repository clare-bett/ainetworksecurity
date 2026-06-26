# Design Notes

## Runtime model

The primary deployment target is an existing Dockerized Kali machine that already has `kali-mcp` connected to it. This project is installed into that Kali as a local service listening on `127.0.0.1:8080`.

```text
agent client -> kali-mcp -> existing Kali shell/tools -> http://127.0.0.1:8080
```

The repository also keeps an optional Docker Compose lab for local self-contained testing, but that is not the primary path when your Kali and MCP service already exist.

## Flag lifecycle

The repository contains no real flags. Deployment works like this:

1. `scripts/init-env.sh` or `scripts/init-env.ps1` creates a local `.env`.
2. For direct Kali install, `scripts/kali-install.sh` creates `/etc/aegisnet/aegisnet.env`.
3. `/opt/aegisnet/app/bootstrap.py` derives six flags and places them into challenge surfaces.
4. The Flask service starts as the low-privilege `aegisnet` user.

## Vulnerability surfaces

- Public metadata exposure.
- Backup artifact exposure.
- SQL injection in login.
- Object-level authorization failure in a ticket API.
- Path traversal in report download.
- Shell command injection in diagnostics.

## Fixed-call agent evaluation

The project defines the budget in `agent/challenge.yaml` and the agent prompt in `agent/system_prompt.md`. Most MCP clients enforce the budget in the orchestration layer, so this repository keeps the policy explicit and makes the judge independent of the agent framework.

## Source visibility caveat

If `kali-mcp` can run arbitrary commands as root on the same Kali instance, it can read the installed application and all flag material. No application-level install script can prevent root from doing that. For a fair black-box run, run `kali-mcp` as a non-root user, install AegisNet under root-owned paths, and remove or lock down the Git checkout after installation.
