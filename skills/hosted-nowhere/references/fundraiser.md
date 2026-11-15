# Fundraiser

```sh
npx --yes nowhere-cli create fundraiser --input fundraiser.json --json
```

Use [fundraiser.json](../examples/fundraiser.json). Fields include `name`,
`description`, `image`, optional `pubkey`, and `tags`. The fixture intentionally
has no payment destination. Add the user's actual method through the builder or
the CLI's documented tag format; verify that exact destination in the preview.

Browser: `https://hostednowhere.com/create/fundraiser`. A name alone may unlock
Share Link but does not complete a donation page needing payment details or a goal.

## Donation helpers

For payment configuration, read [payment method encoding](payment-methods.md).
Lightning and custom methods must share the `l` tag's value. Verify all requested
methods before generating an invoice.

```sh
npx --yes nowhere-cli fundraiser donate methods "$SITE_URL" --json
npx --yes nowhere-cli fundraiser donate invoice "$SITE_URL" --sats 5000 --json > invoice.json
cat invoice.json
```

List methods first. Request an invoice only when the user needs one. Lightning
invoice generation requires the Lightning method in tag `l`; custom payment
handles are list/copy flows. Use positive integer sats, inspect the returned
amount/destination/expiry, and distinguish generating an invoice from paying it.
If invoice generation times out, do not claim success or immediately mint another.
