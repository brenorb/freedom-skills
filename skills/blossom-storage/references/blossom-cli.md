# Rust Blossom CLI reference

This skill uses [`MonumentalSystems/blossom-rs`](https://github.com/MonumentalSystems/blossom-rs)'s `blossom-cli` crate as its backend.

## Installation and versioning

Install a pinned release rather than tracking an unreviewed moving target:

```bash
cargo install blossom-cli --version 0.5.6
```

Before relying on a newer release, inspect its help and release notes:

```bash
blossom-cli --version
blossom-cli --help
```

The CLI is part of a larger Rust workspace that also contains a Blossom library and server. Keep the skill dependent on the client binary only; do not install or run the server unless the user explicitly asks for local infrastructure.

## Core command contract

The documented command surface includes:

| Operation | Command shape | Notes |
|---|---|---|
| Generate a test key | `blossom-cli keygen` | Do not use this to replace the user's established signer without confirmation. |
| Upload | `blossom-cli upload FILE` | Authenticated; returns a blob descriptor. |
| Download | `blossom-cli download SHA256 [OUTPUT]` | May write to a file or stdout depending on arguments. |
| Check existence | `blossom-cli exists SHA256` | Prefer JSON output for automation. |
| Delete | `blossom-cli delete SHA256 --yes` | Destructive; confirmation is required before `--yes`. |
| List | `blossom-cli list PUBKEY` | Listing support depends on the server. |
| Mirror | `blossom-cli mirror URL` | Copies a remote blob into the selected server. |
| Inspect server | `blossom-cli status` | Use for connectivity and server information. |

Global options include a server selector, an authentication key option, and `--format json|text` in current releases. Confirm exact placement with `blossom-cli --help` because the CLI is under active development.

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
