# Nostr VPN onboarding

Read this file only when `nvpn` is missing, the user needs first-time setup, or the local config/network state is not usable yet. Resolve the executable first using `references/command-discovery.md`.

## Verify the local state

```bash
"$NVPN" version --json
```

## Select the intended identity

Choose the existing identity's config, resolve its absolute path once and keep it in `$NVPN_CONFIG`. The path `/absolute/path/to/nvpn/config.toml` is a placeholder; do not initialize there or choose a new path when the task is to use an existing identity. Default directories vary with the OS, user and service context. An environment variable used by an interactive shell may also be absent under elevation, so every example passes `--config` explicitly.

For Bash on Linux/macOS, reject an unset or relative selection before using the examples:

```bash
case "${NVPN_CONFIG:-}" in
  /*) ;;
  *) printf '%s\n' "Select the intended absolute NVPN_CONFIG path first." >&2; exit 2 ;;
esac
```

Keep the config and all key sidecars together. Preserve the intended owner; only that user and the authorized service account should have access. On Unix, use a private directory and owner-only config/key files. On Windows, preserve equivalent per-user/service ACLs. Do not make files world-readable, copy identities or change ownership blindly to work around access errors. A service may need privileged access, but a new root-owned identity is not a repair for an unknown config.

Set an absolute `$nvpnConfig` in PowerShell and use `& $nvpn ... --config $nvpnConfig`. Pass the same absolute value explicitly in an elevated PowerShell; do not assume variables from another shell are available. Consult the configured service if its path is uncertain; stop rather than guessing.

After selecting the intended config, inspect its runtime and service state:

```bash
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" service status --config "$NVPN_CONFIG" --json
```

## Install

### Cargo

```bash
cargo install nvpn
"$NVPN" version --json
```

### Prebuilt releases

Official release artifacts live at:

- `https://github.com/mmalmi/nostr-vpn/releases/latest`
- `https://git.iris.to/#/npub1xdhnr9mrv47kkrn95k6cwecearydeh8e895990n3acntwvmgk2dsdeeycm/nostr-vpn?tab=releases`

Release availability is platform- and architecture-specific. Check the current release notes before choosing an artifact. If the desktop app is already installed, first look for its bundled CLI using `references/command-discovery.md` instead of installing a second copy.

## Create or join a network

Initialize only when the user requested a new identity; run as its intended owner. Existing identities skip this step:

```bash
"$NVPN" init --config "$NVPN_CONFIG"
```

Request access to a network and show a terminal QR:

```bash
"$NVPN" join-request --config "$NVPN_CONFIG"
```

For a non-interactive request, print only the link:

```bash
"$NVPN" join-request --config "$NVPN_CONFIG" --no-wait --no-qr
```

For manual joining with values received from an admin:

```bash
"$NVPN" join-manual --config "$NVPN_CONFIG" \
  --admin-device-id ADMIN_DEVICE_ID \
  --network-id NETWORK_ID \
  --json
```

Some releases have older invite/broadcast command names. Run `"$NVPN" --help` and follow the installed binary's interface.

## Start the VPN

Foreground session:

```bash
"$NVPN" start --config "$NVPN_CONFIG" --connect
```

Background daemon:

```bash
"$NVPN" start --config "$NVPN_CONFIG" --daemon --connect
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" stop --config "$NVPN_CONFIG"
```

Persistent OS-managed service:

```bash
test -f "$NVPN_CONFIG" || { printf '%s\n' "Intended config is missing; stop before service installation." >&2; exit 1; }
sudo "$NVPN" service install --config "$NVPN_CONFIG"
"$NVPN" service status --config "$NVPN_CONFIG" --json
```

On Windows, run the service command from an elevated PowerShell instead of using `sudo`, while passing the same absolute `$nvpnConfig`. Never omit the config argument to retry a permission failure.

## First troubleshooting checks

```bash
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" ip --config "$NVPN_CONFIG" --peer --json
"$NVPN" doctor --config "$NVPN_CONFIG" --json
```

If tunnel creation fails on macOS, retry with elevation:

```bash
sudo "$NVPN" start --config "$NVPN_CONFIG" --connect
```

Do not expose join links, QR codes, identity keys, private keys, or diagnostic bundles in chat or public issue reports.


## Readiness and version compatibility

`status_source: "config"` describes configuration, not a live connection; its `mesh_ready` is unknown. Require `status_source: "daemon"` before treating a boolean `mesh_ready` as runtime evidence. A service being installed/running, configured peers, or a successful mesh ping does not establish that the intended application service is reachable. Check that service separately within the user's task scope.

The command/config and JSON contracts were reviewed in the published [4.1.20 release](https://github.com/mmalmi/nostr-vpn/releases/tag/v4.1.20), source [`5e8c0efd322c8ae3fdb18e212fbfd1b012046cd9`](https://github.com/mmalmi/nostr-vpn/tree/5e8c0efd322c8ae3fdb18e212fbfd1b012046cd9). Its tagged CLI source includes `join-request --json` and `join-requests`, although the agent guide still calls them source-only. Treat the installed binary's help as the capability gate; do not infer support from older guidance or automatically build an unreleased checkout. Older clients can use the supported interactive join/admin-app approval flow.

Validation for this update uses synthetic config identifiers, status JSON and argv-only CLI/elevation stubs. It does not execute `nvpn`, create identity keys, install a service, change routes or establish a VPN. Platform permissions and actual service/mesh operation remain unverified.
