---
name: contact-book-sanitizer
description: Reduce unnecessary exposure in a contacts database before syncing, sharing, migrating, or handing a device to another person.
---

# Contact Book Sanitizer

Minimize the contact graph before it crosses a trust boundary.

## Workflow

1. Identify the destination app/device and whether the transfer needs names,
   numbers, notes, groups, avatars, or all contacts.
2. Export a protected backup first when recovery matters, then work from a
   derivative copy.
3. Remove stale entries, sensitive notes, hidden groups, duplicate identities,
   and fields not required for the destination.
4. Inspect sync settings, linked accounts, shared devices, and automatic
   suggestions before importing the sanitized set.
5. Verify the destination contains only the approved fields and document how
   to revoke or delete the transfer.

Do not erase the only copy without an explicit, confirmed deletion request.

## Minimal check

Compare the destination field list and contact count against the approved
export, not against memory.
