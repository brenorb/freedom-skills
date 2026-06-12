# nostr-vpn onboarding

Read this file only when `nvpn` is missing, the user needs first-time setup, or the local config/network state is not usable yet.

## Verify the local state

```bash
command -v nvpn
nvpn version --json
nvpn status --json
nvpn service status --json
```

`nvpn` stores config in the OS config directory by default:

- Linux: `~/.config/nvpn/config.toml`
- macOS: `~/Library/Application Support/nvpn/config.toml`
- Fallback: `./nvpn.toml`

## Install

### Cargo

```bash
cargo install nvpn
nvpn version --json
```

### Prebuilt releases

Official release artifacts live at:

- `https://github.com/mmalmi/nostr-vpn/releases/latest`
- `https://git.iris.to/#/npub1xdhnr9mrv47kkrn95k6cwecearydeh8e895990n3acntwvmgk2dsdeeycm/nostr-vpn?tab=releases`

Apple Silicon macOS, Linux x64, Windows x64, and Android arm64 have release artifacts. Intel macOS is source-only.

## Create or join a network

Initialize local identity and config:

```bash
nvpn init
```

Create an invite for the active network:

```bash
nvpn create-invite
```

Join from an invite:

```bash
nvpn import-invite 'nvpn://invite/...'
```

For nearby-device pairing on the same LAN:

```bash
nvpn invite-broadcast --duration-secs 900
nvpn discover --accept --json
```

## Start the VPN

Foreground session:

```bash
nvpn start --connect
```

Background daemon:

```bash
nvpn start --daemon --connect
nvpn status --json
nvpn stop
```

Persistent OS-managed service:

```bash
sudo nvpn service install
nvpn service status --json
```

On Windows, run `nvpn service install` from an elevated shell instead of using `sudo`.

## First troubleshooting checks

```bash
nvpn status --json
nvpn ip --peer --json
nvpn doctor --json
```

If tunnel creation fails on macOS, retry with elevation:

```bash
sudo nvpn start --connect
```
