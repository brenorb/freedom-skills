#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pytest"]
# ///

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "skills"
    / "p2p-transfer-filepizza"
    / "scripts"
    / "filepizza_tmux_runner.py"
)
SPEC = importlib.util.spec_from_file_location("filepizza_tmux_runner", MODULE_PATH)
filepizza_tmux_runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = filepizza_tmux_runner
SPEC.loader.exec_module(filepizza_tmux_runner)


def test_run_seed_worker_runs_node_in_runtime_and_redirects_logs(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    log_path = tmp_path / "worker.log"
    seed_script = tmp_path / "filepizza_seed.js"
    file_path = tmp_path / "example.txt"
    state_path = tmp_path / "upload.state.json"

    calls: list[tuple[list[str], str, bool, bool]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert kwargs["stdout"] is not None
        kwargs["stdout"].write("seed ok\n")
        calls.append(
            (
                cmd,
                str(kwargs["cwd"]),
                kwargs["stderr"] == subprocess.STDOUT,
                bool(kwargs["text"]),
            )
        )
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(filepizza_tmux_runner.subprocess, "run", fake_run)

    exit_code = filepizza_tmux_runner.run_seed_worker(
        runtime_dir=runtime_dir,
        log_path=log_path,
        seed_script=seed_script,
        file_path=file_path,
        state_path=state_path,
        upload_id="upload-123",
    )

    assert exit_code == 0
    assert log_path.read_text() == "seed ok\n"
    assert calls == [
        (
            ["node", str(seed_script), str(file_path), str(state_path), "upload-123"],
            str(runtime_dir),
            True,
            True,
        )
    ]


def test_main_logs_launcher_errors_and_returns_one(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log_path = tmp_path / "worker.log"
    monkeypatch.setattr(
        filepizza_tmux_runner,
        "run_seed_worker",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    exit_code = filepizza_tmux_runner.main(
        [
            str(tmp_path / "runtime"),
            str(log_path),
            str(tmp_path / "filepizza_seed.js"),
            str(tmp_path / "example.txt"),
            str(tmp_path / "upload.state.json"),
            "upload-123",
        ]
    )

    assert exit_code == 1
    assert "boom" in log_path.read_text()
