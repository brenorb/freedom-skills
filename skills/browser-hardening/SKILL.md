---
name: browser-hardening
description: Review and harden a browser for sensitive research or publishing by reducing sync, extension, permission, tracking, and contaminated-session risk.
---

# Browser Hardening

Reduce exposure while preserving the sites and workflows the user actually
needs.

## Workflow

1. Define task, account boundary, threat model, device ownership, and whether
   the user needs ordinary browsing, research, publishing, or a temporary
   isolated session.
2. Review browser version, sync, profiles, extensions, permissions, saved
   credentials, autofill, history, downloads, notifications, and third-party
   cookies.
3. Disable or remove unnecessary extensions and permissions, separate profiles,
   turn off personal sync for the sensitive task, and keep a rollback path.
4. Test required sites, downloads, accessibility, and sign-in behavior after
   each change; do not stack opaque “privacy” extensions blindly.
5. Explain residual risks: IP/network observation, fingerprinting, account
   identity, malware, device compromise, and operator error.

Do not claim that browser settings provide anonymity or safe handling of a
malicious file.

## Minimal check

The user can see which settings changed, what broke, and how to restore the
previous profile state.
