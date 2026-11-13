---
name: matrix-community-ops
description: Administer Matrix rooms, users, moderation, bridges, and bots with least privilege and an explicit privacy boundary.
---

# Matrix Community Ops

Operate a Matrix community without conflating room membership, federation,
bridge delivery, and end-to-end encryption.

## Workflow

1. Define the room goal, homeserver ownership, moderation roles, invite policy,
   retention, bridge scope, and whether the room is public or private.
2. Inspect current room state and permissions before making changes. Prefer a
   dedicated bot/admin account with the smallest required power level.
3. For invites, bans, aliases, bridges, and announcements, preview the exact
   target and content and ask before external mutations.
4. Explain federation, server visibility, bridge metadata, backups, and E2EE
   limitations in the room's onboarding text.
5. Verify the change from room state or an independent client and record a
   rollback path for role and policy changes.

Never paste access tokens into messages or logs. Do not assume an encrypted
room hides metadata from homeservers, bridges, or compromised devices.

## Minimal check

Every administrative change has a named target, least-privilege actor, and
post-change verification.
