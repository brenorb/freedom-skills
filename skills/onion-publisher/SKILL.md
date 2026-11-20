---
name: onion-publisher
description: Prepare and review a static publication for a Tor onion service while minimizing metadata, accidental exposure, and deployment mistakes.
---

# Onion Publisher

Package a publication for an onion service without assuming that Tor makes the
content, operator, or readers anonymous.

## Workflow

1. Confirm the content, audience, hosting boundary, and whether the onion
   address may be shared publicly.
2. Build a static bundle and inspect HTML, assets, links, fonts, analytics,
   comments, filenames, EXIF, and generated metadata for identifying leakage.
3. Follow the host's supported Tor onion-service deployment method; keep the
   service key outside the publication bundle and back it up separately.
4. Test from a clean Tor client: address resolution, every page, downloads,
   redirects, and absence of accidental clearnet dependencies.
5. Record the onion address, version/hash, deployment date, and rollback plan.

Do not deploy or announce an onion service without explicit authorization. Do
not claim operator anonymity, and do not mix private administration with public
content paths.

## Minimal check

Fetch the published bundle through Tor and compare its content manifest with the
reviewed local bundle.
