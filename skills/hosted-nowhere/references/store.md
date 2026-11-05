# Store — deprecated

**Explain the deprecation before using this route.** Hosted Nowhere removed Store
from its tools because public relays need not preserve stock or orders. They may
go offline or discard events; a buyer may pay without the seller reliably
receiving the order. Store remains a demonstration and is not recommended for
live selling. This is a reliability limit, not something that signing a link fixes.
Source: [Hosted Nowhere Store](https://hostednowhere.com/store), checked 2026-10-19.

Continue with an explicitly requested experiment or existing-store operation.
Do not silently create a store for a generic request to sell products.

## Legacy creation and review

```sh
npx --yes nowhere-cli create store --input store.json --json
npx --yes nowhere-cli inspect "$SITE_URL" --json
```

Use [store.json](../examples/store.json) only as a disposable example;
replace the owner key for actual owner operations. Fields include `pubkey`,
`name`, `description`, `image`, `tags`, and `items`. Each item needs `name` and a
numeric `price`; optional item fields include `description`, `image`, and `tags`.
The example uses USD, with a price of `7.5` meaning USD 7.50, and uses the default inventory gate. Do not change a real store's inventory
configuration merely to get checkout to pass.

Browser: first read `https://hostednowhere.com/store`; the legacy builder is
`https://hostednowhere.com/create/store`. Orders are encrypted to the seller key;
using a key the seller does not control can make them unreadable.

## Buyer flow, only when requested

`RELAY` below is the supplied relay URL. Keep it on checkout, order retrieval,
and status operations; omit the override only when default relays are intended.

```sh
npx --yes nowhere-cli store checkout quote "$SITE_URL" --cart cart.json --buyer-country US --json --relay "$RELAY"
npx --yes nowhere-cli store checkout begin "$SITE_URL" --cart cart.json --buyer buyer.json --method bitcoin --json --relay "$RELAY"
```

Cart: `{"items":[{"i":0,"qty":1}]}`; optional `v` selects a variant.
Prepare buyer fields required by the quote, such as `name`, `email`, `street`,
`city`, `country`, and `refundAddress`. Carry the quoted buyer country into
`buyer.json` even when it is optional, and preserve other user-supplied buyer
fields. Use the selected method ID (`bitcoin`,
`payid`, or a returned custom method), never a guessed destination.

Quote resolves shipping, discounts, required fields, countries, payment methods,
and inventory. **Begin immediately publishes an order**; it is not a preview.
Capture checkout output once. `published.receipt` is a serialized JSON string;
`published.receiptPayload` is the same receipt as an object. Save that object
(or parse the string) to `receipt.json` for decrypt/verify commands. Do not pass
the entire checkout response as a receipt. Save it privately before reporting
completion. An order or a
Lightning invoice is not proof of payment. Do not begin again after an ambiguous
timeout: reconcile using the receipt/event ID, seller retrieval, and buyer contact.

## Seller operations

```sh
npx --yes nowhere-cli store orders "$SITE_URL" --secret "$SELLER_SECRET" --json --relay "$RELAY"
npx --yes nowhere-cli store orders "$SITE_URL" --secret "$SELLER_SECRET" --csv --relay "$RELAY"
npx --yes nowhere-cli store receipt decrypt --input receipt.json --secret "$SELLER_SECRET" --json
npx --yes nowhere-cli store verify "$SITE_URL" --input receipt.json --secret "$SELLER_SECRET" --json
npx --yes nowhere-cli store status publish "$SITE_URL" --input status-input.json --secret "$SELLER_SECRET" --json --relay "$RELAY" > status.json
npx --yes nowhere-cli store status fetch "$SITE_URL" --json --relay "$RELAY"
```

`status-input.json` contains the stock/notice input; `status.json` captures the
publication response. Status input may contain `items`, `variants`, `low`, `notice`, `closed`, or
`redirect`; inspect existing state and targeted CLI help before changing it.
Use an existing remote signer via `--use-signer` instead of `--secret` when
configured. Inventory is enabled by the presence of tag `k`, including `k=0`; it can block
checkout if status is missing. **CLI 0.3.0 adds `k=1` when `k` is omitted**, even
on updates. The live builder also requires inventory management during beta.
Do not promise an off switch or repeatedly rewrite the link trying to remove it.
For an authorized disposable checkout experiment, publish stock status first:

```json
{"items":{"0":3},"notice":"Test only"}
```

`items` maps item indexes to stock states: 3 means in stock, 2 low stock, and
0/1 unavailable. Publish this with the intended seller key and selected relay,
then quote and confirm the inventory gate is `ok` before beginning checkout.
For a real store, fetch and preserve existing stock and management state; do not
invent stock to bypass a failure. Explain the required inventory behavior if the
user requests an unsupported inventory-free flow.

For manual PayID in an AUD store, use `{"key":"j","value":"seller@example.com"}`.
Tag `5` is for custom payment configurations; it does not configure built-in
PayID. Verify the quote offers method `payid` with the intended destination before
beginning checkout.
Validate actual payment in the seller's wallet before shipping; seeing an order
in a portal proves neither authenticity nor payment. Check JSON decryption
failures before CSV export and report omitted/unreadable orders.

The low-level `npx --yes nowhere-cli store order "$SITE_URL" --input order.json --json` publishes
an assembled wire-format order with cent-denominated totals. Prefer checkout
assembly; do not reuse catalogue price units as wire-order cents.

Use repeated `--relay` overrides for isolated tests. Store inventory lookups depend
on the fragment; edits can change the namespace. Preserve original URLs and
receipts to retrieve old state. Relay acknowledgement never guarantees retention.
