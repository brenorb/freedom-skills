# Forum chat, private messages, and rooms

```sh
npx --yes nowhere-cli forum chat send "$SITE_URL" --input chat-input.json --json --relay "$RELAY" > chat.json
npx --yes nowhere-cli forum chat list "$SITE_URL" --moderated --json --relay "$RELAY"
npx --yes nowhere-cli forum private send "$SITE_URL" --recipient-session-pubkey "$RECIPIENT_SESSION" --input private-input.json --json --relay "$RELAY" > private.json
npx --yes nowhere-cli forum private list "$SITE_URL" --session-secret "$SESSION_SECRET" --json --relay "$RELAY"
npx --yes nowhere-cli forum room announce "$SITE_URL" --input room-input.json --json --relay "$RELAY" > room.json
npx --yes nowhere-cli forum room send "$SITE_URL" --input room-chat-input.json --json --relay "$RELAY" > room-chat.json
npx --yes nowhere-cli forum room list "$SITE_URL" --room-name main --access-code "$ROOM_CODE" --moderated --json --relay "$RELAY"
```

A basic Forum already supports these commands; no additional chat, private-message,
or room creation flag is required. For a new forum, create it from
[forum.json](../examples/forum.json) using the Forum reference, save the returned
URL, and run the commands above. For an existing forum, use its URL directly.
`roomName` and `accessCode` belong to the runtime inputs below, not forum creation
tags. Start with the requested operation; use its targeted `--help` if it fails.

The `*-input.json` files contain message inputs; the captured `chat.json`,
`private.json`, `room.json`, and `room-chat.json` files contain actual send
responses with `event.id`. Use the requested output names and never substitute
the input for the response.

Inputs: chat/private `{"message":"Hello"}`; room
`{"roomName":"main","accessCode":"chosen-code"}`; room chat adds `message`.
For `--recipient-session-pubkey`, use the recipient session's **64-character
hexadecimal public key** (`pubkeyHex`), not its `npub` or Nowhere base64url form.
This option is stricter than the author-key field used at site creation. Obtain
or convert the public encoding; sending does not require the recipient's secret.
Private decryption needs the stable recipient session secret, not the author's
signing key. Preserve session material securely. Chat uses ephemeral relay events;
a later empty listing does not prove no message was sent. Relay acceptance proves
only that the relay accepted the event, not recipient delivery or reading.
Coordinate a live receiver for delivery tests, and never replay chat automatically
after a timeout. Send each requested message once; do not send an extra test
message to manufacture history. Verify the final forum URL in the browser before
reporting completion, even when chat history is correctly empty.

## Report the observed state precisely

Prefer a brief completion report: the final URL, requested files, and the record
below. Extra documentation files are usually unnecessary unless the user asks.
**Never copy private/session secret values into prose, extra reports, or command
examples, including disposable test values.** Use `$SESSION_SECRET` or
`$AUTHOR_SECRET` placeholders when explaining a command, and report public session
identifiers instead. Keep this rule when summarizing configuration too.

A CLI send creates and signs an event locally, then asks the selected relay to
accept it. Its event ID and valid signature are **not a recipient acknowledgment**.
Even a successful relay response does not establish that anyone received or read
the message. Do not label a send “Delivered” in a table, heading, summary, or
explanation solely because the CLI succeeded. This distinction applies to general
chat, private messages, room announcements, and room chat alike.

Use this completion record, filled from actual observations:

- **Relay acceptance:** accepted or failed, with saved event IDs/responses.
- **Recipient delivery:** unverified unless a coordinated live recipient actually
  acknowledged receipt. State “unverified” when no such acknowledgment exists.
- **Later history:** observed list contents; an empty ephemeral listing proves
  neither delivery nor non-delivery. Do not replay sends to change that result.
- **Page verification:** final forum URL and the visible name/features checked.

A live recipient acknowledgment is a separate test requiring an active receiver
at send time. If the task exercises only send/list operations, finish with the
unverified-delivery limitation; do not invent a receiver or imply it was tested.
