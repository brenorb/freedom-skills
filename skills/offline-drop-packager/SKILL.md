---
name: offline-drop-packager
description: Assemble a verified offline bundle for USB, SD card, LAN, or local relay distribution with hashes, readable indexes, and safe metadata.
---

# Offline Drop Packager

Make an offline package usable by someone who does not share the original
environment.

## Workflow

1. Define audience, device/filesystem limits, language, expiry, update method,
   and whether the package may be copied onward.
2. Select only approved HTML, PDF, media, maps, installers, and instructions;
   remove caches, secrets, private paths, trackers, and unnecessary metadata.
3. Add a plain index, version/date, file sizes, SHA-256 manifest, integrity
   instructions, and a text-only fallback.
4. Test extraction and use on a clean/offline device; verify links, fonts,
   media, language, malware scans, and available disk space.
5. Package a signed or independently communicated hash when appropriate and
   record how to replace or revoke a stale bundle.

Do not include a tool or executable without explaining provenance and how to
verify it.

## Minimal check

The package reproduces its manifest after extraction on a clean offline path.
