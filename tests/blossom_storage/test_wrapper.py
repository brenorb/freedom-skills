from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "blossom-storage"
    / "uvx"
    / "src"
    / "blossom_uvx"
    / "__init__.py"
)
SPEC = importlib.util.spec_from_file_location("blossom_uvx", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
blossom_uvx = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = blossom_uvx
SPEC.loader.exec_module(blossom_uvx)


def test_cache_root_honors_explicit_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    monkeypatch.setenv("BLOSSOM_CLI_CACHE_DIR", str(cache))

    assert blossom_uvx.cache_root() == cache


def test_configured_binary_requires_executable_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    monkeypatch.setenv("BLOSSOM_RUST_CLI_BIN", str(missing))

    with pytest.raises(blossom_uvx.WrapperError, match="not an executable file"):
        blossom_uvx.configured_binary()


def test_resolve_binary_prefers_explicit_binary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    binary = tmp_path / "blossom-cli"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o700)
    monkeypatch.setenv("BLOSSOM_RUST_CLI_BIN", str(binary))
    monkeypatch.setattr(blossom_uvx.shutil, "which", lambda _: "/wrong/path")

    assert blossom_uvx.resolve_binary() == binary


def test_install_is_blocked_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLOSSOM_CLI_NO_INSTALL", "1")

    with pytest.raises(blossom_uvx.WrapperError, match="automatic installation is disabled"):
        blossom_uvx.install_binary()
