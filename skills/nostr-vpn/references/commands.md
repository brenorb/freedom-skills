# `nvpn` command patterns

Read this file after resolving the executable as described in `SKILL.md` and `command-discovery.md`. The examples use `$NVPN` for the resolved absolute path. On PowerShell, use `& $nvpn` instead.

## Verify installation and runtime state

```bash
"$NVPN" version --json
"$NVPN" --help
"$NVPN" status --json
"$NVPN" service status --json
```

## Initialize and join a network

Initialize local identity and config:

```bash
"$NVPN" init
```

Generate a terminal join QR and wait for admin approval:

```bash
"$NVPN" join-request
```

Print only the link, or replace a pending request:

```bash
"$NVPN" join-request --no-wait --no-qr
"$NVPN" join-request --reset
```

Join with values exchanged out of band:

```bash
"$NVPN" join-manual \
  --admin-device-id ADMIN_DEVICE_ID \
  --network-id NETWORK_ID \
  --json
```

Older online documentation may mention `create-invite`, `import-invite`, `invite-broadcast`, or `discover`. Check `"$NVPN" --help` before using those commands: command names have changed across releases.

## Session lifecycle

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

Pause, resume, reload, or repair local network state:

```bash
"$NVPN" pause
"$NVPN" resume
"$NVPN" reload
"$NVPN" repair-network
```

`connect` runs a foreground FIPS mesh session directly. `start` can select a network/device and interface with `--network-id`, `--device`, and `--iface`.

## Persistent service

```bash
sudo "$NVPN" service install
"$NVPN" service status --json
sudo "$NVPN" service disable
sudo "$NVPN" service enable
sudo "$NVPN" service uninstall
```

Use an elevated PowerShell on Windows instead of `sudo`. Confirm service changes before applying them.

## Inspect peers and connectivity

```bash
"$NVPN" status --json
"$NVPN" ip --json
"$NVPN" ip --peer --json
"$NVPN" whois 100.64.0.2 --json
"$NVPN" ping 100.64.0.2
```

## Persist node and network settings

Use `set --json` and pass only the fields the user asked to change. Common settings include:

```bash
"$NVPN" set --node-name laptop --autoconnect true --json
"$NVPN" set --exit-node PEER_ID --exit-node-leak-protection true --json
"$NVPN" set --advertise-routes "10.0.0.0/24,10.0.1.0/24" --json
"$NVPN" set --advertise-exit-node true --json
"$NVPN" set --join-requests-enabled true --json
```

The current CLI also exposes endpoint, tunnel-IP, listen-port, DNS, FIPS discovery/WebRTC/LAN discovery, non-roster peer, WireGuard exit, and Cashu paid-exit settings. Run `"$NVPN" set --help` to see the complete version-specific flag set.

## Manage the device/admin roster

These commands change the active network roster. Use `--publish` only when the change should be published immediately:

```bash
"$NVPN" add-device --device DEVICE_ID --json
"$NVPN" remove-device --device DEVICE_ID --json
"$NVPN" add-admin --device DEVICE_ID --json
"$NVPN" remove-admin --device DEVICE_ID --json
"$NVPN" add-device --device DEVICE_ID --publish --json
```

Confirm the target IDs and network before any roster change.

## Diagnostics

```bash
"$NVPN" doctor --json
"$NVPN" doctor --write-bundle /tmp/nvpn-doctor
```

Doctor bundles may contain local network and peer metadata. Treat them as sensitive before sharing.

## WireGuard upstream testing

Handshake-only test; it does not create a tunnel or modify routes:

```bash
"$NVPN" wg-upstream-test --config-file /path/to/provider.conf
```

Scoped test through one host, or a full-route test:

```bash
sudo "$NVPN" wg-upstream-test \
  --config-file /path/to/provider.conf \
  --scoped-host 1.1.1.1

sudo "$NVPN" wg-upstream-test \
  --config-file /path/to/provider.conf \
  --replace-default \
  --probe-target 1.1.1.1
```

`--replace-default` changes live routing and is explicitly dangerous. Confirm before using it.

## Advanced surfaces

The current CLI also exposes:

- `pubsub publish` for signed Nostr control-event JSON files;
- `paid-exit` for Cashu-paid public exit offers, buyer/seller sessions, payments, settlement, and wallet metadata;
- `update`, `install-cli`, and `uninstall-cli` for the CLI binary itself.

Inspect each surface with:

```bash
"$NVPN" pubsub --help
"$NVPN" paid-exit --help
"$NVPN" update --help
```

Do not use these advanced or state-changing commands unless they match the user's explicit goal.
