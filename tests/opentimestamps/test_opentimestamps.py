from __future__ import annotations

import importlib.util
import json
import os
import signal
import subprocess
import textwrap
import time

import pytest
import sys
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "opentimestamps"
        / "scripts"
        / "opentimestamps.py"
    )
    spec = importlib.util.spec_from_file_location("opentimestamps_skill", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


opentimestamps = load_module()


def test_default_timestamp_path_appends_ots():
    path = Path("/tmp/archive.tar.gz")
    assert opentimestamps.default_timestamp_path(path) == Path("/tmp/archive.tar.gz.ots")


def test_infer_target_path_removes_ots_suffix():
    path = Path("/tmp/archive.tar.gz.ots")
    assert opentimestamps.infer_target_path(path) == Path("/tmp/archive.tar.gz")


def test_backup_timestamp_path_appends_bak():
    path = Path("/tmp/archive.tar.gz.ots")
    assert opentimestamps.backup_timestamp_path(path) == Path("/tmp/archive.tar.gz.ots.bak")


def test_parse_submitted_calendars_reads_all_matches():
    text = """
    Submitting to remote calendar https://a.pool.opentimestamps.org
    Submitting to remote calendar https://b.pool.opentimestamps.org
    """
    assert opentimestamps.parse_submitted_calendars(text) == [
        "https://a.pool.opentimestamps.org",
        "https://b.pool.opentimestamps.org",
    ]


def test_parse_pending_calendars_supports_verify_output():
    text = """
    Calendar https://alice.btc.calendar.opentimestamps.org: Pending confirmation in Bitcoin blockchain
    Calendar https://btc.calendar.catallaxy.com: Pending confirmation in Bitcoin blockchain
    """
    assert opentimestamps.parse_pending_calendars(text) == [
        "https://alice.btc.calendar.opentimestamps.org",
        "https://btc.calendar.catallaxy.com",
    ]


def test_parse_pending_calendars_supports_info_output():
    text = "verify PendingAttestation('https://bob.btc.calendar.opentimestamps.org')"
    assert opentimestamps.parse_pending_calendars(text) == [
        "https://bob.btc.calendar.opentimestamps.org"
    ]


def test_parse_verify_success_extracts_block_and_time():
    text = "Success! Bitcoin block 358391 attests data existed as of 2015-06-05 UTC"
    assert opentimestamps.parse_verify_success(text) == {
        "block_height": 358391,
        "attested_at": "2015-06-05 UTC",
    }


def test_parse_info_summary_extracts_digest_and_pending():
    text = """
    File sha256 hash: e66347a0e1fab2e35b031c12ed6916bd6b8584808ee4e09f82f23fb76d221575
    verify PendingAttestation('https://bob.btc.calendar.opentimestamps.org')
    """
    assert opentimestamps.parse_info_summary(text) == {
        "file_sha256": "e66347a0e1fab2e35b031c12ed6916bd6b8584808ee4e09f82f23fb76d221575",
        "pending_calendars": ["https://bob.btc.calendar.opentimestamps.org"],
    }


def test_resolve_ots_runner_prefers_system_binary(monkeypatch):
    monkeypatch.setattr(opentimestamps.shutil, "which", lambda name: "/usr/bin/ots" if name == "ots" else None)
    assert opentimestamps.resolve_ots_runner() == (["/usr/bin/ots"], "system")


def test_resolve_ots_runner_falls_back_to_uvx(monkeypatch):
    def fake_which(name: str):
        if name == "uvx":
            return "/usr/bin/uvx"
        return None

    monkeypatch.setattr(opentimestamps.shutil, "which", fake_which)
    assert opentimestamps.resolve_ots_runner() == (
        ["/usr/bin/uvx", "--from", "opentimestamps-client", "ots"],
        "uvx",
    )


@pytest.fixture
def fake_client(tmp_path, monkeypatch):
    client = tmp_path / "ots"
    client.write_text(
        f"#!{sys.executable}\n" + textwrap.dedent("""
        import json, os, pathlib, subprocess, sys, time
        args = sys.argv[1:]
        if "--help" in args:
            time.sleep(float(os.environ.get("OTS_HELP_DELAY", "0")))
            print("usage: ots " + args[0] + (" [--timeout TIMEOUT]" if os.environ.get("OTS_SUPPORT_TIMEOUT") == "1" else ""))
            sys.exit(0)
        log = os.environ.get("OTS_ARGUMENT_LOG")
        if log:
            pathlib.Path(log).write_text(json.dumps(args))
        if os.environ.get("OTS_CLIENT_PID"):
            pathlib.Path(os.environ["OTS_CLIENT_PID"]).write_text(str(os.getpid()))
        mode = os.environ.get("OTS_TEST_MODE", "success")
        if mode == "invalid":
            print("Invalid timestamp file", file=sys.stderr)
            sys.exit(2)
        if mode == "stall":
            print("Calendar https://test.invalid: Pending confirmation in Bitcoin blockchain", flush=True)
            time.sleep(30)
        if mode == "incomplete":
            while True:
                print("Got new incomplete attestation", flush=True)
                time.sleep(0.02)
        if mode == "descendant":
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            pathlib.Path(os.environ["OTS_CHILD_PID"]).write_text(str(child.pid))
            # Exit while the descendant holds stdout/stderr open.
            sys.exit(0)
        if "stamp" in args:
            pathlib.Path(args[-1] + ".ots").write_bytes(b"fixture proof")
            print("Submitting to remote calendar https://test.invalid")
        elif "info" in args:
            print("File sha256 hash: " + "a" * 64)
        else:
            print("Success! Bitcoin block 358391 attests data existed as of 2015-06-05 UTC")
        """)
    )
    client.chmod(0o755)
    original_which = opentimestamps.shutil.which
    monkeypatch.setattr(opentimestamps.shutil, "which", lambda name: str(client) if name == "ots" else original_which(name))
    return client


def test_success_paths_and_stamp_output_move(fake_client, tmp_path, capsys):
    original = tmp_path / "document"
    original.write_bytes(b"original")
    proof = tmp_path / "proofs" / "document.ots"
    assert opentimestamps.main(["stamp", "--input", str(original), "--timestamp", str(proof), "--timeout", "5"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["submitted_calendars"] == ["https://test.invalid"]
    assert proof.read_bytes() == b"fixture proof"
    assert not original.with_suffix(".ots").exists()
    assert opentimestamps.main(["info", "--timestamp", str(proof)]) == 0
    assert json.loads(capsys.readouterr().out)["summary"]["file_sha256"] == "a" * 64
    assert opentimestamps.main(["verify", "--timestamp", str(proof), "--input", str(original)]) == 0
    assert json.loads(capsys.readouterr().out)["verification"]["block_height"] == 358391
    assert original.read_bytes() == b"original"


@pytest.mark.parametrize("operation", ["upgrade", "verify"])
@pytest.mark.parametrize("supported", [False, True])
def test_calendar_timeout_is_forwarded_only_when_supported(
    fake_client, tmp_path, monkeypatch, capsys, operation, supported,
):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    log = tmp_path / "args.json"
    monkeypatch.setenv("OTS_ARGUMENT_LOG", str(log))
    monkeypatch.setenv("OTS_SUPPORT_TIMEOUT", "1" if supported else "0")
    assert opentimestamps.main([operation, "--timestamp", str(proof), "--timeout", "3"]) == 0
    result = json.loads(capsys.readouterr().out)
    args = json.loads(log.read_text())
    assert result["calendar_timeout_supported"] is supported
    assert ("--timeout" in args) is supported
    if supported:
        assert args[args.index("--timeout") + 1] == "3"


@pytest.mark.parametrize("mode", ["stall", "incomplete"])
def test_wait_is_bounded_and_timeout_is_not_a_bad_proof(
    fake_client, tmp_path, monkeypatch, capsys, mode,
):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    monkeypatch.setenv("OTS_TEST_MODE", mode)
    start = time.monotonic()
    assert opentimestamps.main(["--operation-timeout", "0.4", "--wait", "upgrade", "--timestamp", str(proof)]) == 124
    assert time.monotonic() - start < 3
    result = json.loads(capsys.readouterr().out)
    assert result["timed_out"] is True
    assert "--wait" in result["command"]
    assert result["stdout"]
    assert "verification" not in result
    assert proof.read_bytes() == b"fixture"


def test_help_probe_uses_the_same_total_deadline(fake_client, tmp_path, monkeypatch, capsys):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    monkeypatch.setenv("OTS_HELP_DELAY", "0.25")
    monkeypatch.setenv("OTS_TEST_MODE", "stall")
    start = time.monotonic()
    assert opentimestamps.main(["--operation-timeout", "0.4", "verify", "--timestamp", str(proof), "--timeout", "3"]) == 124
    assert time.monotonic() - start < 0.9
    assert json.loads(capsys.readouterr().out)["timed_out"] is True


def test_help_probe_itself_is_bounded(fake_client, tmp_path, monkeypatch, capsys):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    monkeypatch.setenv("OTS_HELP_DELAY", "30")
    assert opentimestamps.main(["--operation-timeout", "0.3", "verify", "--timestamp", str(proof), "--timeout", "3"]) == 124
    result = json.loads(capsys.readouterr().out)
    assert result["command"][-1] == "--help"


def test_invalid_proof_keeps_the_client_error(fake_client, tmp_path, monkeypatch, capsys):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    monkeypatch.setenv("OTS_TEST_MODE", "invalid")
    assert opentimestamps.main(["verify", "--timestamp", str(proof)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["exit_code"] == 2
    assert result["stderr"] == "Invalid timestamp file"
    assert "timed_out" not in result


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group cancellation")
def test_timeout_kills_descendants_that_keep_pipes_open(fake_client, tmp_path, monkeypatch, capsys):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    pid_path = tmp_path / "child.pid"
    monkeypatch.setenv("OTS_TEST_MODE", "descendant")
    monkeypatch.setenv("OTS_CHILD_PID", str(pid_path))
    start = time.monotonic()
    assert opentimestamps.main(["--operation-timeout", "0.4", "verify", "--timestamp", str(proof)]) == 124
    assert time.monotonic() - start < 3
    capsys.readouterr()
    pid = int(pid_path.read_text())
    # Reparented zombies may persist briefly. They must no longer be running.
    state = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True).stdout.strip()
    assert not state or state.startswith("Z")


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf"])
def test_operation_timeout_rejects_unbounded_values(value):
    with pytest.raises(SystemExit) as exc:
        opentimestamps.build_parser().parse_args(["--operation-timeout", value, "info", "--timestamp", "proof.ots"])
    assert exc.value.code == 2


@pytest.mark.parametrize("value", ["0", "-1", "1.5"])
def test_calendar_timeout_requires_positive_whole_seconds(value):
    with pytest.raises(SystemExit) as exc:
        opentimestamps.build_parser().parse_args(["verify", "--timestamp", "proof.ots", "--timeout", value])
    assert exc.value.code == 2


@pytest.mark.skipif(os.name != "posix", reason="POSIX interrupt delivery")
def test_ctrl_c_cancels_the_client_and_returns_130(fake_client, tmp_path, monkeypatch):
    proof = tmp_path / "document.ots"
    proof.write_bytes(b"fixture")
    pid_path = tmp_path / "client.pid"
    monkeypatch.setenv("OTS_TEST_MODE", "stall")
    monkeypatch.setenv("OTS_CLIENT_PID", str(pid_path))
    monkeypatch.setenv("PATH", str(fake_client.parent) + os.pathsep + os.environ["PATH"])
    wrapper = Path(opentimestamps.__file__)
    process = subprocess.Popen([sys.executable, str(wrapper), "verify", "--timestamp", str(proof)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 3
        while not pid_path.exists():
            if time.monotonic() >= deadline:
                pytest.fail("client did not start")
            time.sleep(0.01)
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=3)
        assert process.returncode == 130, stderr
        assert json.loads(stdout)["cancelled"] is True
        pid = int(pid_path.read_text())
        state = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True).stdout.strip()
        assert not state or state.startswith("Z")
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=3)
