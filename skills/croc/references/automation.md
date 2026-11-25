# Non-interactive live transfers

## Secret delivery

Read the installed [local privacy choice](local-privacy.md) first. With **allowed**, the sender helper generates a fresh random code when `CROC_SECRET` is absent and includes `code` in its `running` event. The agent may use it to set `CROC_SECRET` on the intended receiver through an authorized tool/channel. With **private**, provision the same fresh, high-entropy `CROC_SECRET` in both child environments through trusted local automation; never return it to the model. A local process environment is not inherently secret from its host or same-user processes. Avoid unnecessary logs and shell history in either mode; see [trust assumptions](trust-assumptions.md).

The bundled helper invokes Croc without stdin or a controlling terminal, suppresses both output streams at the OS boundary, and emits `running` followed by `completed` or `failed`. It gives Croc a temporary `HOME`/`XDG_CONFIG_HOME` so saved options cannot override the intended receive code, relay or collision policy; the user's Croc configuration stays untouched. Use explicit helper flags or environment settings such as `CROC_RELAY` for custom configuration. Completion requires Croc to exit 0; check the received manifest/hashes separately. No TTY emulation, `read`, `yes | croc`, clipboard or `--classic` is needed.

```bash
# The receiver needs CROC_SECRET; in private mode inject it locally on both sides.
# Resolve scripts/ from the skill folder.
# Start on the sender, then run the receiver concurrently on the other endpoint.
python3 scripts/transfer.py send "/absolute/path/file" "/absolute/path/folder"
python3 scripts/transfer.py receive "/absolute/path/empty-directory"
```

The destination must already exist and be empty. Do not let another process populate it during the transfer. The helper rejects `CROC_STORE_TOKEN`: Croc otherwise prioritizes it over `CROC_SECRET` and receives a hosted transfer instead. The helper accepts the offered transfer automatically, so establish the intended sender, allowed inputs and receiving authorization beforehand. It does not provide a pre-write manifest inspection protocol. It supports POSIX hosts (tested on macOS and Linux); the underlying Croc CLI also supports other platforms.

## Flags that matter

For a verified local/trusted stack where raw Croc output may stay within the trust boundary, the equivalent direct commands are:

```bash
croc --yes --ignore-stdin --disable-clipboard --no-update-check send -- "/absolute/path/file"
croc --yes --disable-clipboard --no-update-check --out "/absolute/path/empty-directory"
```

- `--yes` suppresses acceptance prompts; it does not supply a missing code. `CROC_SECRET` supplies the code on both endpoints.
- `--ignore-stdin` is essential when sending named files from an agent executor with piped stdin: Croc v11.6.6 otherwise treats stdin as the payload instead of the named files. `/dev/null` alone does not reproduce a pipe; the E2E regression control supplies an actual pipe with a distinct payload.
- `--disable-clipboard` prevents invite copying; it does not redact Croc's output. The helper suppresses both streams, even on failure.
- `--yes` does not define a collision policy. For explicitly authorized direct transfers into existing destinations, `--rename` keeps both versions, or `--overwrite` permits overwrite/resume. The helper intentionally requires an empty directory instead.
- `--no-update-check` avoids the transfer's background update query. It does not change transfer transport.

## Deadlines, failures and relays

Put helper options before `send`/`receive`. `--croc /path/to/croc` selects an executable. `--relay host:port` selects an authorized relay; `--relay-only` adds `--no-local --transport relay` to the sender. Use both endpoints' matching relay settings. The defaults retain Croc's normal transport selection; never silently switch an approved relay or a direct-only requirement.

Exit 0 means completed; exit 1 reports a nonzero Croc exit or a closed status-output pipe; exit 2 reports invalid prerequisites or failure to start; exit 124 is the total deadline; exit 130 is SIGINT interruption and exit 143 is SIGTERM cancellation. Missing secrets and nonempty destinations fail before starting Croc. Errors are deliberately generic because raw diagnostics can contain the code. A timeout, handled cancellation or closed status pipe terminates/reaps the child and preserves any partial received files; do not automatically retry into that nonempty directory. SIGKILL cannot be handled; an executor using it must manage the child separately. Use an approved fresh directory or handle resume explicitly through the direct CLI.

## Reproducible verification

Repository maintainers can run `python3 tests/croc/e2e.py --croc /path/to/croc-v11.6.6 --report /path/to/report.json` from the repository root. This real-binary harness uses only synthetic fixtures and a loopback relay, checks that child fd 0/1/2 are not TTYs and `/dev/tty` cannot open, compares the complete received file manifest and SHA-256 values, and includes negative controls. The repository's Croc workflow downloads checksum-verified v11.6.6 releases on Linux and macOS and publishes sanitized JSON evidence as an Actions artifact. These tests establish the exercised paths; they do not establish public-relay availability or behavior on untested platforms.
