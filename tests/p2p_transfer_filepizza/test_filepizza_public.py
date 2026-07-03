#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pytest"]
# ///

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "skills"
    / "p2p-transfer-filepizza"
    / "scripts"
    / "filepizza_public.py"
)
SPEC = importlib.util.spec_from_file_location("filepizza_public", MODULE_PATH)
filepizza_public = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = filepizza_public
SPEC.loader.exec_module(filepizza_public)


def test_build_parser_accepts_all_supported_commands() -> None:
    parser = filepizza_public.build_parser()

    upload_args = parser.parse_args(["upload", "/tmp/example.txt"])
    status_args = parser.parse_args(["status", "abc123"])
    stop_args = parser.parse_args(["stop", "abc123"])
    list_args = parser.parse_args(["list"])

    assert upload_args.command == "upload"
    assert upload_args.file == "/tmp/example.txt"
    assert status_args.command == "status"
    assert status_args.upload_id == "abc123"
    assert stop_args.command == "stop"
    assert stop_args.upload_id == "abc123"
    assert list_args.command == "list"


def test_require_binary_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(filepizza_public.shutil, "which", lambda name: None)

    with pytest.raises(RuntimeError, match="Required binary not found in PATH: node"):
        filepizza_public.require_binary("node")


def test_ensure_runtime_requires_node_and_npm(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []
    monkeypatch.setattr(filepizza_public, "require_binary", lambda name: seen.append(name))

    filepizza_public.ensure_runtime()

    assert seen == ["node", "npm"]


def test_normalize_manifest_converts_camel_case_keys() -> None:
    normalized = filepizza_public.normalize_manifest(
        {
            "uploadId": "abc123",
            "filePath": "/tmp/example.txt",
            "shortUrl": "https://file.pizza/download/short",
            "nestedValue": {"peerId": "peer-1"},
        }
    )

    assert normalized == {
        "upload_id": "abc123",
        "id": "abc123",
        "file_path": "/tmp/example.txt",
        "file": "/tmp/example.txt",
        "short_url": "https://file.pizza/download/short",
        "nested_value": {"peer_id": "peer-1"},
    }


def test_materialize_manifest_status_marks_dead_seeders_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: False)

    merged = filepizza_public.materialize_manifest_status({"pid": 77, "status": "seeding"})

    assert merged["alive"] is False
    assert merged["status"] == "stopped"


def test_run_filepizza_cli_invokes_npx_and_parses_json(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout='{"uploadId":"abc123","shortUrl":"https://file.pizza/download/short"}\n', stderr="")

    monkeypatch.setattr(filepizza_public, "ensure_runtime", lambda: None)
    monkeypatch.setattr(filepizza_public.subprocess, "run", fake_run)

    payload = filepizza_public.run_filepizza_cli(["status", "abc123"])

    assert payload["uploadId"] == "abc123"
    assert calls == [["npx", "--yes", filepizza_public.PACKAGE_SPEC, "status", "abc123"]]


def test_run_filepizza_cli_raises_with_stderr_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="boom")

    monkeypatch.setattr(filepizza_public, "ensure_runtime", lambda: None)
    monkeypatch.setattr(filepizza_public.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="boom"):
        filepizza_public.run_filepizza_cli(["status", "abc123"])


def test_start_upload_rejects_missing_file(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RuntimeError, match="Local file not found:"):
        filepizza_public.start_upload(tmp_path / "missing.txt")


def test_start_upload_delegates_to_filepizza_cli(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local_file = tmp_path / "example.txt"
    local_file.write_text("hello\n")

    monkeypatch.setattr(
        filepizza_public,
        "run_filepizza_cli",
        lambda args: {
            "ok": True,
            "uploadId": "abc123",
            "filePath": str(local_file.resolve()),
            "shortUrl": "https://file.pizza/download/short",
        },
    )

    result = filepizza_public.start_upload(local_file)

    assert result["upload_id"] == "abc123"
    assert result["file"] == str(local_file.resolve())
    assert result["short_url"] == "https://file.pizza/download/short"


def test_load_manifest_raises_for_unknown_upload(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", tmp_path)

    with pytest.raises(RuntimeError, match="Unknown upload_id: missing"):
        filepizza_public.load_manifest("missing")


def test_list_uploads_reads_filepizza_cli_manifests(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", tmp_path)

    newest_manifest = tmp_path / "20260703-190000-bbbbbbbb.json"
    oldest_manifest = tmp_path / "20260703-180000-aaaaaaaa.json"
    newest_manifest.write_text(
        json.dumps(
            {
                "uploadId": "new",
                "filePath": "/tmp/new.txt",
                "pid": 123,
                "status": "seeding",
                "shortUrl": "https://file.pizza/download/new",
            }
        )
        + "\n"
    )
    oldest_manifest.write_text(
        json.dumps(
            {
                "uploadId": "old",
                "filePath": "/tmp/old.txt",
                "pid": 456,
                "status": "stopped",
                "shortUrl": "https://file.pizza/download/old",
            }
        )
        + "\n"
    )

    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: pid == 123)

    uploads = filepizza_public.list_uploads()

    assert [upload["upload_id"] for upload in uploads] == ["new", "old"]
    assert uploads[0]["short_url"] == "https://file.pizza/download/new"
    assert uploads[0]["alive"] is True
    assert uploads[1]["status"] == "stopped"


def test_status_and_stop_delegate_to_filepizza_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        filepizza_public,
        "run_filepizza_cli",
        lambda args: {"ok": True, "uploadId": args[-1], "status": args[0]},
    )

    status_result = filepizza_public.status_upload("abc123")
    stop_result = filepizza_public.stop_upload("abc123")

    assert status_result == {"ok": True, "upload_id": "abc123", "id": "abc123", "status": "status"}
    assert stop_result == {"ok": True, "upload_id": "abc123", "id": "abc123", "status": "stop"}


def test_main_list_command_prints_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["filepizza_public.py", "list"])
    monkeypatch.setattr(filepizza_public, "list_uploads", lambda: [{"upload_id": "abc123"}])

    exit_code = filepizza_public.main()
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert json.loads(stdout) == {"ok": True, "uploads": [{"upload_id": "abc123"}]}


def test_main_dispatches_status_and_stop_commands(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["filepizza_public.py", "status", "abc123"])
    monkeypatch.setattr(filepizza_public, "status_upload", lambda upload_id: {"ok": True, "upload_id": upload_id})

    exit_code = filepizza_public.main()
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert json.loads(stdout) == {"ok": True, "upload_id": "abc123"}

    monkeypatch.setattr(sys, "argv", ["filepizza_public.py", "stop", "abc123"])
    monkeypatch.setattr(filepizza_public, "stop_upload", lambda upload_id: {"ok": True, "stopped": upload_id})

    exit_code = filepizza_public.main()
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert json.loads(stdout) == {"ok": True, "stopped": "abc123"}


def test_main_dispatches_upload_command(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    local_file = tmp_path / "example.txt"
    local_file.write_text("hello\n")
    monkeypatch.setattr(sys, "argv", ["filepizza_public.py", "upload", str(local_file)])
    monkeypatch.setattr(
        filepizza_public,
        "start_upload",
        lambda file_path: {"ok": True, "file": str(file_path), "upload_id": "abc123"},
    )

    exit_code = filepizza_public.main()
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert json.loads(stdout) == {"ok": True, "file": str(local_file), "upload_id": "abc123"}
