---
name: blossom-storage
description: Use when the user wants to upload, download, verify, mirror, list, delete, or recover files on Blossom blob servers, especially through the Rust `blossom-cli` client, Nostr-authenticated storage, hash-addressed media, or multi-server preservation workflows.
---

# Blossom Storage

Use the bundled `uvx` wrapper as the execution layer. The wrapper delegates to the external Rust `blossom-cli` binary from the `MonumentalSystems/blossom-rs` project; it does not vendor or reimplement that client. Keep this skill focused on safe, repeatable workflows around the CLI.

## Default workflow

1. Identify the local file or blob hash, the requested operation, and the intended Blossom server. Prefer a server explicitly supplied by the user. Do not silently choose a random public server for sensitive material.
2. Treat uploads, mirrors, metadata publication, and deletions as external or state-changing actions. Confirm the target and scope when the user has not already specified them.
3. For sensitive or politically exposed material, require client-side encryption before upload. A SHA-256 hash verifies integrity; it does not make an unencrypted blob private.
4. Use the bundled wrapper with JSON output. Run `uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom --help` only when command or option placement is uncertain.
5. After every upload or download, verify the SHA-256 hash. Preserve the returned blob descriptor, especially its `sha256`, `url`, `size`, and MIME type.
6. Report the server, hash, URL, verification result, and any publication or mirroring side effects.

Read [references/blossom-cli.md](references/blossom-cli.md) when installation, authentication, version behavior, or command details are needed.

## Run through uvx

Use the bundled wrapper path for all operations:

```bash
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" status
```

The wrapper first checks `BLOSSOM_RUST_CLI_BIN`, then a `blossom-cli` binary on `PATH`, then its versioned cache. If none is available, it uses Cargo to install the pinned Rust release. Set `BLOSSOM_CLI_NO_INSTALL=1` to fail instead of installing, or set `BLOSSOM_CLI_CACHE_DIR` to control the cache location.

For an end-to-end check against an already-running server, set `BLOSSOM_E2E_SERVER` and `BLOSSOM_E2E_SECRET_KEY`, then run `pytest -m e2e`. The test uploads a unique temporary blob, verifies existence and download, and deletes that blob during cleanup. It skips when these variables are absent.

## Upload files

Use the CLI's upload command and request machine-readable output:

```bash
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" upload "/absolute/path/to/file"
```

For the current Rust client, pass `--no-publish` unless the user explicitly wants the upload to publish NIP-94 file metadata or update the Nostr Blossom server list. Confirm the installed version's help output if the flag placement differs.

Before reporting success:

- Check that the returned descriptor contains a 64-character lowercase SHA-256 hash.
- Compare it with the local file hash using `shasum -a 256` or `sha256sum`.
- Distinguish an existing blob from a newly stored blob when the CLI exposes that status.
- Do not expose private keys, authorization tokens, or sensitive local paths in the final report.

## Download and recover blobs

Download by the blob's SHA-256 hash, then verify the resulting file:

```bash
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" download \
  "$SHA256" "/absolute/path/to/output-file"
```

When the original URL is unavailable:

1. Extract the last 64-character hexadecimal string from the URL.
2. Try the user's configured Blossom servers in priority order.
3. Verify the downloaded bytes against the extracted hash.
4. Report which server recovered the blob.

Do not treat a successful HTTP response as proof that the content is correct until the local hash matches.

## Mirror for resilience

Use mirroring only when the user asks for redundancy, preservation, or recovery from a server failure. Mirroring asks a destination server to fetch an existing blob URL; it is not the same as uploading local bytes.

For each destination:

- Confirm the destination server before the request.
- Preserve the source hash and use a narrowly scoped authorization token.
- Verify that the destination descriptor has the same hash, size, and expected MIME type.
- Continue to the next destination only when the user requested multi-server replication.
- Report partial success explicitly; never claim durable preservation from one successful mirror.

## Inspect and delete blobs

Use `exists`, `status`, or `list` for read-only inspection as appropriate:

```bash
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" exists "$SHA256"
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" status
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" list "$PUBKEY"
```

Deletion is destructive. First identify the exact server and hash, show the intended target, and obtain confirmation unless the user has already given unambiguous authorization. Use `--yes` only after confirmation:

```bash
uvx --from "/absolute/path/to/skills/blossom-storage/uvx" blossom \
  --format json --server "$BLOSSOM_SERVER" delete "$SHA256" --yes
```

Never interpret a failed delete as proof that the blob is gone; check the server response and, when appropriate, verify with `exists`.

## Authentication and secrets

- Prefer the user's existing Nostr signer or account integration when the CLI supports it.
- Never print, log, commit, or place an `nsec` in a chat response.
- Avoid passing real private keys directly as command-line arguments because shell history and process inspection may expose them.
- If the installed CLI only accepts a raw key argument, stop before using a high-value key and explain the exposure. A dedicated low-risk identity may be acceptable for a user-approved test.
- Keep authorization tokens short-lived and scoped to the intended operation, server, and blob hash.

## Failure handling

- Do not retry blindly on `401`, `402`, `403`, `413`, or `429`; explain the authentication, payment, authorization, size, or rate-limit condition.
- For reads, try the next explicitly configured server after a transient connection or availability failure.
- For writes, do not silently switch servers or create extra replicas unless the user requested redundancy.
- If the CLI and server disagree about a hash, preserve the local file and report an integrity failure rather than overwriting anything.
- If the CLI is missing, read the installation and version guidance in [references/blossom-cli.md](references/blossom-cli.md) before installing anything.
