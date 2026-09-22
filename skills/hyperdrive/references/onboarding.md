# hyperdrive wrapper onboarding

Read this file only when the wrapper dependencies are missing, `node scripts/hyperdrive_cli.js ...` fails before it reaches Hyperdrive itself, or the user explicitly asks for setup help.

## Verify the local state

From the skill's `scripts/` directory:

```bash
command -v node
command -v npm
node hyperdrive_cli.js --help
```

If the script fails with `Cannot find module ...`, install the local wrapper dependencies.

## Install the wrapper dependencies

From:

```bash
skills/hyperdrive/scripts
```

run:

```bash
npm install
```

Then verify:

```bash
node hyperdrive_cli.js --help
```

## First safe smoke test

Create a local drive:

```bash
node hyperdrive_cli.js create --store /tmp/hyperdrive-demo --json
```

Put one local file into it:

```bash
node hyperdrive_cli.js put \
  --store /tmp/hyperdrive-demo \
  --source /absolute/path/to/file.txt \
  --path /file.txt \
  --json
```

Or import a whole directory tree:

```bash
node hyperdrive_cli.js put \
  --store /tmp/hyperdrive-demo \
  --source /absolute/path/to/evidence-dir \
  --path /case-123 \
  --json
```

List the contents:

```bash
node hyperdrive_cli.js list --store /tmp/hyperdrive-demo --json
```

Mirror the drive back to a plain local directory:

```bash
node hyperdrive_cli.js mirror \
  --store /tmp/hyperdrive-demo \
  --dest /tmp/hyperdrive-out \
  --json
```

Mirror only a subtree directly into the destination root:

```bash
node hyperdrive_cli.js mirror \
  --store /tmp/hyperdrive-demo \
  --prefix /case-123 \
  --strip-prefix \
  --dest /tmp/hyperdrive-out \
  --json
```

## Local state

The wrapper uses the directory passed with `--store` as a Corestore root. Treat that directory as the local state for the drive.
