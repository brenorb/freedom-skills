#!/usr/bin/env python3
"""Run an authorized Croc transfer under the choice saved in its SKILL.md."""

import argparse
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import tempfile
import time

from invite_policy import read_policy


def status(state, **fields):
    try:
        print(json.dumps({"status": state, **fields}), flush=True)
        return True
    except BrokenPipeError:
        # Avoid another broken-pipe error while Python flushes on exit.
        sys.stdout = open(os.devnull, "w")
        return False


def stop(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--croc", default="croc", help="Croc executable")
    parser.add_argument("--timeout", type=float, default=600, help="Total transfer deadline in seconds")
    parser.add_argument("--relay", help="Explicitly selected relay address")
    parser.add_argument("--relay-only", action="store_true", help="Disable local discovery and use relay data transport")
    modes = parser.add_subparsers(dest="mode", required=True)
    send = modes.add_parser("send", help="Send the approved files or folders")
    send.add_argument("paths", nargs="+")
    receive = modes.add_parser("receive", help="Accept into an existing empty directory")
    receive.add_argument("destination")
    args = parser.parse_args()

    policy = read_policy()
    if policy["model_access"] == "ask":
        status("failed", error="configuration_required", policy=policy)
        return 2
    secret = os.environ.get("CROC_SECRET", "").strip()
    if not secret and args.mode == "send" and policy["model_access"] == "allow":
        secret = secrets.token_hex(24)
    if not secret:
        status("failed", error="missing_secret")
        return 2
    if os.environ.get("CROC_STORE_TOKEN"):
        status("failed", error="conflicting_store_token")
        return 2
    if not 0 < args.timeout < float("inf"):
        status("failed", error="invalid_timeout")
        return 2

    command = [args.croc, "--yes", "--ignore-stdin", "--disable-clipboard", "--no-update-check"]
    if args.relay:
        command += ["--relay", args.relay]
    if args.mode == "send":
        paths = [Path(p).resolve() for p in args.paths]
        if any(not p.exists() for p in paths):
            status("failed", error="missing_input")
            return 2
        command += ["send"]
        if args.relay_only:
            command += ["--no-local", "--transport", "relay"]
        command += ["--", *map(str, paths)]
    else:
        destination = Path(args.destination).resolve()
        try:
            empty = destination.is_dir() and not any(destination.iterdir())
        except OSError:
            empty = False
        if not empty:
            status("failed", error="destination_not_empty_directory")
            return 2
        command += ["--out", str(destination)]

    # Croc emits code-bearing commands/URLs on stderr, including on some failures.
    # Discard both streams at the OS boundary; never relay raw diagnostics.
    cancelled = 0

    def cancel(signum, _frame):
        nonlocal cancelled
        cancelled = signum

    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    # Remembered Croc options can override a receive code/relay/collision policy.
    # Keep each invocation independent without changing the user's Croc config.
    configuration = tempfile.TemporaryDirectory(prefix="croc-transfer-")
    child_env = {**os.environ, "CROC_SECRET": secret, "HOME": configuration.name,
                 "XDG_CONFIG_HOME": str(Path(configuration.name) / "config")}
    try:
        process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True, env=child_env,
        )
    except OSError:
        configuration.cleanup()
        status("failed", error="cannot_start_croc")
        return 2
    try:
        # Only the choice saved in the installed SKILL.md permits exposing an invite.
        fields = {"code": secret} if args.mode == "send" and read_policy()["model_access"] == "allow" else {}
        if not status("running", **fields):
            return 1
        deadline = time.monotonic() + args.timeout
        while True:
            if cancelled:
                stop(process)
                status("failed", error="interrupted")
                return 128 + cancelled
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                stop(process)
                status("failed", error="timeout")
                return 124
            try:
                code = process.wait(timeout=min(.25, remaining))
                break
            except subprocess.TimeoutExpired:
                pass
        if code:
            status("failed", error="croc_failed", exit_code=code)
            return 1
        status("completed")
        return 0
    finally:
        stop(process)
        configuration.cleanup()


if __name__ == "__main__":
    sys.exit(main())
