# Forum

```sh
npx --yes nowhere-cli create forum --input forum.json --json
```

Use [forum.json](../examples/forum.json) with the intended creator's `pubkey`.
The codec identifies this app as `discussion`. Optional fields include
`description`, `image`, and `tags`. Keep actual author identities for real forums;
throwaway keys are for explicitly disposable work.

Browser: `https://hostednowhere.com/create/forum`. Check topics, enabled features,
and moderation settings. Keep the complete fragment and any salt: forum runtime
keys depend on them. Changing the URL or salt can change the namespace and hide
old activity; retain the old URL and never promise automatic migration.

The name, description, and enabled features render directly from the URL fragment;
creating a forum does not register it on a relay. Posts, torrents, replies, and
chat use relays separately. A CLI `--relay` override neither edits the link nor
configures the browser's relay connections. A rendered forum header therefore
does not prove the browser can fetch the activity seen in a CLI readback. Verify
the requested page features and relay artifacts separately; report unobserved
browser activity as unverified. Do not republish or change the URL, salt, or relay
selection just to make an empty browser list match the CLI.
See the [URL and Forum architecture](https://hostednowhere.com/how-it-works).

## Posts and replies

`RELAY` below is the supplied relay URL. Use the explicit override consistently
for runtime writes and reads; omit it only when default relays are intended.
When the user supplies a namespace salt, pass it with `--salt "$SALT"` as below.
Omit that flag when no salt is requested. Do not append `?salt=...` after the URL
fragment or edit the fragment to encode a salt.

```sh
npx --yes nowhere-cli forum post "$SITE_URL" --input post-input.json --secret "$AUTHOR_SECRET" --salt "$SALT" --json --relay "$RELAY" > post.json
npx --yes nowhere-cli forum posts "$SITE_URL" --moderated --salt "$SALT" --json --relay "$RELAY"
npx --yes nowhere-cli forum reply "$SITE_URL" --post-event "$POST_ID" --input reply-input.json --salt "$SALT" --json --relay "$RELAY" > reply.json
npx --yes nowhere-cli forum replies "$SITE_URL" --post-event "$POST_ID" --moderated --salt "$SALT" --json --relay "$RELAY"
```

Inputs: post `{"title":"Dispatch","body":"Details"}`;
reply `{"body":"Reply text"}` (optional `quotedReplyId`). Omit `topic` unless the
forum actually enables that named topic. A default **General** browser view does
not establish that the CLI accepts `"topic":"General"`. Omit author secrets only when a disposable identity is intended; an active
remote signer can use `--use-signer`. Save returned event IDs and read back using
the same URL, relay selection, and salt. `--moderated` matches the website's WoT
and banned-word view; absence from that view need not mean publication failed.

For post authorship, compare the publish response's `authorPubkeyHex` with the
readback's `posts[].payload.p`. The CLI verifies the inner `sig`/`w` author proof
before returning that payload. The outer relay `event.pubkey` identifies a fresh
envelope key; `replyPubkey` identifies a derived reply channel. Different values
are expected. Use the verified inner author and the local WoT check for identity
checks; preserve the complete public key when comparing its encodings.

If local validation fails, correct the input/flags and **keep the output redirect**
on the corrected command. Once a publish succeeds and returns an event ID, stop
publishing. If its JSON was shown only in a tool response, save that exact existing
JSON to the requested file; do not re-run the publish to capture it. If the response
cannot be recovered, use a matching readback and report the missing original
response rather than creating a duplicate.

## Torrents

For torrent authoring, preflight, publishing, duplicate detection, and replies,
read [the torrent workflow](forum-torrents.md). It includes the required feature
flags and category configuration; verification tag `V` does not enable torrents.

## Chat, private messages, and rooms

For these tasks, read [the chat workflow](forum-chat.md). It contains the send/list
commands, session-key rules, and required distinction between relay acceptance
and recipient delivery. Do not report a message as delivered without a live
recipient acknowledgment.

## Moderation and relay targeting

```sh
npx --yes nowhere-cli forum wot check "$SITE_URL" --scope post --author "$AUTHOR_NPUB" --json
```

`forum wot check` is a local access check and accepts neither `--relay` nor
`--salt`; torrent parsing is local too.

Relay flows accept repeated `--relay` overrides; `--salt` must match the namespace.
Use the same values for write/read checks. Keep raw and moderated views distinct
when investigating a missing post. For other CLI features, such as voice
signaling, read the targeted `npx --yes nowhere-cli forum <feature> --help`; do not infer that
signaling alone establishes an audio connection.
