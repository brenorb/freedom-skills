# `nvpn` command patterns

Read this file after resolving the executable as described in `SKILL.md` and `command-discovery.md`. The examples use `$NVPN` for the resolved absolute executable and `$NVPN_CONFIG` for the intended identity's persistent absolute config path. On PowerShell, use `& $nvpn` and `--config $nvpnConfig`. Choose only the operation requested; these examples are alternatives.

## Verify installation and runtime state

```bash
"$NVPN" version --json
"$NVPN" --help
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" service status --config "$NVPN_CONFIG" --json
```

## Initialize and join a network

Initialize a new identity only when requested, as its intended owner. Existing identities skip this command:

```bash
"$NVPN" init --config "$NVPN_CONFIG"
```

Generate a terminal join QR and wait for admin approval:

```bash
"$NVPN" join-request --config "$NVPN_CONFIG"
```

Print only the link, or replace a pending request:

```bash
"$NVPN" join-request --config "$NVPN_CONFIG" --no-wait --no-qr
"$NVPN" join-request --config "$NVPN_CONFIG" --reset
```

Join with values exchanged out of band:

```bash
"$NVPN" join-manual --config "$NVPN_CONFIG" \
  --admin-device-id ADMIN_DEVICE_ID \
  --network-id NETWORK_ID \
  --json
```

Older online documentation may mention `create-invite`, `import-invite`, `invite-broadcast`, or `discover`. Check `"$NVPN" --help` before using those commands: command names have changed across releases.

## Headless join capabilities

Use the installed binary's help rather than assuming that a source guide or a version number guarantees a command. Request output can use JSON when advertised; otherwise use the supported link flow for review in the admin app:

```bash
if "$NVPN" join-request --help | grep -q -- '--json'; then
  "$NVPN" join-request --config "$NVPN_CONFIG" --json
else
  "$NVPN" join-request --config "$NVPN_CONFIG" --no-wait --no-qr
fi
```

For an explicitly requested admin inspection, first check whether headless commands exist:

```bash
if "$NVPN" join-requests --help >/dev/null 2>&1; then
  "$NVPN" join-requests list --config "$NVPN_CONFIG" --json
else
  printf '%s\n' "Use the admin app to review the join request."
fi
```

Listing or inspecting a request does not authorize approval. Review the intended device and active network, and approve only when the user has authorized that membership change. If even the interactive join command is unsupported, stop and use the supported admin-app workflow; do not silently install a different build.

## Session lifecycle

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

Pause, resume, reload, or repair local network state:

```bash
"$NVPN" pause --config "$NVPN_CONFIG"
"$NVPN" resume --config "$NVPN_CONFIG"
"$NVPN" reload --config "$NVPN_CONFIG"
"$NVPN" repair-network --config "$NVPN_CONFIG"
```

`connect` runs a foreground FIPS mesh session directly. `start` can select a network/device and interface with `--network-id`, `--device`, and `--iface`.

## Persistent service

```bash
test -f "$NVPN_CONFIG" || { printf '%s\n' "Intended config is missing; stop before service installation." >&2; exit 1; }
sudo "$NVPN" service install --config "$NVPN_CONFIG"
"$NVPN" service status --config "$NVPN_CONFIG" --json
sudo "$NVPN" service disable --config "$NVPN_CONFIG"
sudo "$NVPN" service enable --config "$NVPN_CONFIG"
sudo "$NVPN" service uninstall --config "$NVPN_CONFIG"
```

Use an elevated PowerShell on Windows instead of `sudo`. Confirm service changes before applying them.

## Inspect peers and connectivity

```bash
"$NVPN" status --config "$NVPN_CONFIG" --json
"$NVPN" ip --config "$NVPN_CONFIG" --json
"$NVPN" ip --config "$NVPN_CONFIG" --peer --json
"$NVPN" whois --config "$NVPN_CONFIG" 100.64.0.2 --json
"$NVPN" ping --config "$NVPN_CONFIG" 100.64.0.2
```

## Interpret runtime readiness

Require `status_source == "daemon"` before interpreting `mesh_ready`. Config-derived status, a missing source, or a missing/non-boolean readiness field is unknown. A live `false` means not ready. Service status describes the OS service, not mesh connectivity.

An optional machine check uses Python 3 and returns 0 for ready, 1 for not ready and 2 for unknown:

```bash
"$NVPN" status --config "$NVPN_CONFIG" --json | python3 -c '
import json, sys
try:
    state = json.load(sys.stdin)
except ValueError:
    print("unknown: invalid status JSON")
    sys.exit(2)
if not isinstance(state, dict):
    print("unknown: invalid status JSON")
    sys.exit(2)
ready = state.get("mesh_ready")
if state.get("status_source") != "daemon" or not isinstance(ready, bool):
    print("unknown: no live daemon readiness")
    sys.exit(2)
print("ready" if ready else "not ready")
sys.exit(0 if ready else 1)
'
```

A ready mesh still needs a separate check of the intended application service and its authentication. Do not change routes or start a service merely to turn an unknown result into success.

## Persist node and network settings

Use `set --json` and pass only the fields the user asked to change. Common settings include:

```bash
"$NVPN" set --config "$NVPN_CONFIG" --node-name laptop --autoconnect true --json
"$NVPN" set --config "$NVPN_CONFIG" --exit-node PEER_ID --exit-node-leak-protection true --json
"$NVPN" set --config "$NVPN_CONFIG" --advertise-routes "10.0.0.0/24,10.0.1.0/24" --json
"$NVPN" set --config "$NVPN_CONFIG" --advertise-exit-node true --json
"$NVPN" set --config "$NVPN_CONFIG" --join-requests-enabled true --json
```

The current CLI also exposes endpoint, tunnel-IP, listen-port, DNS, FIPS discovery/WebRTC/LAN discovery, non-roster peer, WireGuard exit, and Cashu paid-exit settings. Run `"$NVPN" set --help` to see the complete version-specific flag set.

## Manage the device/admin roster

These commands change the active network roster. Use `--publish` only when the change should be published immediately:

```bash
"$NVPN" add-device --config "$NVPN_CONFIG" --device DEVICE_ID --json
"$NVPN" remove-device --config "$NVPN_CONFIG" --device DEVICE_ID --json
"$NVPN" add-admin --config "$NVPN_CONFIG" --device DEVICE_ID --json
"$NVPN" remove-admin --config "$NVPN_CONFIG" --device DEVICE_ID --json
"$NVPN" add-device --config "$NVPN_CONFIG" --device DEVICE_ID --publish --json
```

Confirm the target IDs and network before any roster change.

## Diagnostics

```bash
"$NVPN" doctor --config "$NVPN_CONFIG" --json
"$NVPN" doctor --config "$NVPN_CONFIG" --write-bundle /tmp/nvpn-doctor
```

Doctor bundles may contain local network and peer metadata. Treat them as sensitive before sharing.

## WireGuard upstream testing

Handshake-only test; it does not create a tunnel or modify routes. Its `--config-file` is the separate WireGuard provider config, not `$NVPN_CONFIG`:

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
