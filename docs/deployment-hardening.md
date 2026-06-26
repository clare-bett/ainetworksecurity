# Deployment Hardening for Fair Evaluation

Use these settings when you want the agent to solve the challenge as a black-box target on an existing Kali machine:

- Run `kali-mcp` as a non-root user if you expect local file permissions to matter.
- Install with `sudo bash scripts/kali-install.sh`.
- Remove the Git checkout after install, or keep it under a directory the MCP user cannot read.
- Do not give the agent the GitHub repository URL during the challenge.
- Use `http://127.0.0.1:8080` as the target URL from MCP.
- Do not give `kali-mcp` access to Docker APIs or host mounts.
- Reset flags with `sudo bash scripts/kali-reset-flags.sh`.

If `kali-mcp` runs as root on the same Kali machine, the agent can read `/opt/aegisnet`, `/etc/aegisnet`, and runtime files directly. In that model the challenge becomes white-box unless you restrict the MCP command tool or put the target into a separate container/VM.
