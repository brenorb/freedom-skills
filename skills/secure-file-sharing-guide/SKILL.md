---
name: secure-file-sharing-guide
description: Choose and prepare a safer way to transfer files or media based on sensitivity, recipient, expiry, metadata, and connectivity.
---

# Secure File Sharing Guide

Choose the least complex transfer that meets the threat model and recipient
needs.

## Workflow

1. Classify the file: public, internal, sensitive, or highly sensitive; check
   size, metadata, retention, and whether the recipient can verify integrity.
2. Prefer an existing trusted end-to-end encrypted channel for a small direct
   transfer, an encrypted archive for offline delivery, or a temporary P2P link
   when both parties can remain online.
3. Remove or preserve metadata intentionally, hash the final file, and send the
   verification value through a separate trusted channel when appropriate.
4. Set expiry, revoke access where supported, and avoid services that require
   unnecessary accounts or expose filenames and recipient lists.
5. Confirm the exact recipient and file path before sending; verify receipt and
   safe deletion only when the user asks.

Do not treat a link with a password as end-to-end encryption. Never upload
private material to an unknown service merely because it is convenient.

## Minimal check

The recommendation names the confidentiality, integrity, availability, and
metadata tradeoff for the chosen method.
