# p2p-transfer-filepizza commands

Read this file only when the default workflow in `SKILL.md` is not enough.

## Upload a file

```bash
npx --yes filepizza-cli@0.1.0 share /absolute/path/to/file
```

Example result:

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

## Inspect one upload

```bash
npx --yes filepizza-cli@0.1.0 status 20260703-203624-c1c0361e
```

## Stop seeding

```bash
npx --yes filepizza-cli@0.1.0 stop 20260703-203624-c1c0361e
```

## Inspect cached manifests manually

The upstream CLI does not expose `list`. If you need to inspect cached local state:

```bash
ls ~/.cache/filepizza-cli/uploads
python3 -m json.tool ~/.cache/filepizza-cli/uploads/<upload_id>.json
```

## Operational notes

- The skill intentionally invokes the published package directly: `npx --yes filepizza-cli@0.1.0 ...`.
- Runtime state lives under `~/.cache/filepizza-cli/uploads/`.
- The CLI requires `node` and `npm` in `PATH`.
- The first run may spend extra time downloading the npm package into the local npm cache.
- `status` and `stop` operate on the upload identifier returned by `share`.

## Troubleshooting

- If `share` fails before doing network work, confirm the file path exists locally and is a regular file.
- If `npx` reports a missing binary, install `node` and `npm` or fix `PATH`.
- If `npx` returns an error, rerun the same command directly and inspect stderr.
- If an upload looks alive but the link does not work, confirm the seeding process is still running with `status`.
