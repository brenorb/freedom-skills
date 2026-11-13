---
name: chain-of-custody-lite
description: Maintain a lightweight evidence handling log with hashes, transfers, access purpose, and derivative relationships.
---

# Chain of Custody Lite

Make ordinary evidence handling auditable without pretending to replace a
forensic or legal chain-of-custody process.

## Workflow

1. Give each item a stable evidence ID and compute a cryptographic hash before
   analysis when possible.
2. Log each custody event: timestamp, actor, action, source/destination,
   purpose, tool/version, and resulting hash.
3. Keep originals immutable and record derivatives as new items that point to
   the original ID and transformation.
4. Separate access permissions from the log; redact personal details in copies
   intended for wider review.
5. Re-hash at handoff and flag any mismatch, missing event, or clock ambiguity.

This is an operational record, not a legal conclusion. Preserve the original
device or storage context when a qualified examiner is required.

## Minimal check

Replaying the log from intake to current state must explain every derivative
and reproduce its recorded hash.
