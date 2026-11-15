# Flakes and devShells

Patterns for the `nix` skill. Prefer flakes over channels for anything new.

## Minimal flake skeleton

```nix
{
  description = "My project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    # pin everything else here too, e.g.:
    # home-manager.url = "github:nix-community/home-manager";
  };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.default = pkgs.hello;
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [ git jq curl ];
      };
    };
}
```

For multiple systems, factor the outputs:

```nix
outputs = { self, nixpkgs, ... }:
  let
    forAllSystems = f: nixpkgs.lib.genAttrs [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ]
      (system: f (import nixpkgs { inherit system; }));
  in
  {
    packages = forAllSystems (pkgs: { default = pkgs.hello; });
    devShells = forAllSystems (pkgs: { default = pkgs.mkShell { packages = [ pkgs.git ]; }; });
  };
```

## devShell patterns

- Put build tools and CLIs the agent needs in `mkShell { packages = [...]; }`, not in a wrapper derivation.
- Use `shellHook` for env vars and one-time setup messages:

```nix
pkgs.mkShell {
  packages = [ pkgs.go ];
  shellHook = ''
    export GOPATH="$PWD/.go"
  '';
}
```

- Enter non-interactively from scripts: `nix develop --command bash -c '...'`

## Packaging a simple program

```nix
packages.${system}.default = pkgs.stdenv.mkDerivation {
  pname = "mytool";
  version = "0.1.0";
  src = ./.;
  installPhase = ''
    mkdir -p $out/bin
    cp mytool $out/bin/
  '';
};
```

Prefer `pkgs.buildPythonApplication`, `pkgs.buildGoModule`, etc. over hand-rolled derivations when one exists.

## Lockfile hygiene

- Commit `flake.lock`; it is what makes builds reproducible.
- Update deliberately: `nix flake update` (all inputs) or `nix flake lock --update-input nixpkgs` (one input), then rebuild and test.
- `nix flake metadata` shows the exact locked revisions.

## Gotchas

- **Untracked files are invisible.** Flake evaluation copies only git-tracked files into the store. If `nix build` claims a file does not exist, run `git add` first.
- **Pure evaluation.** Expressions cannot read environment variables, `/etc`, or the network at eval time. Pass data in via flake inputs or `--impure` (deliberately).
- **`nixpkgs#...` is the registry default**, usually nixpkgs-unstable. For reproducible work use a locked input (`inputs.nixpkgs`) or an explicit revision (`nixpkgs/<rev>#...`).
- Errors are often deep: rerun with `--show-trace`, and for build failures use `-L` to read the actual build log.
