---
name: download-safety-check
description: Check a downloaded file's provenance, signature, hash, type, archive contents, and execution risk before opening or installing it.
---

# Download Safety Check

Inspect first; never execute an unverified download to discover what it is.

## Workflow

1. Record source URL, redirect/final URL, publisher, requested version, file
   name, size, timestamp, and hash without opening the file.
2. Prefer official release pages and verify signed checksums or signatures with
   a separately trusted key; record the key fingerprint and verification result.
3. Inspect MIME/type, archive paths, symlinks, scripts, macros, install hooks,
   bundled binaries, permissions, and unexpected files.
4. Scan or examine in an isolated environment and choose view, extract,
   sandbox, install, or reject according to the user's authorization.
5. Preserve a verification note and rollback/uninstall path for approved
   installs.

Do not treat a hash from the same untrusted page as independent authenticity.

## Minimal check

The report includes provenance, expected-versus-actual hash or signature, file
type, and a clear action recommendation.
