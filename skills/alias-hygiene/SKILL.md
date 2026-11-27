---
name: alias-hygiene
description: Review an alias or pseudonym for accidental reuse across handles, domains, files, and recovery channels before publication.
---

# Alias Hygiene

Prevent easy cross-context collisions without pretending a unique handle is
anonymous.

## Workflow

1. Define the alias's intended context and search boundary; do not search
   private or restricted data without authorization.
2. Check exact and near-exact reuse across usernames, email local-parts,
   domains, avatars, filenames, PGP/Nostr identities, and public bios.
3. Inspect registration and recovery details the user controls for accidental
   reuse, and distinguish a collision from evidence of the same operator.
4. Recommend one change at a time, preserving account recovery and avoiding
   destructive renames until dependencies are known.
5. Record residual public links and an expiry date for re-review.

Do not publish a dossier of unrelated people sharing an alias.

## Minimal check

The audit records the checked namespaces, date, evidence links, and confidence
for every suspected reuse.
