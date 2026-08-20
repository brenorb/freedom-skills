---
name: low-bandwidth-publisher
description: Adapt a publication for slow, metered, or intermittently connected readers with a small, readable, resilient bundle.
---

# Low-Bandwidth Publisher

Optimize for completion on a weak connection, not for a benchmark score.

## Workflow

1. Identify the reader's device, likely connection, language, and whether they
   need text, images, audio, or downloads first.
2. Make the primary page plain HTML with local CSS, compressed images only when
   useful, no autoplay, no remote fonts, and no mandatory JavaScript.
3. Add a text-only view, printable/downloadable copy, explicit file sizes, and
   resumable or separately linked large assets where supported.
4. Test with network throttling or an offline local server; measure total bytes,
   request count, first meaningful content, and behavior when assets fail.
5. Record the bundle version and keep the text copy independently mirrorable.

Never remove safety-critical context merely to save bytes. Avoid third-party
analytics and external requests that reveal reader interest.

## Minimal check

The core message must be readable with CSS and JavaScript disabled and after
large optional assets are blocked.
