---
name: 2fa-migration-helper
description: Plan and verify a two-factor-authentication migration between devices or authenticators without exposing secrets or losing recovery access.
---

# 2FA Migration Helper

Make the new factor work before retiring the old one.

## Workflow

1. Inventory accounts, current factors, recovery codes, trusted sessions, and
   owner/priority; never ask the user to paste OTP seeds or codes.
2. Choose the destination authenticator and confirm it is controlled by the
   user, backed up according to its security model, and not silently synced.
3. Add the new factor using the service's supported flow and test login in a
   separate session before removing the old factor.
4. Regenerate recovery codes when the service requires it, store them in the
   approved recovery location, and revoke old devices/sessions deliberately.
5. Record completion and unresolved accounts without storing secrets in notes.

Do not disable the only working factor or send a recovery code to anyone.

## Minimal check

At least one fresh login succeeds with the new factor before the old factor is
removed.
