---
name: cashu-ops
description: Inspect and operate Cashu wallets, mints, tokens, swaps, and recovery flows with explicit trust and privacy warnings.
---

# Cashu Ops

Make ecash operations understandable at the mint, token, wallet, and recovery
boundaries.

## Workflow

1. Identify wallet implementation, mint URL, intended operation, amount,
   expiry, recipient, and whether the value is test or production money.
2. Inspect mint metadata, keysets, fees, support, wallet backup, and current
   balance read-only. Treat a mint as a trust and availability dependency.
3. For send, receive, melt, swap, or redeem, preview amount, fee, token
   destination, privacy implications, and failure/recovery path before action.
4. Verify received proofs and wallet state locally; never treat a copied token,
   QR, or relay message as harmless public text.
5. Document backup and mint-migration steps without printing tokens or seed
   material, and test recovery with a small amount where appropriate.

Do not select a mint solely by popularity or promise privacy beyond the actual
protocol and operator model.

## Minimal check

Every money-moving operation has an explicit mint, amount, recipient, fee, and
post-operation wallet check.
