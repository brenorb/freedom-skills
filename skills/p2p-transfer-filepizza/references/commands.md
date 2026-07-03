# p2p-transfer-filepizza commands

Read this file only when the default workflow in `SKILL.md` is not enough.

## Upload a file

```bash
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py upload /absolute/path/to/file
```

Example result:

```json
{
  "ok": true,
  "upload_id": "share_01JZ7J3MYTQ4X4QH2M2M6N6T7K",
  "short_url": "https://file.pizza/download/abcd1234",
  "long_url": "https://file.pizza/download/pepperoni/mushroom/olive/basil",
  "file": "/absolute/path/to/file",
  "pid": 43152,
  "alive": true,
  "status": "seeding"
}
```

## Inspect active and past uploads

```bash
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py list
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py status share_01JZ7J3MYTQ4X4QH2M2M6N6T7K
```

## Stop seeding

```bash
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py stop share_01JZ7J3MYTQ4X4QH2M2M6N6T7K
```

## Operational notes

- The Python wrapper delegates to `npx --yes filepizza-cli@0.1.0 ...` by default.
- You can override the package spec with `FILEPIZZA_CLI_SPEC`, for example `FILEPIZZA_CLI_SPEC=filepizza-cli@0.1.1`.
- Runtime state lives under `~/.cache/filepizza-cli/uploads/`.
- `list` reads local manifest JSON from that cache directory and marks uploads `alive` by checking whether the recorded pid still exists.
- The wrapper requires `node` and `npm` in `PATH`.
- The first run may spend extra time downloading the npm package into the local npm cache.

## Troubleshooting

- If `upload` fails before doing network work, confirm the file path exists locally and is a regular file.
- If the wrapper reports a missing binary, install `node` and `npm` or fix `PATH`.
- If `npx` returns an error, rerun the same command directly to inspect the upstream CLI behavior:

```bash
npx --yes filepizza-cli@0.1.0 share /absolute/path/to/file
```

- If an upload looks alive but the link does not work, confirm the seeding process is still running with `status` or `list`.
