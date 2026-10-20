# Message

```sh
npx --yes nowhere-cli create message --input message.json --json
```

Start with [message.json](../examples/message.json), replacing its content.
`name` is the sender name; `description` is the body. A message needs a body or a
nonempty title tag `t`. Optional fields include `image` and `pubkey`.

Browser: `https://hostednowhere.com/create/message`. Fill the sender and body or
title, then check the preview and regenerate the final Share Link after edits.

## Reader tips, only when requested

For payment configuration, read [payment method encoding](payment-methods.md).
Lightning and custom methods must share the `l` tag's value.

```sh
npx --yes nowhere-cli message tip methods "$SITE_URL" --json
npx --yes nowhere-cli message tip invoice "$SITE_URL" --sats 2100 --json > invoice.json
cat invoice.json
```

Payment methods live in tag `l`. Use a real Lightning address configured by the
user, not the dummy word `lightning`. Custom methods are list/copy flows. Inspect
methods before requesting an invoice; report its amount and expiry if returned.
Creating an invoice does not pay it. Avoid retrying invoice generation blindly.

Message pages are static, with no CLI relay-backed inbox or reply flow. Route
discussion requests to Forum. Verify the final sender, title, and body in the
rendered URL; successful decoding alone does not establish correct content.
