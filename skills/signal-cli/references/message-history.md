# Reading and searching Signal messages

Use this reference when the user wants to inspect incoming messages or search a
local capture. For previously stored history, start with the supplied capture and
the search commands below; no account sync is needed. For new messages, start with
JSON `receive`. Use account discovery/onboarding only if the account is uncertain
or the requested action fails.

## Receive new messages

With a known account:

```bash
signal-cli -o json -a "+15551234567" receive --timeout 5 --ignore-attachments
```

The output is JSONL: one JSON event per line. Diagnostics remain on stderr.
`--timeout 5` controls waiting for new messages. `--ignore-attachments` avoids
attachment downloads; omit it if the user wants the files. Receiving sends delivery
receipts by default. `--send-read-receipts` is a separate opt-in; do not add it just
to inspect messages.

To keep a searchable capture, choose a private local directory and use a separate
file per account. Append raw events before filtering so later queries can inspect
receipts, groups or non-text metadata too:

```bash
capture_dir="captures/signal"
(
  umask 077
  mkdir -p "$capture_dir"
  touch "$capture_dir/events.jsonl"
  chmod 600 "$capture_dir/events.jsonl"
  signal-cli -o json -a "+15551234567" receive --timeout 5 --ignore-attachments \
    >> "$capture_dir/events.jsonl"
)
```

Check the receive exit status and stderr before reporting success. A failure can
leave a partial capture; an empty file alone does not prove the queue is empty.
Use `>>` to preserve earlier events. Do not merge stderr into the JSONL stream.
For one-off inspection, a temporary capture is sufficient; keeping an archive is
an explicit retention choice. Captures are plaintext and do not enforce Signal's
disappearing-message timers, edits or remote deletion. Keep them out of Git and
unrelated uploads.

## Read captured incoming text

Normalize incoming `envelope.dataMessage` events into a convenient JSONL view:

```bash
(
  umask 077
  jq -c '
    select(.envelope.dataMessage != null)
    | .envelope as $e
    | $e.dataMessage as $m
    | {
        timestamp: ($m.timestamp // $e.timestamp),
        sender: ($e.sourceNumber // $e.sourceUuid // $e.source),
        group_id: ($m.groupInfo.groupId // null),
        message: ($m.message // "")
      }
  ' captures/signal/events.jsonl > captures/signal/messages.jsonl
)
```

The raw capture remains the source; regenerate the view after appending events.
Timestamps are Unix milliseconds. A sender can be a UUID when phone number privacy
hides the number. `group_id` is null for direct messages; the text can be empty for
attachments or other non-text data messages. This view contains data-message bodies; it does not reconstruct edits, deletions,
reactions or sent-message sync events into a full conversation transcript. Inspect
the raw events when those details matter.

## Search captured history

Literal, case-insensitive substring search (the query is passed as data, not a
regular expression or shell code):

```bash
jq -c --arg query 'meeting' '
  select((.message | ascii_downcase) | contains($query | ascii_downcase))
' captures/signal/messages.jsonl
```

`ascii_downcase` folds ASCII letters; it does not implement Unicode-aware case
folding. An empty query matches all rows. Use `contains($query)` for exact-case
literal matching. If the user requests a regex, use `test($pattern; "i")` with an
explicitly supplied pattern, rather than turning every search string into regex.

Filter by sender and a time range, using numeric millisecond bounds:

```bash
jq -c --arg sender '+15557654321' --argjson since 1704067200000 \
  --argjson until 1704153600000 '
  select(.sender == $sender and .timestamp >= $since and .timestamp < $until)
' captures/signal/messages.jsonl
```

Filter a group independently of its members' sender identifiers:

```bash
jq -c --arg group 'BASE64_GROUP_ID' 'select(.group_id == $group)' \
  captures/signal/messages.jsonl
```

These queries stream the saved JSONL. They do not receive messages or change the
account. No matches means no match in this capture; it does not prove the message
was never sent or that another device has no matching history. Report the capture's
scope and whether it contains only incoming text when answering a history query.

## History limits and continuous capture

- `receive` consumes pending events for this device; it does not replay previously
  received messages or fetch the phone's old conversation database.
- An earlier sync without retained output cannot be recovered by repeating
  `receive`. Ask for an existing archive/export when the requested history is
  outside the available capture.
- `signal-cli` does not document a general inbox-history `search` command. Its
  account database, key/session state and resend logs are not a supported complete
  message-history API. Do not invent commands or query internal SQLite tables as
  if they were a stable inbox schema.
- If the user already maintains a JSONL/SQLite message archive, search that archive
  using its documented schema. SQLite is a possible store for captured events,
  not an undocumented built-in Signal history feature.
- `daemon` and `jsonRpc` support ongoing receipt. Use the existing receiver's
  capture/subscriber when it owns the account; do not launch a competing receiver.
  Automatic JSON-RPC notifications use `params.envelope`; subscription
  notifications use `params.result.envelope`. Select receive notifications and
  unwrap their actual shape before using the direct-receive filters above.
  The 0.14.9 HTTP daemon also keeps a bounded in-memory event replay buffer; it
  is not a durable conversation archive and is lost on restart.

## Sources and compatibility

The receive flags were checked with local signal-cli 0.14.8; the JSON fields were
reviewed against stable 0.14.9. Inspect a sample event when using another version
or transport. Keep the raw capture when a schema adaptation is needed.

- [Receive command manual](https://github.com/AsamK/signal-cli/blob/v0.14.9/man/signal-cli.1.adoc#receive).
- [JSON receive handler](https://github.com/AsamK/signal-cli/blob/v0.14.9/src/main/java/org/asamk/signal/json/JsonReceiveMessageHandler.java).
- [Envelope fields](https://github.com/AsamK/signal-cli/blob/v0.14.9/src/main/java/org/asamk/signal/json/JsonMessageEnvelope.java)
  and [data message fields](https://github.com/AsamK/signal-cli/blob/v0.14.9/src/main/java/org/asamk/signal/json/JsonDataMessage.java).
- [JSON-RPC service manual](https://github.com/AsamK/signal-cli/blob/v0.14.9/man/signal-cli-jsonrpc.5.adoc).
