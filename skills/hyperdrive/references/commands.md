# hyperdrive wrapper command patterns

Read this file only when the user needs raw wrapper command patterns beyond the default workflow in `SKILL.md`.

All commands are run from:

```bash
skills/hyperdrive/scripts
```

## Create a drive

```bash
node hyperdrive_cli.js create --store /tmp/my-drive --json
```

## Put a file into a writable local drive

```bash
node hyperdrive_cli.js put \
  --store /tmp/my-drive \
  --source /absolute/path/to/report.pdf \
  --path /drops/report.pdf \
  --json
```

If `--path` is omitted, the wrapper uses the source basename at the drive root.

## Put a directory tree into a writable local drive

```bash
node hyperdrive_cli.js put \
  --store /tmp/my-drive \
  --source /absolute/path/to/evidence-dir \
  --path /drops/case-123 \
  --json
```

Nested files are written under `/drops/case-123/...`.

## List entries in a local drive

```bash
node hyperdrive_cli.js list --store /tmp/my-drive --json
node hyperdrive_cli.js list --store /tmp/my-drive --prefix /drops --json
```

## Get a file from a local or remote drive

Local:

```bash
node hyperdrive_cli.js get \
  --store /tmp/my-drive \
  --path /drops/report.pdf \
  --output /tmp/report.pdf \
  --json
```

Remote:

```bash
node hyperdrive_cli.js get \
  --store /tmp/hyperdrive-cache \
  --key <hex-or-z32-key> \
  --path /drops/report.pdf \
  --output /tmp/report.pdf \
  --json
```

## Mirror a drive to a plain local directory

Local:

```bash
node hyperdrive_cli.js mirror \
  --store /tmp/my-drive \
  --dest /tmp/mirror-out \
  --json
```

Local subtree only, stripped into the destination root:

```bash
node hyperdrive_cli.js mirror \
  --store /tmp/my-drive \
  --prefix /drops/case-123 \
  --strip-prefix \
  --dest /tmp/mirror-out \
  --json
```

Remote:

```bash
node hyperdrive_cli.js mirror \
  --store /tmp/hyperdrive-cache \
  --key <hex-or-z32-key> \
  --dest /tmp/mirror-out \
  --json
```

## Seed a writable drive for peers

```bash
node hyperdrive_cli.js seed --store /tmp/my-drive --json
```

Keep that process alive while peers are listing, getting, or mirroring from the remote key.
