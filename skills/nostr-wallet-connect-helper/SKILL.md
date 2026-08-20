---
name: nostr-wallet-connect-helper
description: Configure and troubleshoot Nostr Wallet Connect permissions, budgets, relays, and app connections without over-granting wallet authority.
---

# Nostr Wallet Connect Helper

Make an NWC connection narrow, legible, and revocable.

## Workflow

1. Identify app, wallet service, intended methods, budget, expiry, relay path,
   and whether the connection is for a test or production wallet.
2. Inspect the current connection and permissions before creating another;
   keep connection strings out of chat, source control, and logs.
3. Request only the methods and amount/time limits needed. Show the user the
   exact spending authority before saving or sharing the connection.
4. Run a read-only balance/status check or a tiny authorized test; distinguish
   app success from wallet settlement.
5. Revoke, rotate, or narrow stale connections and record the remaining
   connections without recording secrets.

Never approve a payment, broaden a budget, or share a connection string based
on an implied request.

## Minimal check

The final report names the allowed methods, budget, expiry, and revocation path.
