# gip-transport onboarding

Read this file only when `gip` or `git-remote-git+pear` is missing, `gip list --json` fails because Gip is not installed yet, or the user explicitly asks for setup help.

## Verify the local state

```bash
command -v git
command -v npm
command -v gip
command -v git-remote-git+pear
gip list --json
```

If `gip` or `git-remote-git+pear` is missing, that is a normal pre-install state.

## Install

Install the published package globally:

```bash
npm install -g gip-transport
```

That global install should provide both of these binaries:

- `gip`
- `git-remote-git+pear`

Then verify:

```bash
command -v gip
command -v git-remote-git+pear
gip
```

If the binaries still do not resolve, the most common problem is that the global npm bin directory is not on `PATH`.

## First repo creation

Create a P2P remote and record the returned URL:

```bash
gip new my-repo
```

This creates the remote in Gip's local store. It does not create a Git working tree in the current directory.

## Attach the remote to an existing Git repo

Inside the Git checkout that should publish to the new Gip remote:

```bash
git remote add origin git+pear://<key>/my-repo
git push origin main
```

If the local branch is not `main`, replace it with the real branch name.

## Keep the repo available

Start seeding from a long-lived shell:

```bash
gip seed
```

If the process stops and no other peer is seeding the repo, other users may no longer be able to clone or fetch.

## Optional: mirror an existing Gip remote locally

If the user already has a `git+pear://` URL and wants this machine to cache or reseed it:

```bash
gip add git+pear://<key>/my-repo
gip list --json
```

## Optional: inspect identity and config

```bash
gip id
gip config
gip config get seed-read-only
```

By default, Gip can reseed read-only repos that this machine has mirrored. Turn that off only when the user explicitly wants a non-reseeding client:

```bash
gip config set seed-read-only off
```

## Local state

Gip stores its local database, keys, mirrored repos, and config under:

```text
~/.gip
```

Treat that directory as important local state. Deleting it or running `gip delete <name>` affects locally stored Gip repos on this machine.
