# Site Behavior

Last reviewed: 2026-06-27
Canonical page: https://labs.second.tech/inspector/

## URL handling

- The page reads VTXO hex from the URL fragment first.
- A shared fragment URL looks like `https://labs.second.tech/inspector/#<hex>`.
- It also accepts inbound `?h=<hex>` and `?vtxo=<hex>` query parameters.
- The page trims whitespace, accepts an optional `0x` prefix, and shows normalized lowercase hex in `Raw encoding`.
- The form submit path writes the hex into `location.hash`, then re-renders from the URL.

## What the page shows

- Summary fields: amount, VTXO ID, policy, server key, exit depth, expiry height, exit delta, and encoding version.
- Exit chain timeline:
  - `On-chain anchor` links to `/tx/<txid>` on `https://mempool.space`.
  - `tx #n` rows represent transitions in the unilateral exit path.
  - Transition labels currently include `Cosigned`, `Hash-locked cosigned`, and `Arkoor (off-chain)`.
  - Expanded rows can show signature status, pubkeys, unlock hash, preimage, tap tweak, fee amount, and sibling outputs.
- `Raw encoding` shows normalized hex and byte length.

## Privacy model

- The page decodes entirely in the browser.
- The source states that pasted hex is not POSTed or sent to an API.
- Shared fragment URLs keep the hex out of server access logs because the fragment is not sent in HTTP requests.
- The fragment still appears in local browser history and is visible to anyone who receives the URL.

## Common decode failures

These are local parsing or validation failures from the page's decoder:

- `odd-length hex string`
- `invalid hex at offset N`
- `unexpected EOF reading ...`
- `invalid Vtxo encoding version: 0x...`
- `trailing bytes after VTXO`
- Oversize or invalid field errors such as bad pubkey prefix, compact_size issues, or unsupported policy and transition type bytes
