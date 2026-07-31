# Rust Blossom CLI reference

This skill uses [`MonumentalSystems/blossom-rs`](https://github.com/MonumentalSystems/blossom-rs)'s `blossom-cli` crate as its backend. The bundled Python package is only an `uvx` launcher; the Rust client remains an external executable.

## Installation and versioning

The skill wrapper installs a pinned release rather than tracking an unreviewed moving target. To run the wrapper from this checkout:

```bash
uvx --from ./skills/blossom-storage/uvx blossom --version
```

The wrapper resolves the Rust binary in this order:

1. `BLOSSOM_RUST_CLI_BIN`, when set.
2. An existing `blossom-cli` executable on `PATH`.
3. The versioned cache under `BLOSSOM_CLI_CACHE_DIR` or the platform cache directory.
4. `cargo install blossom-cli --version 0.5.6 --locked` into its cache.

Set `BLOSSOM_CLI_NO_INSTALL=1` to make missing Rust tooling fail fast. Set `BLOSSOM_CLI_CACHE_DIR` to keep the downloaded binary in a controlled location.

The repository includes an optional E2E test for an existing server. Set `BLOSSOM_E2E_SERVER` and `BLOSSOM_E2E_SECRET_KEY`, then run `pytest -m e2e`. It uses a unique temporary blob and removes it after the lifecycle check; without these variables the test is skipped.

Before relying on a newer Rust release, inspect its help and release notes:

```bash
uvx --from ./skills/blossom-storage/uvx blossom --version
uvx --from ./skills/blossom-storage/uvx blossom --help
```

The CLI is part of a larger Rust workspace that also contains a Blossom library and server. Keep the skill dependent on the client binary only; do not install or run the server unless the user explicitly asks for local infrastructure.

## Core command contract

The documented command surface includes:

| Operation | Command shape | Notes |
|---|---|---|
| Generate a test key | `uvx ... blossom keygen` | Do not use this to replace the user's established signer without confirmation. |
| Upload | `uvx ... blossom upload FILE` | Authenticated; returns a blob descriptor. |
| Download | `uvx ... blossom download SHA256 [OUTPUT]` | May write to a file or stdout depending on arguments. |
| Check existence | `uvx ... blossom exists SHA256` | Prefer JSON output for automation. |
| Delete | `uvx ... blossom delete SHA256 --yes` | Destructive; confirmation is required before `--yes`. |
| List | `uvx ... blossom list PUBKEY` | Listing support depends on the server. |
| Mirror | `uvx ... blossom mirror URL` | Copies a remote blob into the selected server. |
| Inspect server | `uvx ... blossom status` | Use for connectivity and server information. |

Global options include a server selector, an authentication key option, and `--format json|text` in current releases. Confirm exact placement with `uvx --from ./skills/blossom-storage/uvx blossom --help` because the Rust CLI is under active development.

## Important defaults

Current release notes document these behaviors:

- Upload can publish a Nostr `kind:1063` NIP-94 file metadata event.
- Upload can publish a Nostr `kind:10063` Blossom server-list event.
- Both publications can be disabled with `--no-publish`.
- Upload uses streaming rather than buffering the entire file in memory.
- Delete prompts for confirmation unless `--yes` is provided.
- The client supports HTTP and optional Iroh transport paths.

For this skill, publication is opt-in. Use `--no-publish` unless the user explicitly asks to publish metadata or update their server list.

## Protocol and safety context

Blossom blobs are addressed by their SHA-256 hash. The protocol's Nostr authorization uses signed events, commonly kind `24242`, and server-list discovery uses kind `10063`. Hash addressing provides content integrity and deduplication; it does not provide confidentiality.

Encrypt sensitive material before handing it to the CLI. Treat server URLs, public blob URLs, MIME types, and published NIP-94 metadata as potentially observable by the server operator and other parties who obtain the URL.

## Sources

- [Blossom protocol](https://github.com/hzrd149/blossom)
- [BUD-02: blob upload](https://github.com/hzrd149/blossom/blob/master/buds/02.md)
- [BUD-03: user server list](https://github.com/hzrd149/blossom/blob/master/buds/03.md)
- [BUD-04: mirroring blobs](https://github.com/hzrd149/blossom/blob/master/buds/04.md)
- [BUD-11: Nostr authorization](https://github.com/hzrd149/blossom/blob/master/buds/11.md)
- [blossom-rs README](https://github.com/MonumentalSystems/blossom-rs)
- [blossom-rs release notes](https://docs.rs/crate/blossom-rs/latest/source/RELEASE_NOTES.md)
