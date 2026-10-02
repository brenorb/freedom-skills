# Nostr VPN onboarding

Read this file only when `nvpn` is missing, the user needs first-time setup, or the local config/network state is not usable yet. Resolve the executable first using `references/command-discovery.md`.

## Verify the local state

```bash
"$NVPN" version --json
"$NVPN" status --json
"$NVPN" service status --json
```

`nvpn` stores config in the OS config directory by default:

- Linux: `~/.config/nvpn/config.toml`
- macOS: `~/Library/Application Support/nvpn/config.toml`
- Fallback: `./nvpn.toml`

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

Initialize local identity and config:

```bash
"$NVPN" init
```

Request access to a network and show a terminal QR:

```bash
"$NVPN" join-request
```

For a non-interactive request, print only the link:

```bash
"$NVPN" join-request --no-wait --no-qr
```

For manual joining with values received from an admin:

```bash
"$NVPN" join-manual \
  --admin-device-id ADMIN_DEVICE_ID \
  --network-id NETWORK_ID \
  --json
```

Some releases have older invite/broadcast command names. Run `"$NVPN" --help` and follow the installed binary's interface.

## Start the VPN

Foreground session:

```bash
"$NVPN" start --connect
```

Background daemon:

```bash
"$NVPN" start --daemon --connect
"$NVPN" status --json
"$NVPN" stop
```

Persistent OS-managed service:

```bash
sudo "$NVPN" service install
"$NVPN" service status --json
```

On Windows, run the service command from an elevated PowerShell instead of using `sudo`.

## First troubleshooting checks

```bash
"$NVPN" status --json
"$NVPN" ip --peer --json
"$NVPN" doctor --json
```

If tunnel creation fails on macOS, retry with elevation:

```bash
sudo "$NVPN" start --connect
```

Do not expose join links, QR codes, identity keys, private keys, or diagnostic bundles in chat or public issue reports.
