# NIPs and Kinds

Read this file when the user needs protocol context for `nostr-cli` terms such as `kind 1`, `NIP-17`, `nevent`, or relay-list metadata.

This is a practical reference for this skill, not a complete Nostr spec index.

## How to read this

- `kind` means the event type number stored on relays.
- `NIP` means a Nostr protocol convention or standard.
- Prefer the high-level `nostr` commands when they exist. Use `nostr event new` only when the user needs raw control.

## Core kinds for this skill

### `kind 0`

Profile metadata.

Used for names, pictures, bios, website fields, and bot metadata.

In `nostr-cli`:

- `nostr profile`
- `nostr profile update`

### `kind 1`

Plain text note.

This is the normal public post type.

In `nostr-cli`:

- `nostr post`
- `nostr reply`
- `nostr event new --kind 1`

### `kind 3`

Follow list or contact list.

This stores who an account follows.

In `nostr-cli`:

- `nostr follow`
- `nostr unfollow`
- `nostr following`

### `kind 4`

Legacy encrypted DM event.

This is older DM format. The CLI can still read it and can send it when forced.

In `nostr-cli`:

- `nostr dm --nip04`
- `nostr events --kinds 4`

### `kind 7`

Reaction event.

Common examples are `"+"` or emoji-like reactions to another event.

In `nostr-cli`:

- usually via `nostr event new --kind 7 ...`

### `kind 10002`

Relay list metadata.

This is how an account can publish preferred relays.

In `nostr-cli`:

- used indirectly by account import and relay discovery
- inspected through `nostr relays`

### `kind 30023`

Long-form article.

Used for published long-form content.

In `nostr-cli`:

- `nostr post -f article.md`
- `nostr post --title ... --slug ...`

### `kind 30024`

Draft long-form article.

Same long-form model as `30023`, but draft state.

In `nostr-cli`:

- `nostr post --draft`

## Other kinds worth recognizing

### `kind 5`

Deletion event.

Important conceptually, but this skill does not currently center a deletion workflow.

Usually this would require raw event control or a future dedicated command.

### `kind 6`

Repost or boost.

Useful to recognize when inspecting threads or event streams, even though this skill does not provide a dedicated repost workflow.

### `kind 9735`

Zap receipt.

This is the event users usually mean when talking about zaps showing up on Nostr.

The current `nostr-cli` does not expose a native zap send workflow, so this kind is mostly useful for recognition and debugging.

### `kind 10003`

Ephemeral typing-indicator style event used by the interactive DM UX.

This matters mostly if you inspect DM traffic or interactive features, not for the non-interactive core flow of this skill.

## Core NIPs for this skill

### `NIP-01`

Basic protocol: events, ids, signatures, relays.

If the user asks what an event is at all, this is the base layer.

### `NIP-02`

Contact lists and follows.

Relevant to:

- `nostr follow`
- `nostr unfollow`
- `nostr following`

### `NIP-05`

Human-readable identity mapping like `user@domain.com`.

Relevant to:

- `nostr profile user@domain.com`
- `nostr generate nip05`
- resolving identities passed to `--account` or user lookup

### `NIP-10`

Reply threading.

This governs the `e` and `p` tag structure for replies.

Relevant to:

- `nostr reply`

Prefer `nostr reply` over raw `event new` when the user wants to reply to an existing note.

### `NIP-17`

Modern gift-wrapped DMs.

This is the default DM mode in current `nostr-cli`.

Relevant to:

- `nostr dm`

### `NIP-19`

Bech32 identifiers such as `npub`, `nsec`, `note`, and `nevent`.

Relevant to:

- accepting `note1...` or `nevent1...` in replies
- recognizing public vs private identifiers

### `NIP-23`

Long-form content.

Relevant to:

- `nostr post -f ...`
- `--title`
- `--summary`
- `--slug`
- `--draft`

### `NIP-24`

Bot flag in profile metadata.

Not a day-to-day workflow, but useful when the user is managing bot identities.

### `NIP-44`

Encryption format used by modern DMs.

Relevant because `NIP-17` messages use it under the hood.

### `NIP-65`

Relay list metadata convention.

Relevant to:

- relay discovery on import
- understanding why `kind 10002` matters

## Important NIPs not covered as first-class workflows here

### `NIP-57`

Zaps.

Important to know because users often ask about them, but current `nostr-cli` does not expose a native zap send command in its documented command surface.

If the user asks about zaps, treat that as adjacent protocol context rather than a supported primary workflow of this skill.

### `NIP-42`

Relay authentication.

Good to recognize when relay behavior gets weird, but not a first-class workflow in the current skill.

## Command mapping cheatsheet

- Public note: `kind 1` via `nostr post`
- Reply: `kind 1` plus `NIP-10` tags via `nostr reply`
- Follow graph: `kind 3` via `nostr follow` and `nostr unfollow`
- Legacy DM inspection: `kind 4`
- Reaction: usually `kind 7` via `nostr event new`
- Relay list metadata: `kind 10002`, usually not hand-authored
- Long-form article: `kind 30023`
- Long-form draft: `kind 30024`

## Rule of thumb

- If the user wants to post, reply, DM, follow, or publish long-form content, prefer the dedicated `nostr` command.
- If the user wants custom tags, unusual event kinds, or protocol-level control, use `nostr event new`.

## Complete references

If the user needs the full protocol index instead of this practical subset:

- Full NIP index: `https://github.com/nostr-protocol/nips`
- Rendered NIP docs: `https://nips.nostr.com/`
- Basic protocol and event structure: `https://github.com/nostr-protocol/nips/blob/master/01.md`
