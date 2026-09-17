# stegg command patterns

Read this file only when the user needs raw `stegg` command variants beyond the default workflow in `SKILL.md`.

## Check the published CLI

```bash
uvx stegg --help
uvx stegg encode-cmd --help
uvx stegg decode-cmd --help
uvx --with 'stegg[crypto]' stegg info-cmd
```

## Encode a short demo message

Use for low-risk tests only:

```bash
uvx stegg encode-cmd -i carrier.png -t "hello from stegg" -o stego.png -q
```

## Encode a file payload

Preferred for anything operational:

```bash
uvx stegg encode-cmd -i carrier.png -f payload.bin -o stego.png -q
```

## Encode with randomized placement

Use when the user explicitly wants a less obvious embedding pattern:

```bash
uvx stegg encode-cmd -i carrier.png -f payload.bin -o stego.png -s randomized --seed 12345 -q
```

## Check built-in crypto availability

```bash
uvx --with 'stegg[crypto]' stegg info-cmd
```

## Encode with built-in crypto

Use this only when the user explicitly wants ST3GG's built-in encryption and understands the passphrase handling tradeoff:

```bash
uvx --with 'stegg[crypto]' stegg encode-cmd -i carrier.png -f payload.bin -o stego.png -p "passphrase" -q
```

## Decode to the terminal

Good for text payloads and quick verification:

```bash
uvx stegg decode-cmd -i stego.png -q
```

## Decode to a file

Good for binary payloads or encrypted blobs:

```bash
uvx stegg decode-cmd -i stego.png -o extracted.bin -q
```

## Decode raw bytes as hex

Use when the decoded payload is malformed or the user wants low-level inspection:

```bash
uvx stegg decode-cmd -i stego.png --raw -q
```

## Decode with built-in crypto

```bash
uvx --with 'stegg[crypto]' stegg decode-cmd -i stego.png -p "passphrase" -o extracted.bin -q
```

## Analyze a carrier

Treat this as best-effort triage, not the primary workflow:

```bash
uvx stegg analyze suspicious.png
```

## Read a carrier's basic type

Useful before encoding or triage:

```bash
file carrier.png
```
