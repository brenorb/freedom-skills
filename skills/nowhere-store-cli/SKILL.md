---
name: nowhere-store-cli
description: "Create, update, inspect, sign, encrypt, and operate Nowhere store sites with the local `nowhere` CLI. Use when the user wants a store fragment, needs seller-side order or status management, wants buyer-side checkout automation, or needs to verify store receipts and payments without using hostednowhere.com."
---

# nowhere-store-cli

Start with the `nowhere` subcommand that directly matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create a store: `nowhere create store --input store.json --json`
- Update a store: `nowhere update <store-fragment-or-url> --patch patch.json --json`
- Inspect or verify a store fragment: `nowhere inspect <store>` and `nowhere verify <store> --json`
- Sign with an existing key: `nowhere sign <store> --secret nsec1... --json`
- Encrypt or decrypt: `nowhere encrypt <store> --password ...` and `nowhere decrypt <store> --password ...`

## Action-First Flows

### Build or revise the store

1. Use `create store` for a new store or `update` for an existing store.
2. If the store is real, use the seller's real key at creation or signing time. Do not default to a throwaway key.
3. Confirm the result with `inspect` so the site type is `store` and the expected name, items, and tags are present.

### Buyer-side checkout

1. Quote first: `nowhere store checkout quote <store> --cart cart.json --buyer-country US --json`
2. Begin checkout only after the quote looks correct:
   - Lightning: `nowhere store checkout begin <store> --cart cart.json --buyer buyer.json --method bitcoin --json`
   - Manual methods: `nowhere store checkout begin <store> --cart cart.json --buyer buyer.json --method payid --json`
3. Save the returned receipt payload. It is the only proof of the order.

### Seller-side operations

1. Publish buyer orders with `nowhere store order <store> --input order.json --json` when the task already has a fully assembled order payload.
2. Decrypt a receipt with `nowhere store receipt decrypt --input receipt.json --secret nsec1... --json`
3. Fetch seller-visible orders with `nowhere store orders <store> --secret nsec1... --json`
4. Verify payments or receipts with `nowhere store verify <store> --input receipt.json --secret nsec1... --json`
5. Manage inventory/status with:
   - `nowhere store status publish <store> --input status.json --secret nsec1... --json`
   - `nowhere store status fetch <store> --json`

## Inputs To Prepare

- `store.json`: upstream Nowhere store codec shape
- `cart.json`: `{ "items": [{ "i": 0, "qty": 1, "v": "Large" }] }`
- `buyer.json`: checkout fields such as `name`, `email`, `street`, `city`, `country`, `refundAddress`
- `status.json`: encrypted inventory/status payload with `items`, `variants`, `low`, `notice`, `closed`, or `redirect`

## Sharp Edges

- Stores are key-ownership-sensitive. If the seller does not control the key, they may not be able to read orders or manage status later.
- `store checkout quote` is the safest preflight because it resolves shipping, discounts, buyer-field requirements, country rules, payment methods, and inventory gating from the live store data.
- `store checkout begin` publishes the order immediately. Do not call it just to inspect possibilities.
- `store order` expects wire-format cent fields. `store checkout begin` handles that assembly for you.
- When tag `k` enables inventory, a missing status payload can block checkout.
- Use repeated `--relay` flags when the task needs explicit relay targeting for tests or isolated environments.
