# Event

```sh
npx --yes nowhere-cli create event --input event.json --json
```

Use [event.json](../examples/event.json). Fields include `name`,
`description`, `image`, optional `pubkey`, and `tags`. Do not guess tag keys for
dates, venues, or styling; use the CLI's long-form help/upstream tag
documentation or the live builder for those fields.

Browser: `https://hostednowhere.com/create/event`. A name can be enough to reach
Share Link, but complete the requested date, timezone, venue, and other details
before final delivery. Verify them in the final rendered poster. If a QR code is
requested, generate it from the final URL, then test the decoded URL.

Creation builds a static event fragment; it does not publish a Nostr event or
notify attendees. An updated poster needs a new link/QR distributed by the user.
