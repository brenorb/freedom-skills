# Forum

Route: `https://hostednowhere.com/create/forum`

Minimum viable content:

- public key
- forum name

Use the builder's `Generate npub` button only for disposable demos or test runs. For real forums, use a key the user controls.

Success cues:

- the Verification step shows owner and forum phrases
- the Share Link step reveals a URL under `https://hostednowhere.com/s#...`

Important caution:

- forum ownership and verification depend on the chosen key
- if the user cannot operate the matching private key, future management and identity proof will break

Good demo payload:

- forum name: `Mutual Aid Radio Room`
