#!/usr/bin/env python3
"""Real Croc E2E and regression controls, using disposable data and loopback only."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import signal
import shutil
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "skills/croc/scripts/transfer.py"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def manifest(folder):
    return {p.relative_to(folder).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
            for p in sorted(folder.rglob("*")) if p.is_file()}


def assert_no_terminal():
    assert not any(os.isatty(fd) for fd in (0, 1, 2))
    try:
        fd = os.open("/dev/tty", os.O_RDWR)
    except OSError:
        return
    os.close(fd)
    raise AssertionError("Child has a controlling terminal")


class Case:
    def __init__(self, binary, root):
        self.binary, self.root = binary, root
        self.processes = []
        self.secret = secrets.token_hex(24)
        self.env = {**os.environ, "HOME": str(root / "home"),
                    "XDG_CONFIG_HOME": str(root / "config"), "CROC_SECRET": self.secret,
                    "CROC_NO_UPDATE_CHECK": "1"}
        for key in ("CROC_RELAY", "CROC_PASS", "CROC_STORE_TOKEN", "SOCKS5_PROXY", "HTTP_PROXY"):
            self.env.pop(key, None)
        (root / "home").mkdir()
        self.installed = root / "installed-croc"
        shutil.copytree(ROOT / "skills/croc", self.installed, ignore=shutil.ignore_patterns(".local", "__pycache__"))
        self.helper_path = self.installed / "scripts/transfer.py"
        skill_file = self.installed / "SKILL.md"
        skill_file.write_text(skill_file.read_text().replace(
            "Model may handle transfer links and codes: not configured",
            "Model may handle transfer links and codes: private"))
        self.src, self.dst = root / "source", root / "destination"
        self.src.mkdir(); self.dst.mkdir()
        (self.src / "payload.bin").write_bytes(bytes(range(256)) * 4096)
        (self.src / "bundle/nested").mkdir(parents=True)
        (self.src / "bundle/.git").mkdir()
        (self.src / "bundle/.git/HEAD").write_bytes(b"ref: refs/heads/disposable-test\n")
        (self.src / "bundle/nested/unicode-ç.txt").write_text("Croc unattended transfer\n", encoding="utf-8")
        (self.src / "bundle/empty.txt").touch()
        self.port = self.free_ports()
        self.relay = f"127.0.0.1:{self.port}"
        self.common = [binary, "--relay", self.relay, "--no-update-check", "--disable-clipboard"]
        relay = self.start([binary, "relay", "--host", "127.0.0.1", "--ports",
                            ",".join(str(self.port+i) for i in range(5))], "relay")
        deadline = time.monotonic() + 5
        while True:
            assert relay.poll() is None, "Relay exited before readiness"
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=.1):
                    break
            except OSError:
                if time.monotonic() > deadline:
                    raise AssertionError("Relay did not become ready")
                time.sleep(.05)

    @staticmethod
    def free_ports():
        for _ in range(200):
            port = 20000 + secrets.randbelow(35000)
            sockets = []
            try:
                for p in range(port, port+5):
                    sock = socket.socket()
                    sockets.append(sock)
                    sock.bind(("127.0.0.1", p))
                return port
            except OSError:
                pass
            finally:
                for sock in sockets:
                    sock.close()
        raise AssertionError("Cannot allocate five consecutive loopback ports")

    def start(self, command, name, env=None, piped=None):
        stdout = (self.root / f"{name}.stdout").open("wb")
        stderr = (self.root / f"{name}.stderr").open("wb")
        try:
            process = subprocess.Popen(command, env=env or self.env, cwd=self.root,
                                       stdin=subprocess.PIPE if piped is not None else subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True,
                                       preexec_fn=assert_no_terminal)
        finally:
            stdout.close(); stderr.close()
        self.processes.append(process)
        if piped is not None:
            process.stdin.write(piped)
            process.stdin.close()
        return process

    def helper(self, *args):
        return [sys.executable, str(self.helper_path), "--croc", self.binary, "--relay", self.relay,
                "--relay-only", "--timeout", "8", *args]

    def send(self, helper=False, ignore=True, piped=None):
        files = [str(self.src / "payload.bin"), str(self.src / "bundle")]
        command = self.helper("send", *files) if helper else self.common + ["--yes"] + (
            ["--ignore-stdin"] if ignore else []) + ["send", "--no-local", "--transport", "relay", "--", *files]
        process = self.start(command, "send", piped=piped)
        time.sleep(.5)
        return process

    def receive(self, helper=False, yes=True, env=None):
        command = self.helper("receive", str(self.dst)) if helper else self.common + (
            ["--yes"] if yes else []) + ["--out", str(self.dst)]
        return self.start(command, "receive", env=env)

    def safe_output(self):
        for name in ("send", "receive"):
            data = b"".join((self.root / f"{name}.{stream}").read_bytes()
                            for stream in ("stdout", "stderr") if (self.root / f"{name}.{stream}").exists())
            assert self.secret.encode() not in data, "Helper leaked secret"
            assert b"getcroc.com/?code=" not in data, "Helper leaked receive URL"
        return {name: [json.loads(line) for line in (self.root / f"{name}.stdout").read_text().splitlines()]
                for name in ("send", "receive") if (self.root / f"{name}.stdout").exists()}

    def close(self):
        for process in reversed(self.processes):
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()


def run_case(name, case):
    if name == "helper_allow_generated_invite":
        skill_file = case.installed / "SKILL.md"
        skill_file.write_text(skill_file.read_text().replace(
            "Model may handle transfer links and codes: private",
            "Model may handle transfer links and codes: allowed"))
        sender_env = {**case.env}; sender_env.pop("CROC_SECRET")
        sender = case.start(case.helper("send", str(case.src / "payload.bin"), str(case.src / "bundle")),
                            "send", env=sender_env)
        deadline = time.monotonic() + 3
        invite = None
        while invite is None:
            lines = (case.root / "send.stdout").read_text().splitlines()
            if lines:
                invite = json.loads(lines[0]).get("code")
            assert time.monotonic() < deadline, "Generated invite not returned"
            if invite is None:
                time.sleep(.02)
        assert len(invite) == 48
        receiver = case.receive(helper=True, env={**case.env, "CROC_SECRET": invite})
        rx, tx = receiver.wait(timeout=20), sender.wait(timeout=10)
        assert (tx, rx) == (0, 0)
        assert manifest(case.src) == manifest(case.dst)
        return {"sender_exit": tx, "receiver_exit": rx, "manifest_equal": True,
                "generated_invite_returned": True, "invite_value_omitted_from_report": True}
    if name in ("direct_files_and_folder", "helper_files_and_folder",
                "direct_piped_stdin_ignored", "helper_piped_stdin_ignored"):
        helper = name.startswith("helper")
        piped = b"this input must be ignored\n" if "piped" in name else None
        sender = case.send(helper=helper, piped=piped)
        receiver = case.receive(helper=helper)
        rx, tx = receiver.wait(timeout=20), sender.wait(timeout=10)
        assert (tx, rx) == (0, 0), f"Unexpected exits: sender={tx}, receiver={rx}"
        expected, actual = manifest(case.src), manifest(case.dst)
        assert actual == expected, "Received manifest differs"
        result = {"sender_exit": tx, "receiver_exit": rx, "manifest_equal": True, "manifest": actual}
        if helper:
            result["sanitized_output"] = case.safe_output()
        return result
    if name == "control_missing_ignore_stdin":
        marker = b"piped input must not replace explicit file arguments\n"
        sender = case.send(ignore=False, piped=marker)
        receiver = case.receive()
        rx, tx = receiver.wait(timeout=20), sender.wait(timeout=10)
        assert (tx, rx) == (0, 0)
        assert not (case.dst / "payload.bin").exists(), "Expected piped-input regression not reproduced"
        output = (case.root / "receive.stdout").read_bytes()
        received = [p.read_bytes() for p in case.dst.rglob("*") if p.is_file()]
        assert marker in output or marker in received, "Piped marker not received"
        return {"sender_exit": tx, "receiver_exit": rx, "requested_file_received": False,
                "piped_marker_received": True, "marker_sha256": sha(marker)}
    if name == "control_missing_yes":
        case.send()
        receiver = case.receive(yes=False)
        try:
            code = receiver.wait(timeout=4)
            outcome = {"receiver_exit": code}
        except subprocess.TimeoutExpired:
            outcome = {"receiver_timed_out": True}
        assert not (case.dst / "payload.bin").exists()
        return {**outcome, "requested_file_received": False}
    if name == "helper_missing_secret":
        env = {**case.env}; env.pop("CROC_SECRET")
        process = case.start(case.helper("receive", str(case.dst)), "receive", env=env)
        assert process.wait(timeout=3) == 2
        output = case.safe_output()
        assert output["receive"] == [{"status": "failed", "error": "missing_secret"}]
        return {"receiver_exit": 2, "sanitized_output": output}
    if name == "helper_conflicting_store_token":
        env = {**case.env, "CROC_STORE_TOKEN": "disposable-invalid-token"}
        process = case.start(case.helper("receive", str(case.dst)), "receive", env=env)
        assert process.wait(timeout=3) == 2
        assert not manifest(case.dst)
        output = case.safe_output()
        assert output["receive"] == [{"status": "failed", "error": "conflicting_store_token"}]
        return {"receiver_exit": 2, "files_received": 0, "sanitized_output": output}
    if name == "helper_nonempty_destination":
        (case.dst / "existing.txt").write_bytes(b"preserve this file\n")
        before = manifest(case.dst)
        process = case.receive(helper=True)
        assert process.wait(timeout=3) == 2
        assert manifest(case.dst) == before
        output = case.safe_output()
        assert output["receive"][-1]["error"] == "destination_not_empty_directory"
        return {"receiver_exit": 2, "existing_files_unchanged": True, "sanitized_output": output}
    if name == "helper_wrong_secret":
        sender = case.send(helper=True)
        receiver = case.receive(helper=True, env={**case.env, "CROC_SECRET": secrets.token_hex(24)})
        rx, tx = receiver.wait(timeout=16), sender.wait(timeout=10)
        assert rx != 0 and tx != 0
        assert not manifest(case.dst)
        return {"sender_exit": tx, "receiver_exit": rx, "files_received": 0,
                "sanitized_output": case.safe_output()}
    if name == "helper_timeout":
        command = case.helper("send", str(case.src / "payload.bin"))
        command[command.index("--timeout")+1] = "1"
        process = case.start(command, "send")
        assert process.wait(timeout=8) == 124
        output = case.safe_output()
        assert output["send"][-1] == {"status": "failed", "error": "timeout"}
        return {"sender_exit": 124, "sanitized_output": output}
    if name == "helper_sigterm_cleanup":
        probe = case.root / "child-probe"
        pid_file = case.root / "child.pid"
        probe.write_text(f"#!{sys.executable}\nimport os, pathlib, signal\n"
                         f"pid = pathlib.Path({str(pid_file)!r})\n"
                         "temporary = pid.with_suffix('.tmp')\n"
                         "temporary.write_text(str(os.getpid()))\n"
                         "temporary.replace(pid)\n"
                         "print(os.environ['CROC_SECRET'], flush=True)\n"
                         "signal.pause()\n")
        probe.chmod(0o700)
        command = case.helper("send", str(case.src / "payload.bin"))
        command[command.index("--croc")+1] = str(probe)
        process = case.start(command, "send")
        deadline = time.monotonic() + 3
        while not pid_file.exists():
            assert time.monotonic() < deadline, "Probe did not start"
            time.sleep(.02)
        child_pid = int(pid_file.read_text())
        try:
            process.send_signal(signal.SIGTERM)
            assert process.wait(timeout=8) == 143
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                pass
            else:
                raise AssertionError("Detached child survived wrapper cancellation")
            output = case.safe_output()
            assert output["send"][-1] == {"status": "failed", "error": "interrupted"}
            return {"wrapper_exit": 143, "child_reaped": True, "sanitized_output": output,
                    "fixture": "PID-recording child probe; intentionally prints secret to suppressed stdout"}
        finally:
            try:
                os.kill(child_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    if name == "helper_ignores_saved_config":
        remembered = case.start(case.common + ["--yes", "--remember", "--out", str(case.dst)], "remember")
        deadline = time.monotonic() + 3
        while not list(case.root.rglob("receive.json")):
            assert time.monotonic() < deadline, "Croc did not save receive configuration"
            time.sleep(.02)
        remembered.terminate(); remembered.wait(timeout=5)
        saved = next(case.root.rglob("receive.json"))
        saved.write_text("{invalid saved configuration")
        direct = case.receive()
        assert direct.wait(timeout=4) != 0, "Invalid remembered config control unexpectedly succeeded"
        sender, receiver = case.send(helper=True), case.receive(helper=True)
        rx, tx = receiver.wait(timeout=20), sender.wait(timeout=10)
        assert (tx, rx) == (0, 0)
        assert manifest(case.src) == manifest(case.dst)
        assert saved.read_text() == "{invalid saved configuration"
        return {"sender_exit": tx, "receiver_exit": rx, "manifest_equal": True,
                "saved_config_unchanged": True, "direct_control_failed": True,
                "sanitized_output": case.safe_output()}
    raise AssertionError(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--croc", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    binary = str(Path(args.croc).resolve())
    version = subprocess.check_output([binary, "--version"], text=True).strip()
    assert version == "croc version 11.6.6", version
    report = {"version": version, "platform": platform.platform(), "binary_sha256": sha(Path(binary).read_bytes()),
              "helper_sha256": sha(HELPER.read_bytes()), "transport": "loopback relay; sender --no-local --transport relay",
              "terminal": "All transfer children assert isatty(0/1/2)=false and /dev/tty cannot open",
              "stdin": "DEVNULL except explicit pipe regression and pipe-ignore cases", "cases": []}
    names = ("helper_allow_generated_invite", "direct_files_and_folder", "helper_files_and_folder", "direct_piped_stdin_ignored",
             "helper_piped_stdin_ignored", "control_missing_ignore_stdin",
             "control_missing_yes", "helper_missing_secret", "helper_conflicting_store_token", "helper_nonempty_destination",
             "helper_wrong_secret", "helper_timeout", "helper_sigterm_cleanup", "helper_ignores_saved_config")
    failed = False
    with tempfile.TemporaryDirectory(prefix="croc-e2e-") as temporary:
        for name in names:
            root = Path(temporary) / name; root.mkdir()
            case = None
            started = time.monotonic()
            try:
                case = Case(binary, root)
                result = {"name": name, "passed": True, **run_case(name, case)}
            except Exception as exc:
                # Never dump logs, command lines, environment, or exception messages.
                result = {"name": name, "passed": False, "error_type": type(exc).__name__}
                failed = True
            finally:
                if case:
                    case.close()
            result["seconds"] = round(time.monotonic()-started, 3)
            report["cases"].append(result)
            print(json.dumps(result), flush=True)
    report["passed"] = not failed
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+"\n")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
