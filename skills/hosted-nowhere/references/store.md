# Store

Route: `https://hostednowhere.com/create/store`

Minimum viable content:

- public key
- store name
- at least 1 item with a name and numeric price

Use the builder's `Generate npub` button only for disposable demos or test runs. For real stores, use a key the user controls.

Success cues:

- the Verification step shows seller and store phrases
- the Share Link step can reveal a URL under `https://hostednowhere.com/s#...`
- the page exposes copy/share controls for the final URL

Important caution:

- orders are encrypted to the chosen public key
- if the user does not control the matching private key, the orders are effectively lost

Good demo payload:

- store name: `Midnight Tea Counter`
- item 1 name: `Smoked Oolong`
- item 1 price: `12`
