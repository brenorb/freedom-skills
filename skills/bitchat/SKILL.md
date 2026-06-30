---
name: bitchat
description: Use this skill when the user wants to install, configure, troubleshoot, or operate the BitChat CLI for Bluetooth mesh chat, direct messages, geohash/Nostr channels, daemon mode, file transfer, or local protocol checks. It also applies when the user asks to use the published Python package `bitchat4agents` or invoke the terminal command `bitchat`.
---

# bitchat

Use the published `bitchat4agents` package to expose the `bitchat` command, then operate the CLI from the terminal.

## Default workflow

1. Decide whether to use the published package or a local checkout:
   - Prefer the published package for normal usage:

   ```bash
   uv tool install bitchat4agents
   ```

   - Use a local checkout only when the user is developing or testing unreleased code:

   ```bash
   uv sync
   uv run bitchat doctor
   ```

2. Verify the command works and inspect the current local state:

```bash
bitchat doctor
```

3. If the user wants passive receive, start the background daemon before sending anything:

```bash
bitchat daemon start --nickname alice
bitchat daemon status
```

4. Use the bundled command reference when the user needs raw command patterns beyond the defaults here:
   - See `references/commands.md`

## Defaults

- Prefer `uv tool install bitchat4agents` for global installation.
- Prefer `bitchat doctor` before debugging paths, identity, daemon state, or current capabilities.
- Prefer daemon-backed flows for real usage so inbound messages keep recording while no interactive chat is open.
- Prefer `network proxy set tor --policy require` when the user explicitly cares about privacy for Nostr or geohash traffic.
- Prefer `geo levels`, `geo encode`, and `geo decode` for offline location work before `geo lookup`, which may hit a third-party service.
- Prefer `bitchat doctor` output over guessing config paths or feature availability.

## Safety rules

- Confirm before any command that transmits data off-machine:
  - `send`
  - `mesh send`
  - `dm send`
  - `geo send`
  - `geo dm send`
  - `send-file`
  - `mesh send-file`
  - `dm send-file`
- Confirm the final recipient, final geohash, final channel, and final message text before sending.
- Warn before high-precision geohash actions. Building- or block-level geohashes reveal sensitive location detail.
- Treat `geo lookup` as networked. Explain that it may query a third-party geocoding service.
- Do not assume the current config directory name; inspect it with `bitchat doctor`.

## Common tasks

### Start interactive mesh chat

```bash
bitchat chat --nickname alice
```

### Run the daemon and send through it

```bash
bitchat daemon start --nickname alice
bitchat send "hello"
bitchat mesh send "hello #mesh"
bitchat inbox --tail 20
bitchat mesh inbox --tail 20
```

### Inspect peers and private messaging

```bash
bitchat peers
bitchat dm inbox
bitchat dm history @bob
```

### Work with geohash channels

```bash
bitchat geo watch add u4pruy
bitchat geo inbox u4pruy --tail 20
bitchat geo who u4pruy
bitchat geo levels u4pruydqq
bitchat geo encode --lat 37.7749 --lon -122.4194 --all-levels
```

### Run offline checks

```bash
bitchat selftest
```

## Gotchas

- The package name is `bitchat4agents`, but the installed executable is `bitchat`.
- `chat` and `daemon` should not own the radio concurrently.
- Many useful commands assume the daemon is already running.
- BLE behavior is environment-sensitive. If commands look wrong, inspect the exact runtime state with `bitchat doctor` and `bitchat daemon status`.
- If global install works but `bitchat` is not found, the tool bin directory is probably missing from `PATH`.
- Geohash and Nostr features are a different transport surface from local BLE mesh. Diagnose them separately.
