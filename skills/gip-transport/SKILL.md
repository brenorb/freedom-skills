---
name: gip-transport
description: Use this skill when the user wants to create, host, seed, clone, fetch, or push a Git repository over Holepunch P2P remotes via `gip`, `gip-transport`, or `git+pear://` URLs, or when they need to configure blind peers or reseeding behavior for a Gip repo.
---

# gip-transport

Use the local `gip` CLI and `git-remote-git+pear` helper to work with P2P Git remotes over Holepunch.

## Default workflow

1. Start with the command that matches the user's goal. If the user wants a new P2P remote, create it with Gip:

```bash
gip new my-repo
```

2. Add the returned `git+pear://` URL as a normal Git remote inside the working tree:

```bash
git remote add origin git+pear://<key>/my-repo
```

3. Use normal Git transport commands once the remote exists:

```bash
git push origin main
git fetch origin
git clone git+pear://<key>/my-repo
git push origin --delete old-branch
```

4. If the user wants the repo available to other peers, start seeding and keep that process alive:

```bash
gip seed
```

5. If the user wants to mirror a remote into local `.gip` storage without creating a checkout first, add it directly:

```bash
gip add git+pear://<key>/my-repo
```

6. Only fall back to setup checks or onboarding when the first useful command fails because Gip is missing, the remote helper is missing, or the local environment is otherwise uncertain. In that case:

```bash
command -v bare
command -v gip
command -v git-remote-git+pear
gip list --json
```

Then read `references/onboarding.md`.

7. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Treat Gip as Git transport plus a local P2P repo catalog, not as a full Git forge.
- Prefer standard `git push`, `git fetch`, and `git clone` once the `git+pear://` remote already exists.
- Prefer `gip` only for repo creation, local mirroring, seeding, identity, and config management.
- Prefer `gip seed` in a dedicated long-lived terminal or tmux session instead of starting and forgetting it.
- Prefer explicit branch names on the first push.
- Prefer `gip add <url>` only when the user wants a local mirror or wants this machine to help reseed the repo. Direct `git clone` is enough for ordinary consumer use.
- Prefer action first. Do not front-load setup checks once Gip is already verified in the current environment.

## Safety rules

- Treat `gip new`, `gip add`, `gip seed`, `git push` to a `git+pear://` remote, `git push --delete`, `gip delete`, and `gip config ...` as state-changing or networked actions.
- Confirm before the first push to a new P2P remote.
- Confirm before deleting a branch or deleting a locally stored Gip repo.
- Call out that availability depends on peers actively seeding the repo.
- Call out that Gip does not provide GitHub-style PRs, issues, protected branches, CI, or hosted backups by itself.
- Confirm before adding or removing blind peers when the user is not already operating that infrastructure.

## Gotchas

- This is not 1:1 with Git hosting. The push, fetch, and clone verbs stay familiar, but remote creation and availability are separate concerns.
- `gip new` creates the P2P remote in local Gip storage under `~/.gip`; it does not initialize or replace the working tree in the current directory.
- The published `gip` CLI runs via the `bare` runtime. If `bare` is not installed or not on `PATH`, commands can fail with `env: bare: No such file or directory`.
- `git+pear://` remotes only work when `git-remote-git+pear` is installed and on `PATH`.
- If nobody is online seeding the repo, clone and fetch can stall or fail until a seeder comes back.
- `gip seed` is a long-lived availability process, not a one-shot publish step.
- Read-only mirrored repos reseed by default. Check with `gip config get seed-read-only`; disable with `gip config set seed-read-only off` when the user does not want this machine to re-announce cloned data.
- `gip add` mirrors a repo into local Gip storage. `git clone` creates a Git checkout. They overlap, but they are not interchangeable.
- Gip's repo URLs are stateful P2P addresses, not stable hostnames. Prefer the exact `git+pear://...` URL returned by `gip new` or `gip list` instead of hand-editing it.
- `gip delete <name>` deletes the locally stored Gip repo record and wipes the local core for that repo name. It is not the same operation as deleting a remote Git branch.
- Blind peers improve discoverability and availability, but they do not change the need for someone to actually hold and seed the repo data.
- Upstream still lists multi-signer support as TODO.
