# Onboarding

Use this only when the default wrapper flow fails or when you need to explain setup.

## What the wrapper does

- Clones `https://github.com/Bitcoin-PIR/Bitcoin-PIR.git` into `~/.cache/freedom-skills/bitcoin-pir-upstream` if it is missing.
- Runs the upstream native example `pir-sdk-client/examples/fetch_addresses.rs`.
- Parses the example output into JSON.

## Requirements

- `git`
- `cargo` with a working Rust toolchain
- Network access to GitHub and the public Bitcoin PIR servers

## First-run cost

- Initial clone: moderate
- Initial Rust build: roughly a minute on this machine during validation
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

## Current limitations

- This workflow is address-only.
- It does not do standalone `txid`, outpoint, or transaction-history lookups.
- The upstream example is hard-wired to the public demo servers, so this skill is currently for the public deployment path rather than arbitrary local server URLs.
