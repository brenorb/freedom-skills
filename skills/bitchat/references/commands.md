# bitchat command patterns

Read this file only when the user needs raw command patterns beyond the default workflow in `SKILL.md`.

## Install globally with uv

```bash
uv tool install bitchat4agents
bitchat doctor
```

## Run from a local checkout

```bash
uv sync
uv run bitchat doctor
uv run bitchat chat --nickname alice
```

## Background daemon

```bash
bitchat daemon start --nickname alice
bitchat daemon status
bitchat daemon stop
```

## Public mesh

```bash
bitchat send "hello"
bitchat mesh send "hello #mesh"
bitchat inbox --tail 20
bitchat mesh inbox --tail 20
```

## Direct messages

```bash
bitchat dm inbox
bitchat dm history @bob
bitchat dm send @bob "hello"
bitchat dm send-file @bob ./photo.jpg
```

## Geohash channels

```bash
bitchat geo watch add u4pruy
bitchat geo watch list
bitchat geo inbox u4pruy --tail 20
bitchat geo who u4pruy
bitchat geo send u4pruy "hello #u4pruy"
bitchat geo send u4pruy --pow 12 "hello with pow"
bitchat geo send u4pruy --teleport "hello from a teleported channel"
```

## Geohash helpers

```bash
bitchat geo levels u4pruydqq
bitchat geo encode --lat 37.7749 --lon -122.4194 --all-levels
bitchat geo decode u4pruyd
bitchat geo lookup "Union Square, San Francisco"
```

## Geohash channel metadata and notes

```bash
bitchat geo channel set u4pruy --name "Home" --bookmark --select
bitchat geo channel show u4pruy
bitchat geo channel list
bitchat geo notes add u4pruydq "quiet after 9pm"
bitchat geo notes list u4pruydq
```

## Social trust and fallback

```bash
bitchat social list
bitchat social link @bob <npub>
bitchat social favorite @bob
bitchat social fingerprint @bob
bitchat social verify @bob
```

## Network privacy

```bash
bitchat network proxy set tor --policy require
bitchat network proxy status
bitchat network proxy test
bitchat network proxy disable
```

## File transfer

```bash
bitchat send-file ./photo.jpg
bitchat mesh send-file ./photo.jpg
bitchat dm send-file @bob ./photo.jpg
```

## Diagnostics

```bash
bitchat doctor
bitchat peers
bitchat selftest
```
