---
name: ark-vtxo-inspector
description: Use this skill when the user wants to decode or inspect Ark VTXO hex with the public https://labs.second.tech/inspector/ page, explain the exit chain or signatures, check policy and expiry details, or share a browser-only inspector link built from a VTXO hex string.
---

# Ark VTXO Inspector

Use the public Second Labs VTXO Inspector for browser-side decoding of Ark VTXO hex.

## Default workflow

1. If you already have the VTXO hex, open the inspector directly with a fragment URL instead of loading the blank page first:

```text
https://labs.second.tech/inspector/#<hex>
```

2. If the user already shared an inspector URL, open that exact URL instead of rebuilding it.
3. Read the summary section first: amount, VTXO ID, policy, server key, exit depth, expiry height, exit delta, and encoding version.
4. Read the exit chain from top to bottom:
   - `On-chain anchor` is the funding outpoint on the explorer.
   - Each `tx #n` row is one transition in the unilateral exit path.
   - `This VTXO` is the final virtual output being inspected.
5. Expand individual transitions when the user needs details such as signature presence, cosigner keys, unlock hash or preimage, tap tweak, sibling outputs, or fee amount.
6. Expand `Raw encoding` only when the user needs the normalized hex or exact byte length.
7. If decoding fails, preserve the exact error message and read `references/site-behavior.md` for the page's URL rules, field meanings, and common parser failures.

## Defaults

- Prefer fragment links (`#<hex>`) over query parameters or manual paste.
- Prefer the inspector's summary and timeline surfaces before diving into raw encoding.
- Treat the hex input as case-insensitive and optional-`0x` prefixed.
- Treat explorer links as convenience context, not proof that the VTXO is spendable or current.

## Safety rules

- Treat VTXO hex and share URLs as potentially sensitive transaction metadata.
- Do not share an inspector URL externally without confirmation.
- Call out the privacy model accurately: the page decodes in the browser and keeps the hex out of server access logs when it stays in the URL fragment, but the fragment still appears in local browser history.

## Gotchas

- The page also accepts `?h=` and `?vtxo=` inbound links, but the fragment form is the intended sharing path.
- Decode failures are local parser or validation errors, not network errors.
- When the exit chain has more than three transitions, the middle transitions may start collapsed behind a `Show ... more transitions` control.
- A VTXO with no exit-chain steps is still valid; the page explains that it is a virtual representation of an on-chain UTXO.
