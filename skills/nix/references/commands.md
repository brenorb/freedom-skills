# Nix command cheat sheet

Task-first reference for the `nix` skill. All `nix ...` commands need the
`nix-command` and `flakes` experimental features; on a fresh install add
`--extra-experimental-features 'nix-command flakes'` or set them in
`/etc/nix/nix.conf` / `~/.config/nix/nix.conf`.

## Run without installing

| Task | Command |
|---|---|
| Run a tool once | `nix shell nixpkgs#<pkg> -c <cmd> [args...]` |
| Run a flake app | `nix run nixpkgs#<pkg>` |
| Run from a specific revision | `nix run nixpkgs/<rev>#<pkg>` |

## Search and inspect

| Task | Command |
|---|---|
| Search packages | `nix search nixpkgs <term>` |
| Search all outputs | `nix search nixpkgs <term> --json` |
| Show package metadata | `nix eval nixpkgs#<pkg>.meta --json` |
| Show why a path is in the store | `nix-store --query --referrers /nix/store/...` |
| Tree of dependencies | `nix-store --query --tree <drv-or-path>` |

## Flakes

| Task | Command |
|---|---|
| List flake outputs | `nix flake show` |
| Show locked inputs | `nix flake metadata` |
| Update lockfile inputs | `nix flake update` (or `nix flake lock --update-input <name>`) |
| Build an output | `nix build .#<output>` / `nix build .#packages.<system>.<name>` |
| Enter dev shell | `nix develop` (add `--command <cmd>` for non-interactive) |
| Run checks | `nix flake check` |
| Evaluate an expression | `nix eval --raw .#<attr>` / `nix eval --json --expr '<expr>'` |
| Interactive REPL | `nix repl` |

## Builds and debugging

| Task | Command |
|---|---|
| Full error trace | `nix build --show-trace` |
| Build logs | `nix build -L` (or `nix log /nix/store/...`) |
| Rebuild a derivation | `nix build --rebuild` |
| Dry run | `nix build --dry-run` |
| Evaluate without building | `nix eval .#<drv>.outPath` |

## System and user management (approval-gated, see SKILL.md safety rules)

| Task | Command |
|---|---|
| Build NixOS config | `nixos-rebuild build --flake .#<host>` |
| Test without booting | `nixos-rebuild test --flake .#<host>` |
| Switch (needs approval) | `nixos-rebuild switch --flake .#<host>` |
| macOS equivalent | `darwin-rebuild build|switch --flake .#<host>` |
| Home Manager build | `home-manager build --flake .#<user>@<host>` |
| Home Manager switch (needs approval) | `home-manager switch --flake .#<user>@<host>` |
| List generations | `nixos-rebuild list-generations` |
| Rollback (only if asked) | `nixos-rebuild switch --rollback` |

## Store maintenance

| Task | Command |
|---|---|
| Delete unreachable paths | `nix-collect-garbage` |
| Delete old generations + garbage (needs approval) | `nix-collect-garbage -d` |
| Optimize store | `nix-store --optimize` |
| Verify store integrity | `nix-store --verify` |

## Legacy (only when a project still uses channels)

| Task | Command |
|---|---|
| Evaluate with `<nixpkgs>` | `nix-instantiate --eval -E '<expr>'` |
| Build a nix file | `nix-build '<nixpkgs>' -A <pkg>` |
| Update channel | `nix-channel --update` (prefer flakes instead) |
