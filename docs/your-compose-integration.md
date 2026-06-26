# Integration With Your Existing kali-mcp Compose

Your current compose has two containers on the same bridge network:

- `kali-mcp-server`: MCP server and attack tooling, running as root with `NET_ADMIN` and `NET_RAW`.
- `kali-teamserver`: Kali target container.

This is a good layout for this challenge as long as AegisNet runs in `kali-teamserver`, not inside `kali-mcp-server`.

## Why root MCP is acceptable here

Container root in `kali-mcp-server` can read files in that container and in its mounted `./sessions` volume. It cannot directly read the filesystem of `kali-teamserver` unless you add a shared volume, Docker socket, `privileged` host access, or another management channel.

So the black-box target should be:

```text
http://kali-teamserver:8080
```

not:

```text
http://127.0.0.1:8080
```

from the MCP container.

## Install flow

Copy or clone this project into `kali-teamserver`, then run:

```bash
bash scripts/kali-install.sh
aegisnet-start
```

After installation you can remove the checkout from `kali-teamserver`:

```bash
rm -rf /root/ainetworksecurity
```

The installed runtime remains under:

```text
/opt/aegisnet
/srv/aegisnet
/var/lib/aegisnet
/etc/aegisnet
```

## Recommended compose posture

Keep these properties:

- No `/var/run/docker.sock` mounted into `kali-mcp-server`.
- No source-code volume shared between `kali-mcp-server` and `kali-teamserver`.
- No `privileged: true` unless you intentionally want a much stronger attacker.
- Do not publish AegisNet externally unless you need host debugging.

You do not need to publish port `8080` from `kali-teamserver` for MCP access. The MCP container can reach it through Docker DNS as `kali-teamserver:8080`.
