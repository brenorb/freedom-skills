# iroh commands

Read this file when the default workflow in `SKILL.md` is not enough.

## Show upstream help

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- help
cargo run --release --example search -- help
cargo run --release --bin iroh-relay --features server -- --help
```

## Transfer example

Provide data from one machine:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- provide --env prod
```

Fetch from another machine:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --env prod
```

Useful fetch variants:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --mode upload --duration 30 --env prod
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --mode bidi --size 100M --env prod
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --mode ping --env prod
```

If the remote endpoint needs manual addressing hints:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- fetch \
  <endpoint-id> \
  --remote-relay-url https://relay.example.com. \
  --remote-direct-address 203.0.113.10:4242 \
  --env prod
```

## Local development relay setup

Run the local relay:

```bash
cd /absolute/path/to/iroh
cargo run --release --bin iroh-relay --features server -- --dev
```

Run the local DNS server:

```bash
cd /absolute/path/to/iroh
cargo run --release --bin iroh-dns-server
```

Then run endpoints against the local environment:

```bash
cd /absolute/path/to/iroh
cargo run --release --example transfer --all-features -- provide --env dev
cargo run --release --example transfer --all-features -- fetch <endpoint-id> --env dev
```

## Search example

Start a listening endpoint with sample text:

```bash
cd /absolute/path/to/iroh
cargo run --release --example search -- listen "hello-world" "foo-bar" "hello-moon"
```

Query it from another terminal:

```bash
cd /absolute/path/to/iroh
cargo run --release --example search -- query <endpoint-id> hello
```

## Operational notes

- `transfer provide` prints the endpoint id the peer must dial.
- If `IROH_SECRET` is not set, the transfer example generates a fresh secret key and endpoint identity on each run.
- `transfer` defaults to the upstream staging environment when `--env` is omitted.
- `--env dev` requires the local relay and DNS services from the same repo.
- `iroh-relay -- --dev` is for local development. Do not treat it as a production deployment recipe.

## Upstream references

- Repo README: `https://github.com/n0-computer/iroh/blob/main/README.md`
- Docs site: `https://docs.iroh.computer`
- Transfer example: `https://github.com/n0-computer/iroh/blob/main/iroh/examples/transfer.rs`
- Search example: `https://github.com/n0-computer/iroh/blob/main/iroh/examples/search.rs`
- Relay binary: `https://github.com/n0-computer/iroh/blob/main/iroh-relay/src/main.rs`
