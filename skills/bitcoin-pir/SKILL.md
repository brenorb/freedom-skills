---
name: bitcoin-pir
description: Use this skill when the user wants a private, read-only Bitcoin UTXO lookup through Bitcoin PIR for one or more Bitcoin addresses, or when you need to test whether the public Bitcoin PIR demo servers can resolve an address to current UTXOs. This skill is not for standalone txid, outpoint, xpub, seed, or historical transaction-history lookups.
---

# bitcoin-pir

Use the bundled wrapper around the upstream `Bitcoin-PIR/Bitcoin-PIR` native example that was verified against the live public servers.

## Default workflow

1. For a read-only address lookup, run the wrapper with one or more Bitcoin addresses:

```bash
python3 skills/bitcoin-pir/scripts/query_addresses.py 1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb
python3 skills/bitcoin-pir/scripts/query_addresses.py bc1q2292d7mz8txc7462hjy4prs2gtx727ut8mcanr
```

2. Read the JSON result:
- `synced_height` is the server tip used for the query.
- `queries[].merkle_verified` should be `true` for a verified result.
- `queries[].utxos` contains `(txid, vout, amount_sats)` for the current UTXO set.

3. If the user wants the raw upstream console output for debugging, rerun with:

```bash
python3 skills/bitcoin-pir/scripts/query_addresses.py --raw bc1q2292d7mz8txc7462hjy4prs2gtx727ut8mcanr
```

4. If the wrapper returns `unsupported_lookup`, stop and explain the limitation plainly: current Bitcoin PIR supports address-to-current-UTXO lookups, not standalone txid/outpoint/history lookups.

5. If the wrapper fails before querying because Rust, Cargo, or the upstream repo is unavailable, read `references/onboarding.md`.

## Defaults

- Prefer the bundled wrapper over ad hoc shell steps because it handles upstream cloning, execution, and JSON parsing.
- Prefer querying one or a few addresses at a time unless the user explicitly wants a larger batch.
- Prefer reporting the exact `txid:vout` entries returned by Bitcoin PIR instead of paraphrasing them away.
- Prefer the default public demo servers for this skill; the wrapper is intentionally scoped to the public upstream example path.

## Safety rules

- Treat this as a read-only external network action against public Bitcoin PIR servers.
- Do not use this skill for seeds, xpubs, private keys, descriptors containing secrets, or anything beyond plain Bitcoin addresses.
- Call out that the queried addresses still become visible inside the agent/LLM context even though Bitcoin PIR hides them from the PIR servers.
- If the user asks for tx history, tx fetch by txid, or outpoint-only lookup, say that Bitcoin PIR does not currently expose that as a standalone workflow here.

## Gotchas

- The first run can take a while because the upstream Rust project may need to clone and compile.
- The wrapper intentionally rejects txids like `abcd...` and outpoints like `txid:vout`; those are not directly supported by the upstream address-query example.
- A `not_found` result means no current UTXOs for that address in the published dataset, not necessarily that the address never had activity.
- `is_whale: true` means the address was excluded upstream because it has too many UTXOs to fit the normal chunking path.
