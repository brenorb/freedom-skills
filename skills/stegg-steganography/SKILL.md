---
name: stegg-steganography
description: "Use this skill when Codex needs local steganography with ST3GG via `uvx`: hiding or recovering text or files in image carriers, triaging suspicious stego images, or guiding cautious encode/decode workflows for activists, dissidents, or other users operating in adversarial environments."
---

# stegg-steganography

Use the published `stegg` package through `uvx` as the default path. Keep the workflow local, prefer file-based payloads over inline text, and treat steganography as concealment rather than cryptographic protection.

## Default workflow

1. Check the runtime and the actual published entrypoints:

```bash
uvx stegg --help
uvx --with 'stegg[crypto]' stegg info-cmd
```

2. For real secrets, prefer a file payload and pre-encrypt it with another tool before embedding. If the user only wants a quick demo, `--text` is acceptable. For higher-risk work, read `references/threat-model.md` before encoding.
3. Prefer a lossless carrier the user controls directly, usually PNG. Keep the original carrier untouched and write to a new output path.
4. Encode with `uvx`:

```bash
uvx stegg encode-cmd -i carrier.png -f payload.bin -o stego.png -q
uvx stegg encode-cmd -i carrier.png -f payload.bin -o stego.png -s randomized --seed 12345 -q
```

5. Decode immediately to verify the round trip before the file is shared:

```bash
uvx stegg decode-cmd -i stego.png -q
uvx stegg decode-cmd -i stego.png -o extracted.bin -q
```

6. If the user asks for raw command variants, crypto mode, or troubleshooting patterns, read `references/commands.md`.

## Defaults

- Prefer `uvx stegg ...` over installing a persistent global tool.
- Prefer `--file` over `--text` for anything sensitive or longer than a short demo message.
- Prefer PNG carriers that will stay lossless end-to-end.
- Prefer pre-encrypting the payload with a separate tool such as GPG or age, then embedding the ciphertext file.
- Prefer `decode-cmd` as the first read-only recovery step when inspecting a suspected stego image.
- Keep plaintext, ciphertext, original carrier, and stego output as separate files until verification is complete.

## Safety rules

- Do not describe steganography as protection on its own. It hides the existence of data; it does not replace encryption.
- Do not rely on a carrier that will be recompressed, resized, transcoded, or stripped by a platform in transit.
- Avoid putting sensitive plaintext or passphrases directly on the command line when a file-based workflow is possible.
- Treat extracted payloads as untrusted until inspected. Do not auto-open or execute recovered artifacts.
- Confirm the exact input carrier, payload file, and output path before encoding if there is any ambiguity.
- Do not delete the original carrier or the recovered payload until the round trip has been verified.

## Gotchas

- The current published CLI exposes `encode-cmd` and `decode-cmd`, even though some upstream docs still show `encode` and `decode`.
- Built-in crypto support is only available when invoked with extras, for example `uvx --with 'stegg[crypto]' stegg info-cmd`.
- The current published `analyze` command may be unreliable; use it as a secondary aid, not the primary recovery path.
- Auto-detection on decode usually means you do not need to repeat channels, bit depth, or strategy during normal recovery.
- Standard LSB payloads are fragile under JPEG recompression and social-media processing. For high-risk work, assume lossy platforms will destroy or expose the payload.
