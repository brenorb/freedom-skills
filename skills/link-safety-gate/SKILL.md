---
name: link-safety-gate
description: Inspect a suspicious or sensitive URL before opening it by checking destination, redirects, provenance, downloads, and exposure risk.
---

# Link Safety Gate

Turn “can I open this?” into a bounded, inspect-first decision.

## Workflow

1. Preserve the exact URL and source context; do not open it automatically.
2. Decode obvious shorteners or punycode, inspect hostname/path/query, and
   compare against the expected organization or sender.
3. Check redirects, certificate/domain signals, archive/reputation evidence,
   content type, download behavior, and whether login or personal data is
   requested.
4. Choose inspect-only, open in an isolated profile, download for scanning, or
   reject; state what the check cannot prove.
5. If opened, avoid login and active content until the user authorizes the
   required action; record the final URL and any downloaded artifact hash.

Do not upload a private URL to a public scanner without permission.

## Minimal check

The gate reports the final destination and separates reachability from trust.
