---
name: blossom-cli
description: Use when the user wants to upload, download, verify, mirror, list, delete, or recover files on Blossom blob servers with `blossom-cli`, including Nostr-authenticated storage, hash-addressed media, multi-server replication, or server failure recovery.
---

# Blossom CLI

Run the requested operation through the published `blossom-cli` package with `uvx`. Do not install the CLI first and do not add a second wrapper.

When the user already supplied the file or hash and server, run the matching command first. Do not prepend `command -v`, file-existence probes, key checks, version checks, or setup steps. Diagnose those conditions only if the action fails.

## Upload

When the file and destination server are known, upload immediately:

```bash
uvx blossom-cli \
  --server "$BLOSSOM_SERVER" --format json --no-publish \
  upload "/absolute/path/to/file"
```

Use `BLOSSOM_SECRET_KEY` from the existing environment for blob operations. The current Rust client resolves a signer even when a server permits the eventual read. `status`, `resolve`, and `keygen` do not need this key. Do not put an `nsec` or hex secret directly in the command.

Keep `--no-publish` unless the user explicitly wants to publish NIP-94 file metadata and update their Nostr Blossom server list. After upload:

1. Read the returned descriptor and preserve its `sha256`, `url`, `size`, and content type.
2. Hash the local file with `shasum -a 256` on macOS or `sha256sum` on Linux.
3. Require the local hash to match the descriptor before reporting success.
4. Report the target server and any publication side effects.

## Download or recover

Download by SHA-256 and verify the result:

```bash
uvx blossom-cli \
  --server "$BLOSSOM_SERVER" --format json \
  download "$SHA256" "/absolute/path/to/output-file"
```

Hash the downloaded bytes and require a match. A successful HTTP response alone does not prove integrity.

For recovery, extract the 64-character SHA-256 from the original Blossom URL and try the user's servers in priority order. Try embedded `blossom:` URI server hints before author-discovered or fallback servers. Read [references/protocol-and-edge-cases.md](references/protocol-and-edge-cases.md) before orchestrating fallback across servers.

## Inspect

Run the matching read action directly:

```bash
uvx blossom-cli --server "$BLOSSOM_SERVER" --format json status
uvx blossom-cli --server "$BLOSSOM_SERVER" --format json exists "$SHA256"
uvx blossom-cli --server "$BLOSSOM_SERVER" --format json list "$PUBKEY"
```

Do not treat every non-`404` response as proof that a blob exists. Authentication failures, rate limits, server errors, and timeouts mean presence is unknown. Use the tri-state rules in [references/protocol-and-edge-cases.md](references/protocol-and-edge-cases.md).

## Mirror or replicate

Mirror an existing blob when the source URL and destination server are known:

```bash
uvx blossom-cli \
  --server "$DESTINATION_SERVER" --format json --no-publish \
  mirror "$SOURCE_BLOB_URL"
```

For multiple destinations, upload once and mirror the returned descriptor to the remaining servers. Verify the same hash on every successful destination and report partial success explicitly. If media processing changes the blob, mirror the processed descriptor rather than the original bytes.

Read [references/protocol-and-edge-cases.md](references/protocol-and-edge-cases.md) for preflight, ownership registration, direct-upload fallback, publication ordering, payment challenges, and retry boundaries.

## Delete

Deletion is destructive. Identify the exact server and hash, obtain confirmation unless the user already gave unambiguous authorization, then run:

```bash
uvx blossom-cli \
  --server "$BLOSSOM_SERVER" --format json \
  delete "$SHA256" --yes
```

Do not interpret a failed delete as proof that the blob is gone. Check the response and verify absence when appropriate.

## Safety and failure rules

- Treat uploads, mirrors, metadata publication, payments, and deletions as external state changes. Use only destinations and side effects within the user's request.
- Encrypt sensitive material before upload. Hash addressing proves integrity, not confidentiality.
- Never print, log, commit, or place secret keys in command arguments.
- Do not retry blindly on `401`, `402`, `403`, `413`, `415`, `422`, or `429`.
- Retry or fail over reads after transient network or `5xx` failures. Do not silently create replicas during a read-only request.
- Preserve local data on every integrity mismatch; never overwrite it to make hashes agree.
- Run `uvx blossom-cli --help` when the requested operation is not covered here or an option fails. Use subcommand help for details, for example `uvx blossom-cli upload --help`.
