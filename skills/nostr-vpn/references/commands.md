# nostr-vpn command patterns

Read this file only when the user needs raw `nvpn` command patterns beyond the default workflow in `SKILL.md`.

## Verify install and runtime state

```bash
command -v nvpn
nvpn version --json
nvpn status --json
nvpn service status --json
```

## Initialize config and identity

```bash
nvpn init
```

## Share or join a network with invites

```bash
nvpn create-invite
nvpn import-invite 'nvpn://invite/...'
```

## LAN pairing

Broadcast the current network invite:

```bash
nvpn invite-broadcast --duration-secs 900
```

Listen for nearby invites:

```bash
nvpn discover --json
nvpn discover --accept --json
```

## Session lifecycle

Foreground session:

```bash
nvpn start --connect
```

Background daemon:

```bash
nvpn start --daemon --connect
nvpn pause
nvpn resume
nvpn stop
```

Reload or repair local daemon/network state:

```bash
nvpn reload
nvpn repair-network
```

## Service management

```bash
sudo nvpn service install
nvpn service status --json
sudo nvpn service disable
sudo nvpn service enable
sudo nvpn service uninstall
```

## Inspect peers and routes

```bash
nvpn status --json
nvpn ip --json
nvpn ip --peer --json
nvpn whois 100.64.0.2 --json
nvpn ping 100.64.0.2
```

## Diagnostics

```bash
nvpn doctor --json
nvpn doctor --write-bundle /tmp/nvpn-doctor
```

## Persist settings

Enable autoconnect:

```bash
nvpn set --autoconnect true --json
```

Enable join requests on the active network:

```bash
nvpn set --join-requests-enabled true --json
```

Advertise routes or exit-node capability:

```bash
nvpn set --advertise-routes "10.0.0.0/24,10.0.1.0/24" --json
nvpn set --advertise-exit-node true --json
```

Select an exit node and leak protection:

```bash
nvpn set --exit-node "PEER_NODE_ID_OR_NAME" --exit-node-leak-protection true --json
```

## Participant and admin roster changes

```bash
nvpn add-participant --participant npub1... --json
nvpn remove-participant --participant npub1... --json
nvpn add-admin --participant npub1... --json
nvpn remove-admin --participant npub1... --json
```

Add `--publish` when the change should be published immediately:

```bash
nvpn add-participant --participant npub1... --publish --json
```

## WireGuard upstream testing

Handshake-only test without replacing the host default route:

```bash
nvpn wg-upstream-test --config-file /path/to/provider.conf
```

Scoped or full-route tests can change live routing and generally require admin privileges:

```bash
sudo nvpn wg-upstream-test --config-file /path/to/provider.conf --scoped-host 1.1.1.1
sudo nvpn wg-upstream-test --config-file /path/to/provider.conf --replace-default --probe-target 1.1.1.1
```
