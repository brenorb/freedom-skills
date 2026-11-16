# hyperbeam onboarding

Read this file only when `hyperbeam` is missing, `hyperbeam --help` fails, or the user explicitly asks for setup help.

## Verify the local state

```bash
command -v node
command -v npm
command -v hyperbeam
hyperbeam --help
```

If `hyperbeam` is missing, that is a normal pre-install state.

## Install

Install the published package globally:

```bash
npm install -g hyperbeam
```

Then verify:

```bash
command -v hyperbeam
hyperbeam --help
```

If the binary still does not resolve, the most common problem is that the global npm bin directory is not on `PATH`.

## First safe smoke test

For a local smoke test, run the sending side on one terminal:

```bash
echo 'hello world' | hyperbeam
```

Copy the printed passphrase, then run the receiving side on another terminal:

```bash
hyperbeam <passphrase>
```

If the second side prints `hello world`, the basic pipe is working.

## Reuse the same passphrase after restart

If the user wants to bring back the listening side with the same passphrase:

```bash
hyperbeam <passphrase> -r
```

Keep the `-r` flag after the passphrase.

## Local behavior

Hyperbeam itself does not maintain a large local state directory like Gip. The main operational secret is the passphrase being shared between both ends of the pipe.
