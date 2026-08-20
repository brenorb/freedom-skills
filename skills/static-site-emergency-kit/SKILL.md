---
name: static-site-emergency-kit
description: Produce a small, dependency-light static publication bundle for emergency information sharing and later mirror deployment.
---

# Static Site Emergency Kit

Make the smallest useful site that can be copied to another host, USB drive,
or local server under pressure.

## Workflow

1. Define the minimum public message, update owner, contact route, language,
   timestamp, and expiry/retraction policy.
2. Generate plain HTML with local CSS and assets; remove analytics, trackers,
   third-party fonts, build caches, comments, and source maps.
3. Add a visible publication time, version identifier, accessibility basics,
   printable text view, and a plain-text fallback.
4. Scan the bundle for secrets, identifying metadata, absolute paths, broken
   links, and accidental external requests.
5. Package the site with a manifest, hash list, deployment notes, and rollback
   copy. Deploy only through an explicitly approved channel.

Do not include live emergency claims without an owner and update time. Do not
embed private contact details unless the audience and consent are clear.

## Minimal check

Serve the bundle from a clean local directory with networking disabled and verify
that the main message and navigation still work.
