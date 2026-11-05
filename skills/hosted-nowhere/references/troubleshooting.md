# Failure and retry guidance

| Failure | Recovery |
| --- | --- |
| `npx` is missing | Use an available Node.js 20+ installation with npm/npx, then retry the original `npx --yes nowhere-cli` action. A globally installed `nowhere` executable is not required. |
| npm download/cache error | Check the reported registry, network, or cache error. First use needs registry access unless the package is cached. Use package `nowhere-cli`, not the unrelated `nowhere` package. Retry the requested action after fixing the cause; do not install globally as a workaround. |
| Unknown flag/subcommand | Read targeted help, e.g. `npx --yes nowhere-cli update --help` or `npx --yes nowhere-cli forum private list --help`, and check `npx --yes nowhere-cli --version`. Reproduce the tested baseline with `npx --yes nowhere-cli@0.3.0` if needed. |
| Invalid JSON or missing fields | Fix the input file using the selected app example and actual validation error. Keep required key ownership and the requested content; do not replace them with dummy values. Retry local encoding only after fixing input. |
| Decode error | Confirm the complete fragment, quotes, and intended URL. Encrypted links can resemble corrupted links; use the known password, not a guessed one. Preserve the original input while diagnosing. |
| Wrong signing/owner key | Check the embedded public key against the authorized key/signer. Do not generate a replacement identity or overwrite the site's owner to bypass the error. |
| Read timeout or empty results | Check the same original URL/fragment, relay overrides, forum salt, and moderation. A failed connection or empty filtered view does not prove there is no data. Retry reads after correcting the cause. |
| Publish timeout or partial acknowledgement | Treat the outcome as uncertain. Save returned event IDs/receipts. Read back through the same namespace/relays before considering a retry. Do not recreate checkout, signatures, posts, or chat as a diagnostic action. |
| Some owner records fail decryption | Retain JSON and per-record errors. Check the owner key, original link, and event source. Report successful/unreadable counts; never present a CSV that skips failures as complete. |
| Browser Share Link stale after edits | Return to Share Link, regenerate, reopen that exact link, and recheck content/protections. |

Use bounded read retries (at most two after the first failure). If still unresolved,
report the failing operation and evidence. For writes, retry only when absence is
established well enough for that operation or the user explicitly accepts the
duplicate risk; a timeout or an empty list alone is insufficient. Preserve the
original signed event for retransmission if the tool exposes it rather than
generating a distinct event. Do not invent a replay command the CLI lacks.

Chat is ephemeral, so a later read cannot establish non-delivery. Store relay
retention is inherently unreliable; see [the Store deprecation](store.md).
Invoice generation may contact a live payment service; inspect any existing
invoice and its expiry before creating another.

For a reproducible check of this skill's examples, run
`python3 -m unittest discover -s tests/hosted_nowhere -v` from the repository root.
Tests invoke `nowhere-cli@0.3.0` through `npx`, downloading it on first use if needed;
no global install is required. They use actual CLI subprocesses, temporary
data/config, and an in-memory loopback relay for publish/readback and failure
checks. No public relays are used.
`NOWHERE_CLI_COMMAND` may contain a JSON argv array such as
`["node","/absolute/path/to/nowhere-cli/dist/cli.js"]` for an existing build.
