# Blossom CLI command reference

Read this file when a requested command is not in the default workflow, uv cannot resolve the package, authentication is required, or option placement is uncertain.

## Contents

- [Execution contract](#execution-contract)
- [Core commands](#core-commands)
- [Authentication](#authentication)
- [uv resolution failures](#uv-resolution-failures)
- [Output and verification](#output-and-verification)
- [Sources](#sources)

## Execution contract

Use the PyPI package directly and ephemerally:

```bash
uvx --no-config blossom-cli --version
uvx --no-config blossom-cli --help
```

Do not run `pip install`, `uv tool install`, or `cargo install` as onboarding. The published Python package provides the `blossom-cli` command and supported platform wheels bundle the pinned Rust executable.

`--no-config` belongs to `uvx` and must appear before `blossom-cli`. Rust CLI global options such as `--server`, `--format`, and `--no-publish` belong after `blossom-cli` and before the subcommand. Subcommand-specific options belong after the subcommand.

If reproducibility requires an exact Python wrapper release, request it explicitly:

```bash
uvx --no-config blossom-cli@VERSION --version
```

Use the latest published release by default.

## Core commands

| Goal | Command after `uvx --no-config blossom-cli` | Notes |
|---|---|---|
| Inspect version | `--version` | Does not contact a Blossom server. |
| Inspect server | `--server URL --format json status` | Always specify a remote server; the CLI otherwise defaults to localhost. |
| Generate a test identity | `keygen` | Store output securely; do not expose or replace an established identity casually. |
| Upload | `--server URL --format json --no-publish upload FILE` | Remove `--no-publish` only for intentional Nostr publication. |
| Process media | `--server URL --format json --no-publish media FILE` | The returned hash may differ from the source hash. |
| Batch upload | `--server URL --format json --no-publish batch-upload FILE...` | Use `--concurrency N` only when server and network limits are understood. |
| Download | `--server URL --format json download SHA256 [OUTPUT]` | Verify downloaded bytes against `SHA256`. |
| Check existence | `--server URL --format json exists SHA256` | Distinguish absent from unknown/error. |
| List blobs | `--server URL --format json list PUBKEY` | Server support and authorization requirements vary. |
| Mirror | `--server URL --format json --no-publish mirror SOURCE_URL` | Destination fetches the source; verify the returned descriptor. |
| Delete | `--server URL --format json delete SHA256 --yes` | Destructive; use `--yes` only after authorization. |
| Resolve PKARR | `--format json resolve PUBLIC_KEY` | Resolves advertised HTTP and Iroh endpoints; it does not download a blob. |

Run subcommand help after a failure when exact options differ:

```bash
uvx --no-config blossom-cli upload --help
uvx --no-config blossom-cli admin --help
uvx --no-config blossom-cli relay --help
```

## Authentication

Prefer the environment variable supported by the Rust client:

```bash
export BLOSSOM_SECRET_KEY="<secret supplied outside chat>"
```

The current Rust client resolves a signer for upload, media, batch upload, download, existence checks, listing, mirroring, and deletion. `status`, `resolve`, and `keygen` do not require an existing key.

Do not echo the value, include it in diagnostic output, write it into repository files, or pass it with `--key` unless the user understands shell history and process-list exposure. Use a dedicated low-value identity for tests.

Use HTTPS for remote authenticated servers. Signed authorization does not make plaintext HTTP transport confidential.

## uv resolution failures

If plain `uvx blossom-cli ...` says that all versions were filtered by `exclude-newer`, retain `--no-config`:

```bash
uvx --no-config blossom-cli --version
```

This bypasses unrelated project and user uv policy for the ephemeral CLI invocation. Do not edit the user's global uv configuration merely to run the tool.

If the published wheel does not support the current platform, report the platform and wrapper error. Do not install Rust or compile the upstream crate unless the user explicitly requests that fallback. An already-trusted upstream binary can be selected with `BLOSSOM_RUST_CLI_BIN` when available.

If command resolution is still ambiguous, collect only:

```bash
uvx --version
uvx --no-config blossom-cli --version
uvx --no-config blossom-cli --help
```

Do not dump the full environment because it may contain secrets.

## Output and verification

Prefer `--format json` for descriptors and status. Preserve machine-readable output before extracting fields. An upload or mirror descriptor should include a SHA-256 and normally includes URL, size, and content type.

Verify bytes independently:

```bash
shasum -a 256 "/absolute/path/to/file"
sha256sum "/absolute/path/to/file"
```

Use whichever command exists on the current platform; do not require both.

## Sources

- [blossom-cli Python wrapper](https://github.com/brenorb/blossom-cli)
- [MonumentalSystems/blossom-rs](https://github.com/MonumentalSystems/blossom-rs)
- [Blossom protocol BUDs](https://github.com/hzrd149/blossom)
