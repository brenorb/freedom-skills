---
name: archive-everything
description: Build a durable evidence bundle for one or more public URLs, including archive snapshots, local copies, hashes, and provenance.
---

# Archive Everything

Create a reproducible archive bundle before a public page changes or disappears.

## Workflow

1. Confirm the URL list, whether submission to third-party archives is allowed,
   and whether the content is safe to make public.
2. Use the repository's `wayback-archive` workflow for Wayback availability,
   capture, and timestamps. A lookup is not a fresh capture.
3. Save the response body or a complete local copy when the user needs an
   offline artifact. Record the original URL, final URL, capture time, and
   retrieval command.
4. Generate SHA-256 hashes for every saved file and write a small manifest
   mapping each path to its URL, timestamp, media type, and hash.
5. Add PDF, screenshot, or IPFS outputs only when requested; call out that
   public publication is durable and potentially irreversible.

Do not claim that an archive submission succeeded without a returned snapshot
URL. Do not upload private material or follow links outside the requested
scope.

## Minimal check

Re-hash the bundle after creation and verify that every manifest path exists and
matches its recorded SHA-256.
