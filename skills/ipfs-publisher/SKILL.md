---
name: ipfs-publisher
description: Publish a reviewed public artifact to IPFS, capture its CID, verify retrieval, and explain pinning and permanence tradeoffs.
---

# IPFS Publisher

Publish content-addressed material only after the user understands that a CID
can remain discoverable even if the originating site is removed.

## Workflow

1. Confirm the exact files, directory layout, and whether public publication is
   authorized and appropriate.
2. Check for secrets, private metadata, analytics, local paths, and unintended
   files before adding anything.
3. Add the bundle with the available IPFS CLI or service and capture the
   resulting CID plus the client/version used.
4. Retrieve the CID through an independent gateway or local node and compare
   file names, sizes, and SHA-256 hashes with the source bundle.
5. Explain whether the CID is merely available, locally pinned, or pinned by a
   durable service; do not conflate those states.

Do not publish private or legally sensitive material by default. Treat gateway
URLs as transport choices, not proof of persistence.

## Minimal check

The reported CID must retrieve the expected files and reproduce the pre-upload
hash manifest.
