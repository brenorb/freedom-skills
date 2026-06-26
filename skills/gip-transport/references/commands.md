# gip-transport command patterns

Read this file only when the user needs raw `gip` and `git+pear://` command patterns beyond the default workflow in `SKILL.md`.

## Inspect local setup

```bash
command -v bare
command -v gip
command -v git-remote-git+pear
gip list --json
```

## Create a new P2P repo

```bash
gip new my-repo
```

## List locally known Gip repos

```bash
gip list
gip list --json
```

## Add a Gip remote to a Git checkout

```bash
git remote add origin git+pear://<key>/my-repo
git remote -v
```

## Push, fetch, and clone

```bash
git push origin main
git fetch origin
git clone git+pear://<key>/my-repo
git push origin --delete old-branch
```

## Mirror a remote into local Gip storage

```bash
gip add git+pear://<key>/my-repo
```

Use this when the user wants local caching or reseeding without treating the repo as only a checked-out working tree.

## Seed locally known Gip repos

```bash
gip seed
```

## Show the local public key

```bash
gip id
```

Use this when the user needs to share their public key with blind peer operators.

## Inspect config

```bash
gip config
gip config get blind-peers
gip config get seed-read-only
```

## Change config

```bash
gip config set seed-read-only on
gip config set seed-read-only off
gip config add blind-peers <z32-key>
gip config remove blind-peers <z32-key>
```

## Delete a locally stored Gip repo

```bash
gip delete my-repo
```

This deletes the locally stored Gip repo record and local core for that repo name on this machine. It is not the same as deleting a Git branch from a remote.

## Full docs

If the user needs the full upstream command surface or implementation details beyond this skill:

- Project repo: `https://github.com/holepunchto/gip-transport`
- Upstream README: `https://github.com/holepunchto/gip-transport/blob/main/README.md`
