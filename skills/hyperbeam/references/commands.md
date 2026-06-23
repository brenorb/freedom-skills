# hyperbeam command patterns

Read this file only when the user needs raw `hyperbeam` command patterns beyond the default workflow in `SKILL.md`.

## Inspect local setup

```bash
command -v hyperbeam
hyperbeam --help
```

## Send workflow

### One-shot text or stdout stream

```bash
echo 'hello world' | hyperbeam
```

### Single file

```bash
cat /absolute/path/to/file.bin | hyperbeam
```

### Directory or many files via tar stream

```bash
tar czf - /absolute/path/to/folder | hyperbeam
```

Each sending command prints a passphrase on stderr. Share that passphrase with the receiving peer and tell them whether the payload is plain stdout, a single file, or a tar stream.

## Receive workflow

### Plain stdout stream

```bash
hyperbeam <passphrase>
```

### Single file

```bash
hyperbeam <passphrase> > /absolute/path/to/file.bin
```

### Tar stream

```bash
hyperbeam <passphrase> | tar xzf -
```

## Reuse the same passphrase after restarting the listener

```bash
hyperbeam <passphrase> -r
```

Use this order. The CLI reads the passphrase from the first positional argument.

## Large command output handoff

Sender:

```bash
sqlite3 database.db .dump | hyperbeam
```

Receiver:

```bash
hyperbeam <passphrase> > dump.sql
```

## Full docs

If the user needs the full upstream command surface or implementation details beyond this skill:

- Project repo: `https://github.com/mafintosh/hyperbeam`
- Upstream README: `https://github.com/mafintosh/hyperbeam/blob/master/README.md`
- npm package: `https://www.npmjs.com/package/hyperbeam`
