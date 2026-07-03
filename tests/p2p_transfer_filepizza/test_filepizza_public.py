#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pytest"]
# ///

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import time

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


def test_create_upload_id_has_expected_shape() -> None:
    upload_id = filepizza_public.create_upload_id()
    assert len(upload_id) == 24
    assert upload_id[8] == "-"
    assert upload_id[15] == "-"


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


def test_get_upload_paths_uses_expected_suffixes() -> None:
    paths = filepizza_public.get_upload_paths("abc123")
    assert paths.manifest_path.name == "abc123.json"
    assert paths.state_path.name == "abc123.state.json"
    assert paths.log_path.name == "abc123.log"


def test_tmux_session_name_is_stable() -> None:
    assert filepizza_public.tmux_session_name("abc123") == "p2p_transfer_filepizza_abc123"


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
        "tmux_session": "p2p_transfer_filepizza_abc",
    }
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: False)
    monkeypatch.setattr(
        filepizza_public, "is_tmux_session_alive", lambda session_name: session_name == "p2p_transfer_filepizza_abc"
    )

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


def test_ensure_directories_creates_runtime_and_upload_dirs(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_dir = tmp_path / "runtime"
    uploads_dir = tmp_path / "uploads"
    monkeypatch.setattr(filepizza_public, "RUNTIME_DIR", runtime_dir)
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", uploads_dir)

    filepizza_public.ensure_directories()

    assert runtime_dir.is_dir()
    assert uploads_dir.is_dir()


def test_require_binary_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(filepizza_public.shutil, "which", lambda name: None)

    with pytest.raises(RuntimeError, match="Required binary not found in PATH: node"):
        filepizza_public.require_binary("node")


def test_ensure_runtime_bootstraps_missing_assets(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    monkeypatch.setattr(filepizza_public, "RUNTIME_DIR", runtime_dir)

    calls: list[tuple[list[str], pathlib.Path | None]] = []

    def fake_run(cmd: list[str], *, cwd: pathlib.Path | None = None) -> None:
        calls.append((cmd, cwd))
        if cmd[:2] == ["npm", "init"]:
            (runtime_dir / "package.json").write_text("{}\n")
        elif cmd[:2] == ["npm", "install"]:
            (runtime_dir / "node_modules" / "playwright").mkdir(parents=True)
        elif cmd[:3] == ["npx", "playwright", "install"]:
            (runtime_dir / ".chromium-installed").write_text("ok\n")

    monkeypatch.setattr(filepizza_public, "require_binary", lambda name: None)
    monkeypatch.setattr(filepizza_public, "run", fake_run)

    filepizza_public.ensure_runtime()

    assert calls == [
        (["npm", "init", "-y"], runtime_dir),
        (["npm", "install", "playwright"], runtime_dir),
        (["npx", "playwright", "install", "chromium"], runtime_dir),
    ]
    assert (runtime_dir / "package.json").exists()
    assert (runtime_dir / "node_modules" / "playwright").exists()
    assert (runtime_dir / ".chromium-installed").read_text() == "ok\n"


def test_wait_for_share_links_returns_when_both_links_exist(tmp_path: pathlib.Path) -> None:
    state_path = tmp_path / "upload.state.json"
    log_path = tmp_path / "upload.log"
    log_path.write_text("")
    state_path.write_text(
        json.dumps(
            {
                "short_url": "https://file.pizza/download/short",
                "long_url": "https://file.pizza/download/long/path",
                "status": "seeding",
            }
        )
        + "\n"
    )

    result = filepizza_public.wait_for_share_links(
        filepizza_public.UploadPaths("abc", tmp_path / "upload.json", state_path, log_path),
        timeout_s=1,
    )

    assert result["short_url"] == "https://file.pizza/download/short"
    assert result["long_url"] == "https://file.pizza/download/long/path"


def test_wait_for_share_links_timeout_includes_tailed_logs(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log_path = tmp_path / "upload.log"
    log_path.write_text("line1\nline2\nline3\n")
    paths = filepizza_public.UploadPaths("abc", tmp_path / "upload.json", tmp_path / "upload.state.json", log_path)

    timeline = iter([0.0, 0.4, 0.8, 1.2])
    monkeypatch.setattr(filepizza_public.time, "time", lambda: next(timeline))
    monkeypatch.setattr(filepizza_public.time, "sleep", lambda seconds: None)

    with pytest.raises(RuntimeError, match="Timed out waiting for FilePizza share links") as excinfo:
        filepizza_public.wait_for_share_links(paths, timeout_s=1)

    assert "line2" in str(excinfo.value)
    assert "line3" in str(excinfo.value)


def test_start_upload_rejects_missing_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(filepizza_public, "ensure_directories", lambda: None)
    monkeypatch.setattr(filepizza_public, "ensure_runtime", lambda: None)

    with pytest.raises(RuntimeError, match="Local file not found:"):
        filepizza_public.start_upload(tmp_path / "missing.txt")


def test_start_upload_uses_tmux_when_available(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_dir = tmp_path / "runtime"
    uploads_dir = tmp_path / "uploads"
    runtime_dir.mkdir()
    uploads_dir.mkdir()
    local_file = tmp_path / "example.txt"
    local_file.write_text("hello\n")

    monkeypatch.setattr(filepizza_public, "RUNTIME_DIR", runtime_dir)
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(filepizza_public, "SEED_SCRIPT", pathlib.Path("/seed/filepizza_seed.js"))
    monkeypatch.setattr(filepizza_public, "TMUX_RUNNER", pathlib.Path("/seed/filepizza_tmux_runner.py"))
    monkeypatch.setattr(filepizza_public, "ensure_directories", lambda: None)
    monkeypatch.setattr(filepizza_public, "ensure_runtime", lambda: None)
    monkeypatch.setattr(filepizza_public, "create_upload_id", lambda now=None: "20260703-180000-deadbeef")
    monkeypatch.setattr(filepizza_public, "utc_now", lambda: "2026-07-03T18:00:00Z")
    monkeypatch.setattr(filepizza_public, "tmux_available", lambda: True)

    tmux_calls: list[list[str]] = []
    prelaunch_manifest: dict[str, object] = {}

    def fake_subprocess_run(cmd: list[str], **kwargs: object) -> None:
        prelaunch_manifest.update(json.loads((uploads_dir / "20260703-180000-deadbeef.json").read_text()))
        tmux_calls.append(cmd)

    monkeypatch.setattr(filepizza_public.subprocess, "run", fake_subprocess_run)
    monkeypatch.setattr(
        filepizza_public,
        "wait_for_share_links",
        lambda paths: {
            "ok": True,
            "pid": 43210,
            "short_url": "https://file.pizza/download/short",
            "long_url": "https://file.pizza/download/very/long/path",
            "status": "seeding",
            "started_at": "2026-07-03T18:00:01Z",
        },
    )
    monkeypatch.setattr(filepizza_public, "is_tmux_session_alive", lambda session_name: True)
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: False)

    result = filepizza_public.start_upload(local_file)

    manifest_path = uploads_dir / "20260703-180000-deadbeef.json"
    manifest = json.loads(manifest_path.read_text())
    assert result["launcher"] == "tmux"
    assert result["tmux_session"] == "p2p_transfer_filepizza_20260703-180000-deadbeef"
    assert result["short_url"] == "https://file.pizza/download/short"
    assert manifest["pid"] == 43210
    assert prelaunch_manifest["status"] == "starting"
    assert "launcher" not in prelaunch_manifest
    assert tmux_calls
    assert tmux_calls[0][:5] == ["tmux", "new-session", "-d", "-s", "p2p_transfer_filepizza_20260703-180000-deadbeef"]
    assert tmux_calls[0][5:] == [
        sys.executable,
        "/seed/filepizza_tmux_runner.py",
        str(runtime_dir),
        str(uploads_dir / "20260703-180000-deadbeef.log"),
        "/seed/filepizza_seed.js",
        str(local_file.resolve()),
        str(uploads_dir / "20260703-180000-deadbeef.state.json"),
        "20260703-180000-deadbeef",
    ]


def test_start_upload_falls_back_to_subprocess_when_tmux_missing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_dir = tmp_path / "runtime"
    uploads_dir = tmp_path / "uploads"
    runtime_dir.mkdir()
    uploads_dir.mkdir()
    local_file = tmp_path / "example.txt"
    local_file.write_text("hello\n")

    monkeypatch.setattr(filepizza_public, "RUNTIME_DIR", runtime_dir)
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(filepizza_public, "SEED_SCRIPT", pathlib.Path("/seed/filepizza_seed.js"))
    monkeypatch.setattr(filepizza_public, "ensure_directories", lambda: None)
    monkeypatch.setattr(filepizza_public, "ensure_runtime", lambda: None)
    monkeypatch.setattr(filepizza_public, "create_upload_id", lambda now=None: "20260703-180500-feedface")
    monkeypatch.setattr(filepizza_public, "utc_now", lambda: "2026-07-03T18:05:00Z")
    monkeypatch.setattr(filepizza_public, "tmux_available", lambda: False)

    popen_calls: list[tuple[list[str], str]] = []
    prelaunch_manifest: dict[str, object] = {}

    class FakeProcess:
        pid = 98765

    def fake_popen(cmd: list[str], **kwargs: object) -> FakeProcess:
        prelaunch_manifest.update(json.loads((uploads_dir / "20260703-180500-feedface.json").read_text()))
        popen_calls.append((cmd, str(kwargs["cwd"])))
        return FakeProcess()

    monkeypatch.setattr(filepizza_public.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        filepizza_public,
        "wait_for_share_links",
        lambda paths: {
            "ok": True,
            "pid": 98765,
            "short_url": "https://file.pizza/download/short",
            "long_url": "https://file.pizza/download/long/path",
            "status": "seeding",
            "started_at": "2026-07-03T18:05:01Z",
        },
    )
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: True)

    result = filepizza_public.start_upload(local_file)

    assert result["launcher"] == "subprocess"
    assert result["pid"] == 98765
    assert prelaunch_manifest["status"] == "starting"
    assert "launcher" not in prelaunch_manifest
    assert popen_calls == [
        (
            [
                "node",
                "/seed/filepizza_seed.js",
                str(local_file.resolve()),
                str(uploads_dir / "20260703-180500-feedface.state.json"),
                "20260703-180500-feedface",
            ],
            str(runtime_dir),
        )
    ]


def test_load_manifest_raises_for_unknown_upload(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", tmp_path)

    with pytest.raises(RuntimeError, match="Unknown upload_id: missing"):
        filepizza_public.load_manifest("missing")


def test_list_uploads_skips_state_files_and_merges_status(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", tmp_path)
    monkeypatch.setattr(filepizza_public, "ensure_directories", lambda: None)

    newest_manifest = tmp_path / "20260703-190000-bbbbbbbb.json"
    oldest_manifest = tmp_path / "20260703-180000-aaaaaaaa.json"
    newest_state = tmp_path / "20260703-190000-bbbbbbbb.state.json"
    oldest_state = tmp_path / "20260703-180000-aaaaaaaa.state.json"

    newest_state.write_text('{"status":"seeding","short_url":"https://file.pizza/download/new"}\n')
    oldest_state.write_text('{"status":"stopped","short_url":"https://file.pizza/download/old"}\n')
    newest_manifest.write_text(json.dumps({"upload_id": "new", "state_path": str(newest_state), "status": "starting"}) + "\n")
    oldest_manifest.write_text(json.dumps({"upload_id": "old", "state_path": str(oldest_state), "status": "starting"}) + "\n")

    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: False)
    monkeypatch.setattr(filepizza_public, "is_tmux_session_alive", lambda session_name: False)

    uploads = filepizza_public.list_uploads()

    assert [upload["upload_id"] for upload in uploads] == ["new", "old"]
    assert uploads[0]["short_url"] == "https://file.pizza/download/new"
    assert uploads[1]["status"] == "stopped"


def test_stop_upload_terminates_subprocess_and_persists_stopped_status(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", tmp_path)
    manifest_path = tmp_path / "abc123.json"
    state_path = tmp_path / "abc123.state.json"
    state_path.write_text('{"status":"seeding","pid":55}\n')
    manifest_path.write_text(
        json.dumps(
            {
                "upload_id": "abc123",
                "state_path": str(state_path),
                "pid": 55,
                "launcher": "subprocess",
                "status": "seeding",
            }
        )
        + "\n"
    )

    pid_checks = iter([True, False, False])
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: next(pid_checks))
    monkeypatch.setattr(filepizza_public.os, "kill", lambda pid, sig: killed.append((pid, sig)))
    monkeypatch.setattr(filepizza_public.time, "sleep", lambda seconds: None)

    result = filepizza_public.stop_upload("abc123")
    persisted = json.loads(manifest_path.read_text())

    assert killed == [(55, signal.SIGTERM)]
    assert result["status"] == "stopped"
    assert persisted["status"] == "stopped"
    assert persisted["alive"] is False


def test_stop_upload_kills_tmux_session_and_persists_stopped_status(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(filepizza_public, "UPLOADS_DIR", tmp_path)
    manifest_path = tmp_path / "abc123.json"
    state_path = tmp_path / "abc123.state.json"
    state_path.write_text('{"status":"seeding","pid":99}\n')
    manifest_path.write_text(
        json.dumps(
            {
                "upload_id": "abc123",
                "state_path": str(state_path),
                "pid": 99,
                "launcher": "tmux",
                "tmux_session": "p2p_transfer_filepizza_abc123",
                "status": "seeding",
            }
        )
        + "\n"
    )

    tmux_checks = iter([True, False, False])
    pid_checks = iter([True, False, False])
    tmux_runs: list[list[str]] = []
    killed: list[tuple[int, int]] = []

    monkeypatch.setattr(filepizza_public, "is_tmux_session_alive", lambda session_name: next(tmux_checks))
    monkeypatch.setattr(filepizza_public, "is_pid_alive", lambda pid: next(pid_checks))
    monkeypatch.setattr(filepizza_public.subprocess, "run", lambda cmd, **kwargs: tmux_runs.append(cmd))
    monkeypatch.setattr(filepizza_public.os, "kill", lambda pid, sig: killed.append((pid, sig)))
    monkeypatch.setattr(filepizza_public.time, "sleep", lambda seconds: None)

    result = filepizza_public.stop_upload("abc123")
    persisted = json.loads(manifest_path.read_text())

    assert tmux_runs == [["tmux", "kill-session", "-t", "p2p_transfer_filepizza_abc123"]]
    assert killed == [(99, signal.SIGTERM)]
    assert result["status"] == "stopped"
    assert persisted["status"] == "stopped"


def test_main_list_command_prints_json(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
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


def test_module_guard_prints_error_and_exits_two(tmp_path: pathlib.Path) -> None:
    result = filepizza_public.subprocess.run(
        [sys.executable, str(MODULE_PATH), "status", "missing"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "Unknown upload_id: missing" in result.stderr


def make_fake_playwright_runtime(
    tmp_path: pathlib.Path,
    *,
    links: list[str] | None = None,
    launch_error: str | None = None,
    click_error: str | None = None,
) -> pathlib.Path:
    runtime_dir = tmp_path / "runtime"
    playwright_dir = runtime_dir / "node_modules" / "playwright"
    playwright_dir.mkdir(parents=True)
    (runtime_dir / "package.json").write_text('{"name":"filepizza-test-runtime"}\n')
    action_log = tmp_path / "actions.log"
    encoded_links = json.dumps(links or [])
    encoded_launch_error = json.dumps(launch_error)
    encoded_click_error = json.dumps(click_error)
    (playwright_dir / "index.js").write_text(
        f"""
const fs = require("fs");

const links = {encoded_links};
const launchError = {encoded_launch_error};
const clickError = {encoded_click_error};
const actionLog = process.env.PLAYWRIGHT_ACTION_LOG;

function log(event, payload) {{
  if (!actionLog) return;
  fs.appendFileSync(actionLog, JSON.stringify({{ event, payload }}) + "\\n");
}}

exports.chromium = {{
  launch: async (options) => {{
    log("launch", options);
    if (launchError) throw new Error(launchError);
    return {{
      newPage: async () => {{
        log("newPage", null);
        return {{
          goto: async (url, options) => log("goto", {{ url, options }}),
          setInputFiles: async (selector, filePath) => log("setInputFiles", {{ selector, filePath }}),
          locator: (selector) => {{
            log("locator", {{ selector }});
            return {{
              click: async () => {{
                log("locatorClick", {{ selector }});
                if (clickError) throw new Error(clickError);
              }},
            }};
          }},
          getByRole: (role, options) => {{
            log("getByRole", {{ role, options }});
            return {{
              click: async () => {{
                log("click", null);
                if (clickError) throw new Error(clickError);
              }},
            }};
          }},
          evaluate: async () => links,
        }};
      }},
      close: async () => log("close", null),
    }};
  }},
}};
""".strip()
        + "\n"
    )
    return runtime_dir


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for filepizza seeder tests")
def test_filepizza_seed_requires_arguments(tmp_path: pathlib.Path) -> None:
    runtime_dir = make_fake_playwright_runtime(tmp_path)

    result = subprocess.run(
        ["node", str(filepizza_public.SEED_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(runtime_dir),
    )

    assert result.returncode == 1
    assert "Usage: node filepizza_seed.js <file-path> <state-path> <upload-id>" in result.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for filepizza seeder tests")
def test_filepizza_seed_writes_state_tracks_actions_and_exits_cleanly_on_sigterm(tmp_path: pathlib.Path) -> None:
    runtime_dir = make_fake_playwright_runtime(
        tmp_path,
        links=[
            "https://file.pizza/download/abcd1234",
            "https://file.pizza/download/pepperoni/mushroom/olive/basil",
        ],
    )
    local_file = tmp_path / "example.txt"
    local_file.write_text("hello\n")
    state_path = tmp_path / "upload.state.json"
    action_log = tmp_path / "actions.log"

    process = subprocess.Popen(
        ["node", str(filepizza_public.SEED_SCRIPT), str(local_file), str(state_path), "upload-123"],
        cwd=str(runtime_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PLAYWRIGHT_ACTION_LOG": str(action_log)},
    )
    try:
        deadline = time.time() + 5
        while time.time() < deadline and not state_path.exists():
            time.sleep(0.05)
        assert state_path.exists(), "expected state file to be written"

        state = json.loads(state_path.read_text())
        actions = [json.loads(line) for line in action_log.read_text().splitlines()]

        assert state["ok"] is True
        assert state["upload_id"] == "upload-123"
        assert state["file"] == str(local_file.resolve())
        assert state["short_url"] == "https://file.pizza/download/abcd1234"
        assert state["long_url"] == "https://file.pizza/download/pepperoni/mushroom/olive/basil"
        assert state["status"] == "seeding"
        assert process.poll() is None

        assert actions[0]["event"] == "launch"
        assert actions[0]["payload"] == {"headless": True}
        assert any(
            entry["event"] == "goto"
            and entry["payload"]["url"] == "https://file.pizza/"
            and entry["payload"]["options"] == {"waitUntil": "domcontentloaded"}
            for entry in actions
        )
        assert any(
            entry["event"] == "setInputFiles"
            and entry["payload"]["selector"] == 'input[type="file"]'
            and entry["payload"]["filePath"] == str(local_file.resolve())
            for entry in actions
        )
        assert any(
            entry["event"] == "locator"
            and entry["payload"] == {"selector": "#start-button"}
            for entry in actions
        )
        assert any(
            entry["event"] == "locatorClick"
            and entry["payload"] == {"selector": "#start-button"}
            for entry in actions
        )

        process.send_signal(signal.SIGTERM)
        return_code = process.wait(timeout=5)
        assert return_code == 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for filepizza seeder tests")
def test_filepizza_seed_logs_errors_and_exits_nonzero(tmp_path: pathlib.Path) -> None:
    runtime_dir = make_fake_playwright_runtime(tmp_path, click_error="simulated click failure")
    local_file = tmp_path / "example.txt"
    local_file.write_text("hello\n")
    state_path = tmp_path / "upload.state.json"

    result = subprocess.run(
        ["node", str(filepizza_public.SEED_SCRIPT), str(local_file), str(state_path), "upload-456"],
        capture_output=True,
        text=True,
        cwd=str(runtime_dir),
    )

    assert result.returncode == 1
    assert "simulated click failure" in result.stderr
    assert not state_path.exists()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
