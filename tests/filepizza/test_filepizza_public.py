#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pytest"]
# ///

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "skills"
    / "filepizza"
    / "scripts"
    / "filepizza_public.py"
)
SPEC = importlib.util.spec_from_file_location("filepizza_public", MODULE_PATH)
filepizza_public = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = filepizza_public
SPEC.loader.exec_module(filepizza_public)


def test_create_upload_id_has_expected_shape() -> None:
    upload_id = filepizza_public.create_upload_id()
    assert len(upload_id) == 24
    assert upload_id[8] == "-"
    assert upload_id[15] == "-"


def test_get_upload_paths_uses_expected_suffixes() -> None:
    paths = filepizza_public.get_upload_paths("abc123")
    assert paths.manifest_path.name == "abc123.json"
    assert paths.state_path.name == "abc123.state.json"
    assert paths.log_path.name == "abc123.log"


def test_tmux_session_name_is_stable() -> None:
    assert filepizza_public.tmux_session_name("abc123") == "filepizza_abc123"


def test_merge_upload_state_reads_worker_state(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state_path = tmp_path / "abc.state.json"
    state_path.write_text(
        '{"short_url":"https://file.pizza/download/short","long_url":"https://file.pizza/download/long","status":"seeding","pid":55}\n'
    )
    manifest = {"upload_id": "abc", "state_path": str(state_path), "pid": 55, "status": "starting"}
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: True)

    merged = filepizza_public.merge_upload_state(manifest)

    assert merged["short_url"] == "https://file.pizza/download/short"
    assert merged["status"] == "seeding"
    assert merged["alive"] is True


def test_merge_upload_state_uses_tmux_session_when_launcher_is_tmux(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state_path = tmp_path / "abc.state.json"
    state_path.write_text('{"status":"seeding"}\n')
    manifest = {
        "upload_id": "abc",
        "state_path": str(state_path),
        "status": "starting",
        "launcher": "tmux",
        "tmux_session": "filepizza_abc",
    }
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: False)
    monkeypatch.setattr(filepizza_public, "is_tmux_session_alive", lambda session_name: session_name == "filepizza_abc")

    merged = filepizza_public.merge_upload_state(manifest)

    assert merged["alive"] is True
    assert merged["status"] == "seeding"


def test_merge_upload_state_marks_dead_seeders_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: False)
    monkeypatch.setattr(filepizza_public, "is_tmux_session_alive", lambda session_name: False)

    merged = filepizza_public.merge_upload_state({"upload_id": "abc", "state_path": "/tmp/missing", "pid": 77, "status": "seeding"})

    assert merged["alive"] is False
    assert merged["status"] == "stopped"


def test_tail_text_returns_last_lines(tmp_path: pathlib.Path) -> None:
    log_path = tmp_path / "uploader.log"
    log_path.write_text("a\nb\nc\nd\n")
    assert filepizza_public.tail_text(log_path, limit=2) == ["c", "d"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
