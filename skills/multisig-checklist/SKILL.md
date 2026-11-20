---
name: multisig-checklist
description: Design and review a Bitcoin multisig setup, recovery drill, signer rotation, and spending policy without handling seed phrases.
---

# Multisig Checklist

Make quorum, failure, and recovery assumptions explicit before funds depend on
them.

## Workflow

1. Record purpose, threat model, quorum, number of signers, jurisdictions,
   devices, coordinator, network, descriptor, derivation path, and fee policy.
2. Verify each signer independently, capture public wallet metadata, and compare
   the resulting descriptor and address derivation on at least two devices.
3. Store backups and recovery instructions in separate controlled locations;
   document what happens when one signer, device, coordinator, or location is
   unavailable.
4. Run a small-value receive, restore, and spend drill before production use.
5. Define signer replacement, emergency spend, inheritance, and revocation
   procedures with human approval gates.

Never request or record seed phrases. A multisig label or descriptor is not a
complete backup unless the signer material and policy can be reconstructed.

## Minimal check

The recovery drill demonstrates the intended quorum using test funds and leaves
an auditable result.
