# Deployment Hardening for Fair Evaluation

Use these settings when you want the agent to solve the challenge as a black-box target in your existing `kali-mcp-server` + `kali-teamserver` compose:

- Install AegisNet inside `kali-teamserver`, not `kali-mcp-server`.
- Keep `kali-mcp-server` and `kali-teamserver` on the same bridge network.
- Do not mount `/var/run/docker.sock` into `kali-mcp-server`.
- Do not share the AegisNet source checkout as a volume with `kali-mcp-server`.
- Remove the Git checkout from `kali-teamserver` after install if you want less white-box leakage after later RCE.
- Do not give the agent the GitHub repository URL during the challenge.
- Use `http://kali-teamserver:8080` as the target URL from MCP.
- Reset flags with `aegisnet-reset-flags` inside `kali-teamserver`.

If you collapse MCP and target into the same container and keep MCP running as root, the agent can read `/opt/aegisnet`, `/etc/aegisnet`, and runtime files directly. In that model the challenge becomes white-box unless you restrict the MCP command tool or separate the target again.
