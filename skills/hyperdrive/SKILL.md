---
name: hyperdrive
description: Use this skill when the user wants to create, populate, inspect, seed, fetch from, or mirror a Hyperdrive bundle using the local wrapper script, especially for P2P file bundles, archives, static evidence drops, or read-only mirroring of a remote drive into plain local files.
---

# hyperdrive

Use the bundled Node wrapper in `scripts/hyperdrive_cli.js` to make Hyperdrive usable from the terminal for common file-bundle workflows.

## Default workflow

1. Start with the local action that matches the user's goal.

To create a new local writable drive:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js create --store /absolute/path/to/drive-store --json
```

To add one file into that drive:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js put \
  --store /absolute/path/to/drive-store \
  --source /absolute/path/to/file.txt \
  --path /drops/file.txt \
  --json
```

To import a whole local directory tree into a drive prefix:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js put \
  --store /absolute/path/to/drive-store \
  --source /absolute/path/to/evidence-dir \
  --path /drops/case-123 \
  --json
```

2. To inspect a drive locally, list its entries:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js list --store /absolute/path/to/drive-store --json
```

3. To make the drive available to peers, start seeding and keep the process alive:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js seed --store /absolute/path/to/drive-store --json
```

4. To retrieve one file from a local or remote drive:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js get \
  --store /absolute/path/to/cache-or-drive-store \
  --key <remote-key-if-needed> \
  --path /drops/file.txt \
  --output /absolute/path/to/file.txt \
  --json
```

Omit `--key` when reading from a local writable drive in the same store. Include `--key` when this machine is acting as a read-only client for a remote drive.

5. To mirror a whole drive or subtree into plain local files:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js mirror \
  --store /absolute/path/to/cache-or-drive-store \
  --key <remote-key-if-needed> \
  --dest /absolute/path/to/output-dir \
  --prefix / \
  --json
```

Add `--strip-prefix` when the destination should contain only the subtree contents rather than the full drive path:

```bash
cd skills/hyperdrive/scripts
node hyperdrive_cli.js mirror \
  --store /absolute/path/to/cache-or-drive-store \
  --key <remote-key-if-needed> \
  --prefix /drops/case-123 \
  --strip-prefix \
  --dest /absolute/path/to/output-dir \
  --json
```

6. Only fall back to setup checks or onboarding when the first useful command fails because wrapper dependencies are missing or the local environment is uncertain. In that case, read `references/onboarding.md`.

7. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Treat one `--store` directory as one concrete local drive or cache root.
- Prefer `create`, `put`, and `seed` on the writable side.
- Prefer `put` with a directory source when the user wants a bundle, archive, or evidence drop uploaded in one step.
- Prefer `get`, `list`, and `mirror` on the read-only consumer side.
- Prefer `mirror` when the user wants a plain local folder snapshot, evidence handoff, or archive extraction workflow.
- Prefer `mirror --strip-prefix` when the user wants the subtree contents placed directly inside the destination directory.
- Prefer `--json` so downstream automation can parse keys, paths, versions, and outputs deterministically.
- Prefer action first. Do not front-load setup checks once the wrapper is already known-good in the current environment.

## Safety rules

- Treat seeding, remote fetches, and remote mirroring as external network actions.
- Confirm before seeding a drive that contains sensitive material.
- Confirm before mirroring a remote drive into a local destination that may overwrite or mix with existing files.
- Call out that remote reads depend on at least one writable peer actively seeding the drive.
- Confirm before using a provided remote key when the provenance of that key is unclear.

## Gotchas

- The wrapper is a thin convenience layer around the Hyperdrive library, not an official upstream CLI.
- `create` only creates local drive state; peers cannot read the drive until some process is actively seeding it.
- `put` writes bytes into the drive. It does not automatically seed or publish the result.
- `put` accepts either a single file or a local directory tree. Directory uploads preserve nested paths and local symlinks.
- `get` and `mirror` against a remote key use the local `--store` directory as a cache.
- A remote `list` or `get` can fail or time out when no seeder is online.
- Hyperdrive paths are drive-internal paths like `/drops/file.txt`, not local filesystem paths.
- `mirror` writes plain files to the destination directory. It is useful for evidence drops and static bundles, but it is not a bidirectional sync tool.
- `mirror --strip-prefix` rewrites output paths relative to the chosen prefix. Without it, the full drive path is preserved under the destination root.
- This wrapper assumes a simple one-drive-per-store workflow. Use separate `--store` directories for separate drives when you want clear isolation.
