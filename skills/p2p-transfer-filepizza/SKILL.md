---
name: p2p-transfer-filepizza
description: Use this skill when the user wants to share a local file through the public https://file.pizza site without relying on a normal upload API, especially for one-off large files where a temporary peer-to-peer link is acceptable and a local seeding process can stay online.
---

# P2P Transfer FilePizza

Use the published `filepizza-cli` npm package directly against the public `file.pizza` service. This skill is for the hosted public service only, not a self-hosted server.

The supported interface for agents is the upstream CLI invoked through `npx`. Agents should not operate the `file.pizza` UI directly.

## Default workflow

1. Confirm the file path exists locally.
2. Start the upload directly through the published CLI:

```bash
npx --yes filepizza-cli@0.1.0 share /absolute/path/to/file
```

3. Read the JSON result and use the returned `shortUrl` or `longUrl`.
4. If the user asks whether an upload is still alive, inspect it with:

```bash
npx --yes filepizza-cli@0.1.0 status <upload_id>
```

5. If the user wants to stop seeding, or the transfer is no longer needed, stop it explicitly:

```bash
npx --yes filepizza-cli@0.1.0 stop <upload_id>
```

6. If the file or sharing context is politically sensitive, adversarial, or related to dissidents, activists, journalists, or human rights work, read `references/trust-assumptions.md` before recommending `file.pizza`.

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
- Prefer the public site workflow only for files that are acceptable to expose to a third-party web app at the browser-JavaScript trust level.
- Prefer the short URL for user-facing sharing and the long URL for logging or debugging.
- Prefer keeping exactly one seeding process per upload alive until the recipient confirms they have the file.

## Safety rules

- Treat starting an upload as an external action because it creates a shareable public link.
- Do not use this skill for seed phrases, private keys, raw wallets, or similarly high-risk secrets.
- Do not use this skill by default for covert exfiltration, whistleblowing against a state adversary, or situations where website-delivered JavaScript and browser fingerprinting are unacceptable risks.
- Call out that `file.pizza` is peer-to-peer and the uploader must remain online.
- Call out that WebRTC traffic is encrypted in transit, but the site still serves the client-side JavaScript.
- Do not assume the generated link will keep working after the seeding process exits.

## Gotchas

- `file.pizza` does not expose a normal REST upload API. This skill relies on the programmatic `filepizza-cli` package, which speaks the public FilePizza protocol directly.
- The first run may take longer because `npx --yes` may need to fetch the pinned npm package into the local npm cache.
- Runtime state and upload manifests live under `~/.cache/filepizza-cli/uploads/`, not under this repo.
- The direct CLI exposes `share`, `status`, and `stop`. It does not expose a `list` subcommand.
- The CLI requires local `node` and `npm` in `PATH`.
- Large files still depend on WebRTC behavior; success is not as deterministic as a server-side object store.

## Troubleshooting

- If `share` fails before doing network work, confirm the file path exists locally and is a regular file.
- If `npx` reports a missing binary, install `node` and `npm` or fix `PATH`.
- If `npx` returns an error, rerun the same command directly and inspect stderr.
- If an upload looks alive but the link does not work, confirm the seeding process is still running with `status`.
- If you need to inspect cached local state manually, use:

```bash
ls ~/.cache/filepizza-cli/uploads
python3 -m json.tool ~/.cache/filepizza-cli/uploads/<upload_id>.json
```
