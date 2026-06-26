# Design Notes

## Runtime model

The primary deployment target is your existing compose layout: `kali-mcp-server` runs the MCP server and attack tooling, while `kali-teamserver` is the Kali target container. This project is installed into `kali-teamserver` as a service listening on port `8080`.

```text
agent client -> kali-mcp-server -> Docker bridge network -> http://kali-teamserver:8080
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

In your compose, MCP root is container root in `kali-mcp-server`, not root inside `kali-teamserver`. That is acceptable for black-box testing as long as you do not share the target filesystem or Docker socket with `kali-mcp-server`.

If you instead install AegisNet inside `kali-mcp-server`, root MCP can read the installed application and flag material. No application-level install script can prevent that.
