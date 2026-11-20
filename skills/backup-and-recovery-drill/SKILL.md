---
name: backup-and-recovery-drill
description: Design and run a practical backup recovery exercise for accounts, devices, wallets, projects, or communications without exposing secrets.
---

# Backup and Recovery Drill

Prove recovery before the original device or service is unavailable.

## Workflow

1. Define the asset, acceptable loss, recovery owner, failure scenario, backup
   locations, and any legal or safety constraint.
2. Inventory what is actually required: data, credentials, configuration,
   software versions, keys held elsewhere, contacts, and instructions.
3. Create or inspect backups with encryption and separate access controls; never
   paste secrets into the drill record.
4. Restore into a clean test environment or spare device, verify integrity and
   usability, and measure what the owner had to remember or improvise.
5. Fix gaps, record the last successful drill, set a review trigger, and safely
   clean the test copy when the user confirms.

Do not declare a backup valid because it exists or has a recent timestamp.

## Minimal check

The intended owner completes a clean restore and can identify the next recovery
step without relying on the original device.
