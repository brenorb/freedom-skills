---
name: mirror-finder
description: Locate surviving copies of removed or blocked public content across archives, caches, IPFS, onion mirrors, and community mirrors.
---

# Mirror Finder

Find the closest surviving copy of a public resource and explain how closely
it matches the requested original.

## Workflow

1. Normalize the target URL and preserve the exact path, query, and date of the
   missing resource.
2. Check the Wayback availability/history first, then search the Internet
   Archive, known site mirrors, IPFS gateways, and onion mirrors when relevant.
3. Compare title, author, publication date, canonical URL, content hash, and
   visible revision markers. Separate exact copies from excerpts and references.
4. Return a ranked table with source URL, capture date, match quality, access
   requirements, and evidence supporting the match.
5. Save a local copy only when requested and pass it to `archive-everything`
   for a durable evidence bundle.

Do not treat search-engine snippets, repost claims, or a matching title as
proof of identity. Avoid putting sensitive URLs into untrusted search services.

## Minimal check

For the selected mirror, record at least one independent corroborating field
(hash, date, author, canonical link, or archive timestamp).
