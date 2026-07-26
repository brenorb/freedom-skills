---
name: bitchat
description: Use this skill when the user wants to install or operate the BitChat CLI for Bluetooth mesh chat, background receiving, public messages, direct messages, files, geohash/Nostr channels, geohash DMs, location lookup, or local diagnostics.
compatibility: Requires the bitchat CLI; Bluetooth LE is needed for mesh workflows and network access is needed for Nostr/geohash workflows.
metadata:
  version: "0.1.0"
  repository: "https://github.com/brenorb/bitchat-cli"
---

# BitChat

Operate the `bitchat` command from the published `bitchat4agents` package or
from a `bitchat-cli` checkout. Keep the two transports clear:

- `mesh` uses nearby Bluetooth LE peers and can work without the internet.
- `geo` uses Nostr relays and therefore sends data over the configured network.

## Keep the listener running

Start the daemon to participate in the mesh network, receiving, sending and routing messages on the background:

```bash
bitchat daemon status
bitchat daemon start --nickname clanker
bitchat daemon status
```

Check status before starting a second daemon. `chat` and `daemon` both need the BLE radio; stop one before running the other. Stop the listener with:

```bash
bitchat daemon stop
```

## Public mesh messages

Send and receive in the public `#mesh` conversation through the daemon:

```bash
bitchat mesh send "message"
bitchat mesh inbox --tail 20
bitchat peers
```

`bitchat send` and `bitchat inbox` are aliases for the same public scope.

## Direct messages

Review received DMs, inspect one conversation, or send text/file content:

```bash
bitchat dm inbox --tail 20
bitchat dm history @bob --tail 20
bitchat dm send @bob "message"
bitchat dm send-file @bob ./file.jpg
```

The daemon prefers a live BLE route. Text DMs may use Nostr fallback only when the peer has a linked Nostr identity and is favorited; configure that explicitly:

```bash
bitchat social link @bob <npub>
bitchat social favorite @bob
```

Files do not use Nostr fallback.
Favoriting is permission for fallback, not proof of a matching identity, an
active phone subscription, or delivery. Local history and relay ACKs are not
proof that the recipient saw the message.

## Geohash channels: send and receive

Derive location channels offline first:

```bash
bitchat geo encode --lat LAT --lon LON --all-levels
bitchat geo levels GEOHASH
bitchat geo decode GEOHASH
```

Subscribe the daemon before expecting background reception, then inspect or
send in the channel:

```bash
bitchat geo watch add GEOHASH
bitchat geo watch list
bitchat geo inbox GEOHASH --tail 20
bitchat geo who GEOHASH
bitchat geo send GEOHASH "message"
```

Geohashes are location disclosures: city-level precision is safer than neighborhood, block, or building precision. The CLI warns at higher precision and requires `--force` for block/building watches or sends. Treat the final geohash as sensitive and do not substitute a fixture geohash for a user's real location.

For a place-name lookup, use the networked command only when the user accepts the third-party geocoding request:

```bash
bitchat geo lookup "place name"
```

## Geohash DMs and location notes

Geohash-scoped DMs are separate from normal mesh DMs:

```bash
bitchat geo dm send GEOHASH @bob "message"
bitchat geo dm history GEOHASH @bob --tail 20
```

Use `geo notes add` only when the user intends to publish a public note tied to an 8-character building geohash; use `geo notes list` to read existing notes.
The geohash and note text are public location data.

## Installing and upgrading

If the command is missing, install it. If it is already installed and needs the latest published version, upgrade it:

using uv:
```bash
uv tool install bitchat4agents
# If already installed:
uv tool upgrade bitchat4agents
bitchat doctor --json
```

or on homebrew:
```bash
brew install brenorb/tap/bitchat-cli
```

`bitchat doctor --json` shows the active state directory, identity, capabilities, proxy policy, and daemon status; do not guess those paths.

## Privacy and diagnostics

For privacy-sensitive Nostr/geohash traffic, inspect the current proxy policy before sending. Only change it when the user requests a specific routing mode:

```bash
bitchat network proxy status --json
bitchat network proxy set tor --policy require
bitchat network proxy test --json
```

`require` fails closed if the proxy is unavailable. `geo lookup`, geohash messages, geohash DMs, location notes, and Nostr fallback all use the outbound network. Run offline checks with:

```bash
bitchat selftest
```

## Guardrails and gotchas

- The package name is `bitchat4agents`, but the installed executable is `bitchat`.
- Avoid using interactive mode. It's meant for humans.
- Before an external send, confirm the final recipient, geohash/channel, and message or file path when any of them is ambiguous. Never invent missing targets or message text.
- A queued send, local history row, or relay acknowledgement is not recipient delivery. Verify with the receiving inbox/device when that distinction matters.
- If `bitchat` is installed but not found, the `uv` tool bin directory is likely missing from `PATH`.
- BLE behavior depends on the host adapter and permissions; use `doctor` and `daemon status` before diagnosing a protocol failure.
