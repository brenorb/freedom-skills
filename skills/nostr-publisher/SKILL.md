---
name: nostr-publisher
description: Draft and publish Nostr notes, threads, long-form posts, and announcements with relay selection, key safety, and final-send confirmation.
---

# Nostr Publisher

Prepare a publication once and make its audience, relays, identity, and
permanence visible before sending.

## Workflow

1. Confirm content, author identity, audience, tags, language, relay set, and
   whether the post is a note, thread, article, or event announcement.
2. Review links, mentions, quoted claims, attachments, metadata, and accidental
   private context. Use a draft file before touching signing keys.
3. Inspect relay reachability and publication behavior; avoid assuming a relay
   is private, durable, or censorship-free.
4. Show the exact final event/content to the user before signing or publishing.
   Use the repository's `nostr-cli` workflow when available.
5. Verify event ID, relay acknowledgements, and profile visibility separately;
   an acknowledgement is not guaranteed audience delivery.

Never ask for or print a secret key. Do not publish a draft or DM without
explicit current authorization.

## Minimal check

The final event ID and intended relay set are recorded after publication.
