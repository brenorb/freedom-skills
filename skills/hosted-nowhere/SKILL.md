---
name: hosted-nowhere
description: "Create or update Hosted Nowhere sites at hostednowhere.com for the eight supported builders: store, message, fundraiser, petition, event, forum, drop, and art. Use when the user wants a shareable Nowhere URL, wants to fill or revise one of those builders, wants a `/s#...` link from Hosted Nowhere, or needs to inspect verification, signing, or encryption behavior for a Nowhere site."
---

# hosted-nowhere

Use the live Hosted Nowhere builders, not guessed fragments or stale screenshots. The official surfaces are the live site at `https://hostednowhere.com` and the upstream repo at `https://github.com/5t34k/nowhere`.

## Quick Start

1. Identify the target builder and read the matching reference file in `references/`.
2. Open `https://hostednowhere.com/create/<tool>`.
3. Fill the minimum required fields first until the Verification and Share Link stages become usable.
4. Stop and verify success on the Share Link step:
   - the URL starts with `https://hostednowhere.com/s#`
   - the page offers a copy/share control
   - the Verification step shows the expected phrase output
5. Only then add optional polish.

## Builder Selection

- `store`: private product catalog with encrypted orders
- `message`: one-page message, note, or announcement
- `fundraiser`: donation or support page
- `petition`: signature collection page with encrypted submissions
- `event`: poster-style event page
- `forum`: private discussion space
- `drop`: a simple drop/message wall
- `art`: SVG art page

If the requested page type is unclear, read [tool-map.md](references/tool-map.md) first, then route to the matching tool reference:

- [store.md](references/store.md)
- [message.md](references/message.md)
- [fundraiser.md](references/fundraiser.md)
- [petition.md](references/petition.md)
- [event.md](references/event.md)
- [forum.md](references/forum.md)
- [drop.md](references/drop.md)
- [art.md](references/art.md)

Use `python3 scripts/tool_specs.py --json` when you need a machine-readable view of the same map.

## Workflow

1. Read the matching tool reference before touching the builder.
2. Prefer the user's real `npub` when the site is meant to be used for real.
3. Use the builder's own `Generate npub` control only for disposable demos, smoke tests, or when the user explicitly wants a throwaway identity.
4. Treat these three builders as key-ownership-sensitive:
   - `store`
   - `petition`
   - `forum`
5. For those three, warn if the user appears to be using a key they do not control. Orders, signatures, or forum management can become unreadable otherwise.
6. Do not sign or encrypt the Share Link unless the user asks for it or the task is explicitly a test of signing/encryption.

## Success Criteria

- The builder reaches the `Verification` step without validation dead-ends.
- The `Share Link` step exposes a usable `https://hostednowhere.com/s#...` URL.
- The live preview renders the content type you intended.
- For key-sensitive builders, the user understands whether the chosen key is real or disposable.

## Sharp Edges

- `message` needs either body text or a title tag. An empty sender name alone is not enough.
- `drop` requires body text. The title can stay blank.
- `art` requires SVG content. A title alone is not enough.
- `store` requires at least one item with a name and numeric price.
- `forum`, `petition`, and `store` are the most dangerous builders to fake with a throwaway key when the page is intended for real use.
- The Share Link step can become stale after edits. If the UI says the data changed, go back to Share Link and regenerate the final URL.

## Resources

- `scripts/tool_specs.py`: deterministic map of the 8 builders, routes, requirements, and cautions.
- `references/tool-map.md`: quick chooser across all eight builders.
- `references/*.md`: per-builder field and validation guidance.

When the builder behavior and the reference files disagree, trust the live Hosted Nowhere UI first and update the reference after the task.
