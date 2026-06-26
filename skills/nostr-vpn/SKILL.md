---
name: nostr-vpn
description: Use this skill when Codex needs to work with the local `nvpn` command from Nostr VPN for private mesh VPN workflows: install/setup, identity and config initialization, invite creation/import, LAN pairing, session control, service management, peer inspection, diagnostics, and exit-node or route settings.
---

# nostr-vpn

Use the local `nvpn` CLI from Nostr VPN for private mesh VPN setup, pairing, session control, and diagnostics.

## Default workflow

1. Start with the command that matches the user's goal:

```bash
nvpn create-invite
nvpn import-invite 'nvpn://invite/...'
nvpn start --connect
nvpn start --daemon --connect
nvpn status --json
nvpn doctor --json
```

2. If that fails because `nvpn` is missing, the local config is not initialized yet, or there is no usable network state, read `references/onboarding.md`.
3. Prefer the invite flow over manual config editing when joining or sharing a mesh:

```bash
nvpn create-invite
nvpn import-invite 'nvpn://invite/...'
nvpn invite-broadcast --duration-secs 900
nvpn discover --accept --json
```

4. For session control, use the foreground path for one-off work and the daemon or service path for persistent use:

```bash
nvpn start --connect
nvpn start --daemon --connect
nvpn stop
nvpn pause
nvpn resume
sudo nvpn service install
```

5. For inspection and troubleshooting, prefer read-oriented commands before changing config or routes:

```bash
nvpn status --json
nvpn service status --json
nvpn ip --peer --json
nvpn whois 100.64.0.2 --json
nvpn ping 100.64.0.2
nvpn doctor --json
```

6. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer `--json` for inspection commands when available.
- Prefer the default config path instead of passing `--config` unless the user clearly wants an alternate file.
- Prefer `nvpn start --connect` for short-lived troubleshooting and `nvpn start --daemon --connect` for desktop-style persistent use.
- Prefer `nvpn create-invite` and `nvpn import-invite` over manual editing of participants, relays, or network ids.
- Prefer `nvpn set` for persistent settings such as autoconnect, join requests, routes, and exit-node selection.
- On macOS, expect tunnel and service operations to require admin privileges.

## Safety rules

- Treat invite URLs, identity keys, private keys, and WireGuard upstream configs as sensitive.
- Do not paste secrets into chat or shell history when a local file or user-run step is safer.
- Confirm before importing an invite from an untrusted source, changing the active network, or editing participant/admin rosters.
- Confirm before enabling exit-node behavior, route advertisement, WireGuard upstream settings, or service install/uninstall because they can affect host networking.
- Prefer `status`, `ip`, `whois`, `ping`, and `doctor` before disruptive actions.
- `nvpn` does not expose a general dry-run mode, so use read-only commands first when validating state.

## Gotchas

- The CLI name is `nvpn`, not `nostr-vpn`.
- `nvpn init` generates identity keys automatically and writes config into the OS config directory.
- Only one saved network is active at a time.
- `nvpn start --daemon --connect` creates a background daemon; `nvpn stop` is what shuts it down.
- `nvpn service install` is the persistent OS-managed path; it is distinct from `start --daemon`.
- macOS may require `sudo nvpn start --connect` or `sudo nvpn service install` for tunnel setup.
- LAN invite broadcast and discovery run until timeout or `Ctrl-C`.
- Importing an invite may queue a join request rather than granting immediate access, depending on the network's admin settings.
