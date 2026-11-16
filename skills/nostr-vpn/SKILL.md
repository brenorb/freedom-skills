---
name: nostr-vpn
description: "Use this skill when Codex needs to work with the local `nvpn` command from Nostr VPN for private mesh VPN workflows: executable discovery, identity and config initialization, join requests, session control, service management, peer inspection, diagnostics, roster administration, and exit-node or route settings."
metadata:
  version: "0.2.0"
  repository: "https://github.com/mmalmi/nostr-vpn"
  homepage: "https://nostrvpn.org"
---

# nostr-vpn

Use the local `nvpn` CLI from Nostr VPN for private mesh VPN setup, pairing, session control, and diagnostics.

## Executable path

With a known CLI path and intended config, start with the requested action. If the executable is unknown, resolve it once and keep its absolute path in `$NVPN`. Do not run the GUI executable as a substitute for the CLI.

When discovery is needed, try normal command lookup first:

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

## Identity and config

Set `$NVPN_CONFIG` to the intended identity's persistent **absolute** config path, and pass it explicitly on every identity, daemon and service command below. Reuse the same path under elevation; `sudo` and OS services can have different default config directories. If the intended config is unknown, identify the existing user/service config or ask which identity to use. Do not run `init` as a discovery step.

Keep the config and identity-key sidecars together, with their existing owner and private permissions. For a new identity, initialize as the intended user in a private directory. Do not copy an identity, loosen permissions or generate replacement keys merely to make a privileged command succeed. Read `references/onboarding.md` for setup and permissions.

On PowerShell, use an absolute `$nvpnConfig` and pass `--config $nvpnConfig` after the relevant command, for example `& $nvpn status --config $nvpnConfig --json`.

## Default workflow

1. Choose the command that matches the user's goal. These are alternatives, not a sequence; `init` is only for an explicitly requested new identity:

```bash
"$NVPN" init --config "$NVPN_CONFIG"
"$NVPN" join-request --config "$NVPN_CONFIG"
"$NVPN" start --config "$NVPN_CONFIG" --connect
"$NVPN" start --config "$NVPN_CONFIG" --daemon --connect
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" doctor --config "$NVPN_CONFIG" --json
```

2. If that fails because `nvpn` is missing, the local config is not initialized yet, or there is no usable network state, read `references/onboarding.md`.
3. Prefer the join-request flow over manual config editing when joining a mesh:

```bash
"$NVPN" join-request --config "$NVPN_CONFIG"
"$NVPN" join-request --config "$NVPN_CONFIG" --no-wait --no-qr
"$NVPN" join-manual --config "$NVPN_CONFIG" --admin-device-id ADMIN_DEVICE_ID --network-id NETWORK_ID --json
```

`join-request` prints a link and terminal QR code, then waits for approval. Use `--no-qr` when sharing the link another way and `--no-wait` when the agent should return immediately. The exact join surface can vary by release; always check `"$NVPN" --help` before using commands copied from older documentation that mention `create-invite` or `import-invite`.

4. For session control, use the foreground path for one-off work and the daemon or service path for persistent use:

```bash
"$NVPN" start --config "$NVPN_CONFIG" --connect
"$NVPN" start --config "$NVPN_CONFIG" --daemon --connect
"$NVPN" stop --config "$NVPN_CONFIG"
"$NVPN" pause --config "$NVPN_CONFIG"
"$NVPN" resume --config "$NVPN_CONFIG"
test -f "$NVPN_CONFIG" || { printf '%s\n' "Intended config is missing; stop before service installation." >&2; exit 1; }
sudo "$NVPN" service install --config "$NVPN_CONFIG"
```

5. For inspection and troubleshooting, prefer read-oriented commands before changing config or routes:

```bash
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" service status --config "$NVPN_CONFIG" --json
"$NVPN" ip --config "$NVPN_CONFIG" --peer --json
"$NVPN" whois --config "$NVPN_CONFIG" 100.64.0.2 --json
"$NVPN" ping --config "$NVPN_CONFIG" 100.64.0.2
"$NVPN" doctor --config "$NVPN_CONFIG" --json
```

For `status --json`, interpret `mesh_ready` only when `status_source` is `daemon`. Config-only status has unknown readiness; an installed/running service alone does not prove the mesh is connected. See the readiness check in `references/commands.md`.

6. If the user needs raw command patterns or headless join capability checks, read `references/commands.md`. Check the installed binary's help before using `join-request --json` or `join-requests`; retain admin-app approval when unavailable. Never approve a join request automatically.

## Defaults

- Prefer `--json` for inspection commands when available.
- Reuse one explicit absolute config path for the intended identity across user, elevated, daemon and service contexts. Version/help queries do not need a config.
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
- `nvpn init --config ...` generates identity keys. Service installation can also generate a new config when the selected path is missing, so verify the intended existing file before installation.
- Only one saved network is active at a time.
- `nvpn join-request` creates a pending request; approval is controlled by the network's admin policy.
- `nvpn start --daemon --connect` creates a background daemon; `nvpn stop` is what shuts it down.
- `nvpn service install` is the persistent OS-managed path; it is distinct from `start --daemon`.
- macOS may require elevation for tunnel setup. Preserve the same explicit `--config` path when using `sudo`; do not let the root default select another identity.
- The join-request QR is printed in the terminal; do not expose it in logs or screenshots.
- Some releases document invite creation/import commands that are absent from newer binaries; use the installed binary's help output as the authority.
