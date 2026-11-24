# Croc trust assumptions

Croc encrypts the file contents in transit. That does not protect a transfer code from your own agent stack. Treat the code and any receive command, URL, or QR code containing it as the same secret.

## Hosted or unknown agent stack

Decide where inference runs and where tool output, transcripts, traces, logs, telemetry, and synced history go. The model's license or availability of its weights tells you nothing about that data path. A shell running on your computer can still return output to a hosted model. If any part of the path is remote, or you cannot verify the path, use this default:

- Use a private terminal that is not shared, recorded, or relayed to the agent, or the bundled `scripts/transfer.py` helper with `CROC_SECRET` provisioned locally. The helper discards both Croc stdout and stderr and returns only sanitized JSON states/errors; it does not deliver the secret between endpoints. Do not dump raw output even when debugging a failure. See [automation](automation.md).
- Use `--disable-clipboard` so Croc does not copy the invite to a clipboard that may sync or be shared. Keep the code and code-bearing URL local; do not forward them to the inference provider, an online decoder, or a logging service.
- Let the user retrieve the invite from that private terminal, enter it locally at the receiver, or pass it through an authorized private channel that does not expose it to the agent or provider. A private human terminal is not the same as an agent terminal whose output enters a transcript.

## Verified local and trusted end to end

A local model may handle the invite when that helps the authorized transfer, provided inference and secret-bearing tool output, traces, logs, telemetry, and sync are all kept within the verified local trust boundary. There is no blanket ban on local handling. Still avoid shared output, persistence by default, and disclosure to anyone other than the intended recipient. Do not put the literal in command arguments or shell history; do not use `--remember` for a one-time invite.

If an invite escapes the intended boundary, stop the sender and generate a new invite before continuing.

In [Croc v11.6.6](https://github.com/schollz/croc/blob/v11.6.6/src/croc/croc.go#L1753-L1778), the sender can put a code-bearing receive command and web URL on stderr and attempts to copy the invite by default. The [tagged CLI guide](https://github.com/schollz/croc/blob/v11.6.6/README.md#clipboard-options) documents the clipboard switch and what the extended option copies.
