# iroh onboarding

Read this file only when the first useful `iroh` command cannot run because the upstream checkout or Rust toolchain is missing.

## Prerequisites

- Rust toolchain with `cargo`
- `git`
- Enough disk space and build time for a Rust workspace

## Clone the upstream repo

```bash
cd /absolute/path/where/repos/live
git clone https://github.com/n0-computer/iroh.git
cd iroh
```

If the repo already exists locally, prefer reusing that checkout instead of cloning another copy.

## Build the common entrypoints

```bash
cd /absolute/path/to/iroh
cargo build --release --example transfer --all-features
cargo build --release --example search
cargo build --release --bin iroh-relay --features server
```

If the user plans to use the local dev environment from the transfer example comments, also build:

```bash
cd /absolute/path/to/iroh
cargo build --release --bin iroh-dns-server
```

## First command to try after setup

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- help
```

If that works, go back to the main workflow in `SKILL.md` and run the user-facing command that matches the request.

## Notes

- The upstream repo is library-first. Practical command-line workflows come mostly from `cargo run --example ...` and the `iroh-relay` binary.
- If the user needs a stable reusable tool rather than an example, call that out explicitly before building extra wrappers.
- If the user wants blob sync, document sync, or gossip overlays rather than raw transport testing, check whether `iroh-blobs`, `iroh-docs`, or `iroh-gossip` is the real target.
