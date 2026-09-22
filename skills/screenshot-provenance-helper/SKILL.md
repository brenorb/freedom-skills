---
name: screenshot-provenance-helper
description: Record the origin, capture context, timestamp, transformations, and supporting evidence for a screenshot without treating pixels as self-authenticating.
---

# Screenshot Provenance Helper

Make a screenshot reviewable later by preserving context around the pixels.

## Workflow

1. Preserve the original file and record who supplied it, how it was captured,
   source application/page, visible URL, device/time context, and hash.
2. Capture supporting context separately: surrounding page, archive snapshot,
   event log, source message, or independent observer.
3. Note cropping, scaling, OCR, annotation, redaction, and export operations as
   derivatives linked to the original.
4. Check visible UI, clocks, URLs, usernames, notifications, and metadata for
   contradictions or accidental personal data.
5. Package a cautious provenance note and mark what remains unverified.

Do not claim a screenshot proves the underlying event, account owner, or date
without independent corroboration.

## Minimal check

The final artifact links to its original hash and records every transformation.
