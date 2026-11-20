---
name: nowhere-forum-cli
description: "Create, update, inspect, sign, encrypt, and operate Nowhere forum pages with the local `nowhere` CLI. Use when the user wants a forum fragment or URL, needs post or reply automation, torrent workflows, chat flows, room flows, or moderated Web-of-Trust checks without using hostednowhere.com."
---

# nowhere-forum-cli

Start with the `nowhere` subcommand that directly matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create forum --input forum.json --json`
- Update: `nowhere update <forum-fragment-or-url> --patch patch.json --json`
- Inspect or verify:
  - `nowhere inspect <forum> --json`
  - `nowhere verify <forum> --json`
- Sign or encrypt when requested:
  - `nowhere sign <forum> --secret nsec1... --json`
  - `nowhere encrypt <forum> --password ...`
  - `nowhere decrypt <forum> --password ...`

## Action-First Flows

### Posts and replies

- Publish a post: `nowhere forum post <forum> --input post.json --secret nsec1... --json`
- List posts: `nowhere forum posts <forum> --moderated --json`
- Publish a reply: `nowhere forum reply <forum> --post-event <id> --input reply.json --json`
- List replies: `nowhere forum replies <forum> --post-event <id> --moderated --json`

### Torrent workflows

- Parse a real torrent: `nowhere forum torrent parse ./archive.torrent --json`
- Preflight before publish: `nowhere forum torrent check <forum> --torrent-file ./archive.torrent --category 'docs > manuals' --json`
- Publish a torrent: `nowhere forum torrent publish <forum> --torrent-file ./archive.torrent --category 'docs > manuals' --secret nsec1... --json`
- List or discuss torrents:
  - `nowhere forum torrents <forum> --moderated --json`
  - `nowhere forum torrent reply <forum> --torrent-event <id> --input reply.json --json`
  - `nowhere forum torrent replies <forum> --torrent-event <id> --json`

### Chat, private chat, and rooms

- General chat:
  - `nowhere forum chat send <forum> --input chat.json --json`
  - `nowhere forum chat list <forum> --moderated --json`
- Private chat:
  - `nowhere forum private send <forum> --recipient-session-pubkey <hex> --input private.json --json`
  - `nowhere forum private list <forum> --session-secret nsec1... --json`
- Rooms:
  - `nowhere forum room announce <forum> --input room.json --json`
  - `nowhere forum room send <forum> --input room-chat.json --json`
  - `nowhere forum room list <forum> --room-name main --access-code opsec --moderated --json`

### Moderation checks

- `nowhere forum wot check <forum> --scope post --author npub1... --json`

## Inputs To Prepare

- `forum.json`: upstream Nowhere forum codec shape
- `post.json`: `{ "title": "...", "body": "...", "topic": "..." }`
- `reply.json`: `{ "body": "...", "quotedReplyId": "..." }`
- `chat.json`: `{ "message": "..." }`
- `room.json`: `{ "roomName": "...", "accessCode": "..." }`
- `room-chat.json`: `{ "roomName": "...", "accessCode": "...", "message": "..." }`

## Sharp Edges

- Use `--moderated` when the task wants the same WoT and banned-word filtered view the website renders.
- `forum private list` needs the stable session secret, not the author's signing key.
- `forum torrent check` is the safe preflight because it validates the category path, feature toggles, fixed-root rules, and duplicate detection before publish.
- Forum relay flows accept repeated `--relay` flags, and forum namespaces can be split with `--salt`.

