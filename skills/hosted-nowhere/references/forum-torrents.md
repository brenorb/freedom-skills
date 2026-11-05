# Forum torrents

```sh
npx --yes nowhere-cli forum torrent parse ./archive.torrent --json
```

For a new torrent-enabled forum, start from
[forum-torrents.json](../examples/forum-torrents.json), replacing the test owner
and content. These tags have distinct meanings:

| Tag | Meaning |
| --- | --- |
| `b` with `null` value | Enable torrent submissions |
| `F` with `null` value | Fix the allowed top-level categories |
| `q` | Pipe-separated category roots, for example `docs|audio` |
| `V` | Verification configuration; does not enable torrents |

For an existing forum, check its actual settings and preserve other tags. If
preflight reports torrent submissions disabled, diagnose the missing `b` flag.
Do not change a real forum's feature policy unless that change is requested.
Changing its encoded settings can change the namespace, so retain the old URL.

## Check, publish once, and read back

```sh
npx --yes nowhere-cli forum torrent check "$SITE_URL" --torrent-file ./archive.torrent --category docs --relay "$RELAY" --json > preflight.json
npx --yes nowhere-cli forum torrent publish "$SITE_URL" --torrent-file ./archive.torrent --category docs --secret "$AUTHOR_SECRET" --relay "$RELAY" --json > torrent-result.json
npx --yes nowhere-cli forum torrents "$SITE_URL" --moderated --relay "$RELAY" --json
```

Read the preflight response before publishing. It checks feature toggles,
categories, fixed roots, normalization, and duplicates. A `duplicate` object
identifies an existing event: do not publish it again. A null `duplicate` means
no matching infohash/title was found in that query, not a retention guarantee.
Use the user's actual category; nested paths use `docs > manuals` syntax.

Persist the publish response and event ID in that same invocation. Re-running
preflight after a successful publish is a read check for the existing event;
re-running publish is another write. Raw and moderated lists can differ because
of author trust and banned-word filtering. Match URL, relays, and any `--salt`.

## Replies

```sh
npx --yes nowhere-cli forum torrent reply "$SITE_URL" --torrent-event "$TORRENT_ID" --input reply-input.json --secret "$AUTHOR_SECRET" --relay "$RELAY" --json > reply-result.json
npx --yes nowhere-cli forum torrent replies "$SITE_URL" --torrent-event "$TORRENT_ID" --relay "$RELAY" --json
```

`reply-input.json` contains `{"body":"Reply text"}` and optionally
`quotedReplyId`. Use an identity permitted by the forum and preserve returned IDs.
When a remote signer is configured, `--use-signer` replaces `--secret`.
