"""Run the Rust blossom-cli binary through uvx."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


RUST_PACKAGE = "blossom-cli"
RUST_VERSION = "0.5.6"
RUST_REPOSITORY = "https://github.com/MonumentalSystems/blossom-rs"


class WrapperError(RuntimeError):
    """Raised when the Rust CLI cannot be resolved or installed."""


def cache_root() -> Path:
    configured = os.environ.get("BLOSSOM_CLI_CACHE_DIR")
    if configured:
        return Path(configured).expanduser()

    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache).expanduser() if xdg_cache else Path.home() / ".cache"
    return base / "blossom-cli" / RUST_VERSION


def configured_binary() -> Path | None:
    configured = os.environ.get("BLOSSOM_RUST_CLI_BIN")
    if not configured:
        return None

    path = Path(configured).expanduser()
    if not path.is_file() or not os.access(path, os.X_OK):
        raise WrapperError(f"BLOSSOM_RUST_CLI_BIN is not an executable file: {path}")
    return path


def cached_binary() -> Path:
    return cache_root() / "bin" / "blossom-cli"


def install_binary() -> Path:
    if os.environ.get("BLOSSOM_CLI_NO_INSTALL"):
        raise WrapperError(
            "blossom-cli was not found and automatic installation is disabled. "
            "Install blossom-cli 0.5.6 or set BLOSSOM_RUST_CLI_BIN."
        )

    cargo = shutil.which("cargo")
    if cargo is None:
        raise WrapperError(
            "blossom-cli was not found and Cargo is unavailable. "
            "Install Rust/Cargo or set BLOSSOM_RUST_CLI_BIN."
        )

    destination = cache_root()
    destination.mkdir(parents=True, exist_ok=True)
    command = [
        cargo,
        "install",
        RUST_PACKAGE,
        "--version",
        RUST_VERSION,
        "--locked",
        "--root",
        str(destination),
    ]
    print(
        f"Installing {RUST_PACKAGE} {RUST_VERSION} via Cargo (source: {RUST_REPOSITORY})...",
        file=sys.stderr,
    )
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise WrapperError(f"Cargo could not install {RUST_PACKAGE} {RUST_VERSION}")

    binary = cached_binary()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise WrapperError(f"Cargo reported success but did not create {binary}")
    return binary


def resolve_binary() -> Path:
    explicit = configured_binary()
    if explicit:
        return explicit

    on_path = shutil.which(RUST_PACKAGE)
    if on_path:
        return Path(on_path)

    cached = cached_binary()
    if cached.is_file() and os.access(cached, os.X_OK):
        return cached

    return install_binary()


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        binary = resolve_binary()
    except WrapperError as exc:
        print(f"blossom uvx wrapper: {exc}", file=sys.stderr)
        return 127

    command = [str(binary), *args]
    if os.name == "nt":
        return subprocess.call(command)

    os.execv(command[0], command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
