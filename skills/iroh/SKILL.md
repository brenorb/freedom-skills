---
name: iroh
description: Use this skill when the user wants to test peer-to-peer connectivity with n0-computer/iroh, run the official transfer or search examples from a local iroh checkout, or start a local iroh-relay server for development and self-hosted connectivity experiments.
---

# iroh

Use the official `n0-computer/iroh` source checkout. This upstream repo is primarily a Rust library plus runnable examples and binaries, not a single end-user CLI.

## Default workflow

1. Start with the command that matches the user's goal in a local `iroh` checkout.

To test real connectivity between two devices with the official transfer example:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- provide --env prod
```

On the other device:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --env prod
```

2. For a local-only development setup with your own relay and DNS server, start the upstream binaries in separate terminals:

```bash
cd /absolute/path/to/iroh
cargo run --release --bin iroh-relay --features server -- --dev
```

```bash
cd /absolute/path/to/iroh
cargo run --release --bin iroh-dns-server
```

Then run the transfer example against that local infra:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- provide --env dev
```

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --env dev
```

3. For a simple request-response protocol example built on iroh:

```bash
cd /absolute/path/to/iroh
cargo run --release --example search -- listen "hello-world" "foo-bar" "hello-moon"
```

In another terminal:

```bash
cd /absolute/path/to/iroh
cargo run --release --example search -- query <endpoint-id> hello
```

4. If the user wants raw flags or command discovery, inspect the upstream help before improvising:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- help
cargo run --release --example search -- help
cargo run --release --bin iroh-relay --features server -- --help
```

5. Only fall back to setup or cloning when the first useful command fails because the local checkout or Rust toolchain is missing. In that case, read `references/onboarding.md`.

6. If the user needs more exact command patterns, environment notes, or relay details, read `references/commands.md`.

7. If the sharing or connectivity context is high-risk, surveillance-sensitive, or politically exposed, read `references/trust-assumptions.md` before recommending public relays or publishing endpoint information.

## Defaults

- Prefer the official upstream examples and binaries over inventing a local wrapper.
- Prefer `transfer` to validate real network reachability and throughput between endpoints.
- Prefer `search` when the user needs a minimal example of a custom protocol layered on iroh.
- Prefer explicit `--env prod` or `--env dev` instead of relying on the upstream default environment.
- Prefer `--release` for anything beyond a quick local sanity check.
- Prefer `--all-features` for `transfer`, especially when the workflow uses `--env dev`.
- Prefer self-hosted or tightly controlled relay infrastructure over public relays when the user is handling sensitive identities, locations, or relationships.

## Safety rules

- Treat any cross-device `transfer` run as an external network action.
- Confirm before using public relays or sharing endpoint ids in sensitive contexts.
- Confirm before starting a self-hosted relay on a machine with exposed ports or public ingress.
- For high-risk or surveillance-sensitive contexts, prefer local or self-hosted relay experiments over public relay infrastructure unless the user explicitly accepts that tradeoff.

## Gotchas

- The `iroh` repo is not the same thing as `iroh-blobs`, `iroh-docs`, or `iroh-gossip`. If the user really wants content-addressed blob sync, mutable document sync, or pub-sub overlays, those sibling repos are usually the better fit.
- The transfer example is a connectivity and throughput tool, not a polished file-sharing app.
- `transfer` defaults to the upstream staging environment when `--env` is omitted. Be explicit.
- `--env dev` depends on local relay and DNS infrastructure and needs the right feature set enabled.
- If `IROH_SECRET` is unset, the transfer example generates a fresh identity each run.
