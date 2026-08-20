---
name: simplex-helper
description: Set up and operate SimpleX conversations or groups with privacy-aware onboarding, local state checks, and safe message/file workflows.
---

# SimpleX Helper

Guide a person through a concrete SimpleX task while keeping invitations,
profiles, local databases, and message content separate.

## Workflow

1. Confirm whether the user needs a one-to-one chat, group, file transfer,
   relay/proxy setup, backup, or migration, and identify the intended contact.
2. Use the installed SimpleX CLI/app's non-interactive or documented workflow;
   inspect version, local profile, and connectivity before changing anything.
3. Treat an invitation or contact address as a secret until the user chooses to
   share it. Confirm recipient and content immediately before an external send.
4. Explain local history, device compromise, notification, relay, and metadata
   limits; do not describe SimpleX as magic anonymity.
5. Verify the result from the relevant local inbox/status, not from a queued
   command alone. Record migration and backup steps without copying secrets.

Do not invent contact IDs, send messages, or publish group links without clear
authorization.

## Minimal check

The workflow ends with a local status/inbox verification and an explicit record
of what information was shared.
