---
name: p2p-transfer-filepizza
description: Share a local file with a temporary peer-to-peer download link using filepizza-cli via npx, inspect an active share, or stop seeding. Use when the sender can stay online until the recipient finishes downloading.
---

# P2P Transfer FilePizza

Use the published `filepizza-cli` npm package via `npx` with the public `file.pizza` service. The CLI calls FilePizza APIs for connection setup and link management, then transfers file bytes over WebRTC to the recipient.

The sender runs the CLI; the recipient opens the returned link in a browser. Sharing requires no sender-side browser, Playwright, or tmux.

## Default workflow

If the file or sharing context is sensitive, read `references/trust-assumptions.md` before recommending FilePizza or starting a share.

1. Start sharing the requested file:

```bash
npx --yes filepizza-cli@0.1.0 share /absolute/path/to/file
```

2. Save `uploadId` from the JSON result and give the recipient `shortUrl` or `longUrl`. Keep the sender online until the download finishes.
3. If the user asks whether a share is still alive, inspect it with:

```bash
npx --yes filepizza-cli@0.1.0 status <upload_id>
```

4. If the user wants to stop seeding, or the transfer is no longer needed, stop it explicitly:

```bash
npx --yes filepizza-cli@0.1.0 stop <upload_id>
```

Confirm the result reports `status: "stopped"` and `alive: false`.

Example `share` result:

```json
{
  "ok": true,
  "uploadId": "20260703-203624-c1c0361e",
  "filePath": "/absolute/path/to/file",
  "fileName": "example.zip",
  "pid": 43152,
  "status": "seeding",
  "startedAt": "2026-07-03T20:36:25.588Z",
  "updatedAt": "2026-07-03T20:36:27.163Z",
  "peerId": "dd7769bc-c402-460c-b886-67e3b3ea1366",
  "shortSlug": "abcd1234",
  "longSlug": "pepperoni/mushroom/olive/basil",
  "shortUrl": "https://file.pizza/download/abcd1234",
  "longUrl": "https://file.pizza/download/pepperoni/mushroom/olive/basil",
  "alive": true
}
```

## Defaults

- Prefer the published CLI over ad hoc browser automation or manual UI operation.
- Prefer the pinned package version shown in this skill unless the user explicitly wants a different release.
- Use this workflow only when the sender trusts the CLI and its dependencies, and the recipient can accept the FilePizza web client's trust assumptions.
- Prefer the short URL for user-facing sharing and the long URL for logging or debugging.
- Prefer keeping exactly one seeding process per upload alive until the recipient confirms they have the file.

## Safety rules

- Treat starting an upload as an external action because it creates a shareable public link.
- Do not use this skill for seed phrases, private keys, raw wallets, or similarly high-risk secrets.
- Do not use this workflow when peer IP exposure, service metadata, or the recipient's website-delivered JavaScript and browser fingerprinting are unacceptable risks.
- Call out that `file.pizza` is peer-to-peer and the uploader must remain online.
- Call out that WebRTC traffic is encrypted in transit; the sender runs the npm CLI locally and the recipient runs website-delivered JavaScript.
- Do not assume the generated link will keep working after the seeding process exits.

## Gotchas

- FilePizza's service APIs coordinate the transfer; file bytes travel over WebRTC rather than through an HTTP file upload.
- The first run may take longer because `npx --yes` may need to fetch the pinned npm package into the local npm cache.
- Runtime state and upload manifests live under `~/.cache/filepizza-cli/uploads/`, not under this repo.
- The direct CLI exposes `share`, `status`, and `stop`. It does not expose a `list` subcommand.
- The pinned CLI requires Node.js 22 or newer and npm in `PATH`.
- Large files still depend on WebRTC behavior; success is not as deterministic as a server-side object store.

## Troubleshooting

- If `share` fails before doing network work, confirm the file path exists locally and is a regular file.
- If `npx` reports a missing binary, install `node` and `npm` or fix `PATH`.
- If `share` times out, inspect the upload ID named in the error with `status` before retrying: the detached worker may still be running. Stop an unwanted share before starting another.
- For other errors, inspect stderr and resolve the reported cause before retrying.
- If an upload looks alive but the link does not work, confirm the seeding process is still running with `status`.
- If you need to inspect cached local state manually, use:

```bash
ls ~/.cache/filepizza-cli/uploads
python3 -m json.tool ~/.cache/filepizza-cli/uploads/<upload_id>.json
```
