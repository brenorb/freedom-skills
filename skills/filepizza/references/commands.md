# filepizza commands

Read this file only when the default workflow in `SKILL.md` is not enough.

## Upload a file

```bash
python3 skills/filepizza/scripts/filepizza_public.py upload /absolute/path/to/file
```

Example result:

```json
{
  "ok": true,
  "upload_id": "20260610-120000-ab12cd34",
  "short_url": "https://file.pizza/download/abcd1234",
  "long_url": "https://file.pizza/download/pepperoni/mushroom/olive/basil",
  "launcher": "tmux",
  "tmux_session": "filepizza_20260610-120000-ab12cd34",
  "pid": 43152,
  "status": "seeding"
}
```

## Inspect active and past uploads

```bash
python3 skills/filepizza/scripts/filepizza_public.py list
python3 skills/filepizza/scripts/filepizza_public.py status 20260610-120000-ab12cd34
```

## Stop seeding

```bash
python3 skills/filepizza/scripts/filepizza_public.py stop 20260610-120000-ab12cd34
```

## Operational notes

- Runtime state lives under `~/.cache/freedom-skills/filepizza/`.
- Upload logs are saved there as `*.log`.
- If `tmux` is installed, the wrapper prefers a detached tmux session automatically and records the session name in the manifest JSON.
- The wrapper keeps a headless browser process alive so the public link stays usable.
- If Node, npm, or the browser runtime are missing, the wrapper bootstraps them on first use.

## Troubleshooting

- If a manual upload fails in Arc, retry in Chrome. Browser-specific WebRTC or site-compatibility quirks can matter.
- If the wrapper returns no links, inspect the saved `*.log` file for the upload under `~/.cache/freedom-skills/filepizza/uploads/`.
- If an upload looks alive but the link does not work, confirm the seeding process is still running with `status` or `list`.
