---
name: bitcoin-wallet-audit
description: Audit a Bitcoin wallet setup for backup, descriptor, signing, privacy, and recovery risks without requesting private keys or seed phrases.
---

# Bitcoin Wallet Audit

Produce a read-only risk report that a wallet owner can act on.

## Workflow

1. Establish wallet type, custody model, devices, network, intended use, and
   recovery assumptions. Never request a seed phrase, private key, or signing
   secret.
2. Inspect public configuration only: descriptors/xpub scope, address type,
   watch-only status, backup locations, signer inventory, fee policy, and
   software/firmware versions.
3. Check whether a new wallet can be restored in a safe test environment and
   whether backups identify the wallet, quorum, derivation paths, and cosigners
   clearly enough to recover.
4. Flag single points of failure, privacy leaks, unsupported assumptions,
   stale backups, and mismatch between policy and actual setup.
5. Return prioritized fixes with a safe verification step for each; do not make
   transactions or change wallet state without separate authorization.

## Minimal check

The report explicitly confirms that no secret material was collected and lists
the public inputs used for every finding.
