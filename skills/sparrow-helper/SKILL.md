---
name: sparrow-helper
description: Guide read-only Sparrow Wallet tasks such as labels, UTXO review, import/export, watch-only setup, and transaction inspection.
---

# Sparrow Helper

Use Sparrow's clear wallet and transaction views without turning a review into
an accidental spend.

## Workflow

1. Confirm wallet name, network, mode (watch-only or signing), and the exact
   task. Back up before structural changes.
2. For labels and UTXOs, inspect address reuse, confirmations, amounts, coin
   control, privacy grouping, and spend status before editing.
3. For import/export, verify descriptor, network, derivation path, policy, and
   checksum; keep exports restricted and never export private material by
   default.
4. For a transaction, use the `psbt-assistant` review before signing or
   broadcasting and confirm hardware-wallet display values.
5. Verify changes in Sparrow and preserve a rollback/export path for labels or
   wallet configuration.

Do not delete wallets, consolidate coins, or broadcast without explicit,
current authorization.

## Minimal check

After every change, reopen the affected wallet view and confirm the expected
network, policy, labels, and balances.
