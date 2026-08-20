---
name: nostr-profile-ops
description: Review and maintain a Nostr profile, relay list, NIP-05, follows, and migration plan without exposing secret keys.
---

# Nostr Profile Ops

Treat profile metadata and relay choices as public identity infrastructure.

## Workflow

1. Identify the pubkey/profile and requested change; never accept a secret key
   in chat or logs.
2. Inspect current metadata, relay read/write roles, NIP-05 status, follows,
   lists, client support, and stale or untrusted endpoints.
3. Preview changes to name, picture, bio, website, NIP-05, relay set, or
   follows; highlight correlation and delivery effects.
4. Apply only the approved change through a local signer/client, then query
   independent relays to confirm propagation and distinguish stale caches.
5. Keep an export or rollback plan for profile metadata and relay lists.

Do not claim that NIP-05 proves legal identity or that a relay list makes
events private.

## Minimal check

The post-change report includes event ID, effective fields, relay acknowledgements,
and any relays that did not confirm the update.
