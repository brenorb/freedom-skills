# Petition

Route: `https://hostednowhere.com/create/petition`

Minimum viable content:

- public key
- petition name

Use the builder's `Generate npub` button only for disposable demos or test runs. For real petitions, use a key the user controls.

Success cues:

- the Verification step shows author and petition phrases
- the Share Link step reveals a URL under `https://hostednowhere.com/s#...`

Important caution:

- signatures are encrypted to the chosen public key
- if the user does not control the matching private key, every signature becomes unreadable

Good demo payload:

- petition name: `Keep the Night Market Open`
