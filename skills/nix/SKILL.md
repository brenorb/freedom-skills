---
name: nix
description: "Use this skill when the user wants to work with Nix off the shelf: run a package without installing it, search nixpkgs, write or debug flakes and dev shells, build derivations, evaluate Nix expressions, or make NixOS/Home Manager changes safely."
metadata:
  version: "0.1.0"
  inspired-by: "https://github.com/olafkfreund/nix-skills"
---

# Nix

Start with the command that matches the goal. Only check the environment if that command fails.

## Default workflow

1. Run a tool once without installing it:

```bash
nix shell nixpkgs#jq -c jq --version
nix run nixpkgs#bitcoin-core -- --version
```

2. Find a package or program in nixpkgs:

```bash
nix search nixpkgs electrum
```

3. Inside a flake project, use the flake commands:

```bash
nix flake show          # list outputs
nix develop             # enter the dev shell
nix build               # build the default package
nix flake check         # run checks
```

4. Write or debug a Nix expression:

```bash
nix eval --raw .#packages.x86_64-linux.hello.name
nix eval --json --expr 'builtins.attrNames (import <nixpkgs> {})' | head
nix repl                # interactive exploration
nix build --show-trace  # full error traces
```

5. For NixOS or Home Manager changes, build first and only switch after the user approves:

```bash
nixos-rebuild build --flake .#myhost        # or: darwin-rebuild build --flake .#myhost
home-manager build --flake .#user@host
# only after explicit approval:
nixos-rebuild switch --flake .#myhost
home-manager switch --flake .#user@host
```

6. For the full command cheat sheet, read [references/commands.md](references/commands.md). For flake structure and devShell patterns, read [references/flakes.md](references/flakes.md).

## Defaults

- Prefer flakes over legacy channels (`nix-channel`); pin inputs in `flake.lock`.
- Prefer `nix shell nixpkgs#<pkg> -c <cmd>` for one-off tools; it leaves no profile behind.
- Prefer `nix build` / `nixos-rebuild build` over `switch` so failures never touch the running system.
- Prefer `--json` output for anything the agent will parse.
- If `nix` says `experimental Nix feature 'nix-command' is disabled`, rerun with `--extra-experimental-features 'nix-command flakes'`.

## Safety rules

- `nixos-rebuild switch`, `darwin-rebuild switch`, `home-manager switch`, and `nix-collect-garbage -d` change the live system or delete store paths. Never run them without explicit user approval; build first and report what will change.
- Rollback exists (`nixos-rebuild switch --rollback`, previous generations in the boot menu), but only run it when the user asks.
- Never put secrets in a flake or commit them to git; point to sops-nix/agenix instead.

## Gotchas

- Flakes only see git-tracked files: an untracked `foo.nix` is invisible to `nix build .#...` until `git add` (intentional or not).
- `nixpkgs#...` resolves via the flake registry, not your `<nixpkgs>` channel; use `nixpkgs/<rev>#...` or a locked flake input for reproducibility.
- Pure evaluation forbids reading env vars or files outside the flake; use `--impure` deliberately, not by habit.
- `nix eval` on a big attrset can be slow; evaluate the leaf you need (`--raw ... .name`), not the whole set.
