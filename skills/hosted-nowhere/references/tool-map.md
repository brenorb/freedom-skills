# Hosted Nowhere Tool Map

Official sources:

- Live site: `https://hostednowhere.com`
- Upstream repo: `https://github.com/5t34k/nowhere`

Use this file when the requested site type is unclear.

| Tool | Route | Minimum viable content | Share step | Special caution |
| --- | --- | --- | --- | --- |
| Store | `https://hostednowhere.com/create/store` | public key, store name, 1 priced item | 10 | Real deployments require a key the user controls or encrypted orders become unreadable |
| Message | `https://hostednowhere.com/create/message` | sender name, body or title | 6 | Empty body requires a title |
| Fundraiser | `https://hostednowhere.com/create/fundraiser` | name | 6 | Usually wants payment details soon after the first publishable draft |
| Petition | `https://hostednowhere.com/create/petition` | public key, petition name | 7 | Real deployments require a key the user controls or signatures become unreadable |
| Event | `https://hostednowhere.com/create/event` | name | 7 | Date and venue are optional for first publish but usually expected |
| Forum | `https://hostednowhere.com/create/forum` | public key, forum name | 5 | Key ownership matters for forum management and verification |
| Drop | `https://hostednowhere.com/create/drop` | body text | 4 | Title can stay blank |
| Art | `https://hostednowhere.com/create/art` | SVG content | 5 | Needs real SVG, not just a title |

Per-tool references:

- [store.md](store.md)
- [message.md](message.md)
- [fundraiser.md](fundraiser.md)
- [petition.md](petition.md)
- [event.md](event.md)
- [forum.md](forum.md)
- [drop.md](drop.md)
- [art.md](art.md)
