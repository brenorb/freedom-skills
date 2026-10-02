---
name: nostr-vpn
description: "Use this skill when Codex needs to work with the local `nvpn` command from Nostr VPN for private mesh VPN workflows: executable discovery, identity and config initialization, join requests, session control, service management, peer inspection, diagnostics, roster administration, and exit-node or route settings."
metadata:
  version: "0.1.0"
  repository: "https://github.com/mmalmi/nostr-vpn"
  homepage: "https://nostrvpn.org"
---

# nostr-vpn

Use the local `nvpn` CLI from Nostr VPN for private mesh VPN setup, pairing, session control, and diagnostics.

## Resolve the CLI before using it

Do not assume that `nvpn` is on `PATH`, and do not run the GUI executable as a substitute for the CLI. Resolve the executable once, keep the absolute path in a shell variable, and use that variable for the rest of the task.

On every platform, try the normal command lookup first:

```bash
command -v nvpn || true
```

If that fails, read `references/command-discovery.md` and use its platform-specific candidates. In particular, the macOS desktop app bundles the CLI separately from the GUI executable:

```text
/Applications/Nostr VPN.app/Contents/Resources/nvpn
~/Applications/Nostr VPN.app/Contents/Resources/nvpn
```

The GUI at `Contents/MacOS/Nostr VPN` is not the CLI. On Linux, check user and system executable directories plus the Cargo install location. On Windows, check `Get-Command nvpn`/`where.exe nvpn` and the app's `nvpn.exe` or `resources\\nvpn.exe` locations under the user's programs directory and `Program Files`.

After resolving the path, verify the binary before any state-changing command:

```bash
"$NVPN" version --json
"$NVPN" --help
```

For PowerShell, invoke the resolved path with `& $nvpn version --json`. If no executable can be resolved, follow `references/onboarding.md`; do not silently install software.

## Default workflow

1. Start with the command that matches the user's goal:

```bash
"$NVPN" init
"$NVPN" join-request
"$NVPN" start --connect
"$NVPN" start --daemon --connect
"$NVPN" status --json
"$NVPN" doctor --json
```

2. If that fails because `nvpn` is missing, the local config is not initialized yet, or there is no usable network state, read `references/onboarding.md`.
3. Prefer the join-request flow over manual config editing when joining a mesh:

```bash
"$NVPN" join-request
"$NVPN" join-request --no-wait --no-qr
"$NVPN" join-manual --admin-device-id ADMIN_DEVICE_ID --network-id NETWORK_ID --json
```

`join-request` prints a link and terminal QR code, then waits for approval. Use `--no-qr` when sharing the link another way and `--no-wait` when the agent should return immediately. The exact join surface can vary by release; always check `"$NVPN" --help` before using commands copied from older documentation that mention `create-invite` or `import-invite`.

4. For session control, use the foreground path for one-off work and the daemon or service path for persistent use:

```bash
"$NVPN" start --connect
"$NVPN" start --daemon --connect
"$NVPN" stop
"$NVPN" pause
"$NVPN" resume
sudo "$NVPN" service install
```

5. For inspection and troubleshooting, prefer read-oriented commands before changing config or routes:

```bash
"$NVPN" status --json
"$NVPN" service status --json
"$NVPN" ip --peer --json
"$NVPN" whois 100.64.0.2 --json
"$NVPN" ping 100.64.0.2
"$NVPN" doctor --json
```

6. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer `--json` for inspection commands when available.
- Prefer the default config path instead of passing `--config` unless the user clearly wants an alternate file.
- Prefer `nvpn start --connect` for short-lived troubleshooting and `nvpn start --daemon --connect` for desktop-style persistent use.
- Prefer `nvpn join-request` or `nvpn join-manual` over manual editing of network IDs or roster state.
- Prefer `nvpn set` for persistent settings such as autoconnect, join requests, routes, and exit-node selection.
- On macOS, expect tunnel and service operations to require admin privileges.
- Treat `"$NVPN" --help` as the version-specific command reference; the installed binary may be newer or older than the online README.

## Safety rules

- Treat join links, QR codes, identity keys, private keys, roster IDs, and WireGuard upstream configs as sensitive.
- Do not paste secrets into chat or shell history when a local file or user-run step is safer.
- Confirm before sharing a join link/QR, joining a network, changing the active network, or editing device/admin rosters.
- Confirm before enabling exit-node behavior, route advertisement, WireGuard upstream settings, or service install/uninstall because they can affect host networking.
- Prefer `status`, `ip`, `whois`, `ping`, and `doctor` before disruptive actions.
- `nvpn` does not expose a general dry-run mode, so use read-only commands first when validating state.

## Gotchas

- The CLI name is `nvpn`, not `nostr-vpn`.
- `nvpn init` generates identity keys automatically and writes config into the OS config directory.
- Only one saved network is active at a time.
- `nvpn join-request` creates a pending request; approval is controlled by the network's admin policy.
- `nvpn start --daemon --connect` creates a background daemon; `nvpn stop` is what shuts it down.
- `nvpn service install` is the persistent OS-managed path; it is distinct from `start --daemon`.
- macOS may require `sudo nvpn start --connect` or `sudo nvpn service install` for tunnel setup.
- The join-request QR is printed in the terminal; do not expose it in logs or screenshots.
- Some releases document invite creation/import commands that are absent from newer binaries; use the installed binary's help output as the authority.
