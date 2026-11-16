# Onboarding

Use this only when the default wrapper flow fails or when you need to explain setup.

## What the wrapper does

- Clones `https://github.com/Bitcoin-PIR/Bitcoin-PIR.git` into `~/.cache/freedom-skills/bitcoin-pir-upstream` if it is missing.
- Validates the root `Cargo.toml` and the native example at `crates/sdk/client/examples/fetch_addresses.rs` (current layout) or `pir-sdk-client/examples/fetch_addresses.rs` (legacy layout), on both the first clone and later cached runs.
- Runs Cargo package `pir-sdk-client`, example `fetch_addresses`, from the workspace root.
- Reuses a valid existing checkout without fetching, checking out another revision, or changing its files. An invalid existing directory produces an error and is left untouched; pass a different `--upstream-dir` or repair it yourself.
- Parses the example output into JSON.

## Requirements

- `git`
- `cargo` with a working Rust toolchain
- Network access to GitHub and the public Bitcoin PIR servers

## First-run cost

- Initial clone: moderate
- Initial Rust build: depends on the selected upstream revision, toolchain and machine
- Later runs are much faster because Cargo reuses the existing build artifacts

## Known-good manual check

```bash
python3 skills/bitcoin-pir/scripts/query_addresses.py 1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb
```

Known-good result during validation on 2026-06-11:

- `synced_height`: `948454`
- address `1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb`
- one UTXO: `951fb4c4c3d1dbb502c7cd0e7efcdd1ec371fed5fedfbcd3b443ad57b95bb43d:373`
- amount: `1600 sats`

## Compatibility provenance

The workspace layout, Cargo package/example names and console-output format were reviewed at upstream [`0f57b114a5c3e94728b78ed8cb0f54efecb48e83`](https://github.com/Bitcoin-PIR/Bitcoin-PIR/tree/0f57b114a5c3e94728b78ed8cb0f54efecb48e83). The restructure moved the example under `crates/sdk/client/`; the Cargo invocation remains `cargo run --release -p pir-sdk-client --example fetch_addresses`.

Compatibility tests use local current/legacy checkout fixtures and output fixtures derived from that example's print format. They cover the first clone, cache reuse and user-supplied checkouts without querying PIR servers. This update did not rebuild the upstream Rust workspace or rerun the historical live query above. New clones follow upstream's default branch; the reviewed SHA records the evidence, not a version pin. Existing checkouts are never silently upgraded.

## Current limitations

- This workflow is address-only.
- It does not do standalone `txid`, outpoint, or transaction-history lookups.
- The upstream example is hard-wired to the public demo servers, so this skill is currently for the public deployment path rather than arbitrary local server URLs.
