# Croc trust assumptions

Croc encrypts the file contents in transit. That does not protect a transfer code from your own agent stack. Treat the code and any receive command, URL, or QR code containing it as the same access capability. Read the installed [local privacy choice](local-privacy.md) before handling one.

## Hosted or unknown agent stack

Decide where inference runs and where tool output, transcripts, traces, logs, telemetry, and synced history go. A shell running on your computer can still return output to a hosted model. On first use ask for the local privacy choice instead of assuming either permission or prohibition. With an effective **allowed** choice, the user accepts invite exposure to this model/history under that saved choice; the helper may generate and return a code. With **private**, apply this boundary:

- Use a private terminal that is not shared, recorded, or relayed to the agent, or the bundled `scripts/transfer.py` helper with `CROC_SECRET` provisioned locally. In private mode it returns only sanitized JSON status/errors. Do not dump raw output even when debugging a failure. See [automation](automation.md).
- Use `--disable-clipboard` so Croc does not copy the invite to a clipboard that may sync or be shared. Keep the code and code-bearing URL local; do not forward them to the inference provider, an online decoder, or a logging service.
- Let the user retrieve the invite from that private terminal, enter it locally at the receiver, or pass it through an authorized private channel that does not expose it to the agent or provider. A private human terminal is not the same as an agent terminal whose output enters a transcript.

## Verified local and trusted end to end

The saved choice still applies: do not override private because inference is local, or override an explicit allowed choice because it is hosted. Explain the relevant trust assumptions when the user chooses. Even with allow, avoid unnecessary logs/persistence and disclosure to anyone other than the intended recipient; do not use `--remember` for a one-time invite. Changing the preference does not erase previous history or revoke a code.

If an invite escapes the intended boundary, stop the sender and generate a new invite before continuing.

In [Croc v11.6.6](https://github.com/schollz/croc/blob/v11.6.6/src/croc/croc.go#L1753-L1778), the sender can put a code-bearing receive command and web URL on stderr and attempts to copy the invite by default. The [tagged CLI guide](https://github.com/schollz/croc/blob/v11.6.6/README.md#clipboard-options) documents the clipboard switch and what the extended option copies.
