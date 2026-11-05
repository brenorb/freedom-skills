---
name: lightning-ops
description: Inspect and operate Lightning node payments, invoices, channels, liquidity, backups, and health checks with explicit mutation gates.
---

# Lightning Ops

Diagnose the node before changing liquidity or moving funds.

## Workflow

1. Identify implementation, node endpoint, network, operator, and requested
   operation; use read-only health, wallet, channel, and invoice commands first.
2. Check sync, peers, channel states, on-chain balance, pending HTLCs, fees,
   backups, and recent failures.
3. For a payment or channel change, show destination, amount, fee limit,
   expiry, route/peer, and rollback or recovery limits before asking for
   approval.
4. Separate invoice creation, payment authorization, channel mutation, and
   backup changes; do not bundle them into one opaque command.
5. Verify the resulting preimage, payment state, channel state, or backup
   artifact from the node after the operation.

Never paste macaroon, TLS, seed, or private key material into chat or logs.

## Minimal check

Every mutation has a preflight summary and a post-operation state check.
