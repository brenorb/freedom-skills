#!/usr/bin/env python3
"""Structured wrapper around the official OpenTimestamps client."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

VERIFY_SUCCESS_RE = re.compile(
    r"Success! Bitcoin block (?P<block_height>\d+) attests data existed as of (?P<attested_at>.+)"
)
FILE_HASH_RE = re.compile(r"^\s*File sha256 hash:\s*(?P<digest>[0-9a-f]{64})$", re.MULTILINE)
PENDING_CALENDAR_RE = re.compile(
    r"^\s*Calendar (?P<calendar>\S+): Pending confirmation in Bitcoin blockchain$",
    re.MULTILINE,
)
SUBMITTED_CALENDAR_RE = re.compile(
    r"^\s*Submitting to remote calendar (?P<calendar>\S+)$",
    re.MULTILINE,
)
INFO_PENDING_RE = re.compile(r"verify PendingAttestation\('(?P<calendar>[^']+)'\)")


class OpenTimestampsError(RuntimeError):
    """Operational error for the wrapper."""


@dataclass
class OpenTimestampsCommandError(OpenTimestampsError):
    message: str
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str


def ensure_file(path: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        raise OpenTimestampsError(f"file not found: {file_path}")
    return file_path


def default_timestamp_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.name}.ots")


def infer_target_path(timestamp_path: Path) -> Path:
    if timestamp_path.name.endswith(".ots"):
        return timestamp_path.with_name(timestamp_path.name[:-4])
    return timestamp_path.with_name(f"{timestamp_path.name}.target")


def backup_timestamp_path(timestamp_path: Path) -> Path:
    return timestamp_path.with_name(f"{timestamp_path.name}.bak")


def resolve_ots_runner() -> tuple[list[str], str]:
    ots = shutil.which("ots")
    if ots:
        return [ots], "system"

    uvx = shutil.which("uvx")
    if uvx:
        return [uvx, "--from", "opentimestamps-client", "ots"], "uvx"

    uv = shutil.which("uv")
    if uv:
        return [uv, "tool", "run", "--from", "opentimestamps-client", "ots"], "uv"

    raise OpenTimestampsError("OpenTimestamps client not found; install `ots`, `uvx`, or `uv`")


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise OpenTimestampsCommandError(
            message="OpenTimestamps command failed",
            command=cmd,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    return result


def parse_submitted_calendars(text: str) -> list[str]:
    return SUBMITTED_CALENDAR_RE.findall(text)


def parse_pending_calendars(text: str) -> list[str]:
    pending = PENDING_CALENDAR_RE.findall(text)
    if pending:
        return pending
    return INFO_PENDING_RE.findall(text)


def parse_verify_success(text: str) -> dict | None:
    match = VERIFY_SUCCESS_RE.search(text)
    if not match:
        return None
    return {
        "block_height": int(match.group("block_height")),
        "attested_at": match.group("attested_at").strip(),
    }


def parse_info_summary(text: str) -> dict:
    summary: dict[str, object] = {
        "pending_calendars": parse_pending_calendars(text),
    }
    hash_match = FILE_HASH_RE.search(text)
    if hash_match:
        summary["file_sha256"] = hash_match.group("digest")
    return summary


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part).strip()


def build_global_args(args: argparse.Namespace) -> list[str]:
    command: list[str] = []
    if args.wait:
        command.append("--wait")
    if args.no_bitcoin:
        command.append("--no-bitcoin")
    if args.bitcoin_node:
        command.extend(["--bitcoin-node", args.bitcoin_node])
    if args.socks5_proxy:
        command.extend(["--socks5-proxy", args.socks5_proxy])
    return command


def stamp(args: argparse.Namespace) -> dict:
    input_path = ensure_file(args.input)
    requested_path = Path(args.timestamp).expanduser().resolve() if args.timestamp else None
    default_path = default_timestamp_path(input_path)
    runner, runner_kind = resolve_ots_runner()
    command = runner + build_global_args(args) + ["stamp"]
    for calendar in args.calendar:
        command.extend(["--calendar", calendar])
    if args.timeout is not None:
        command.extend(["--timeout", str(args.timeout)])
    if args.min_calendars is not None:
        command.extend(["-m", str(args.min_calendars)])
    command.append(str(input_path))
    result = run_checked(command)
    created_path = default_path
    if requested_path and requested_path != default_path and default_path.is_file():
        requested_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(default_path), str(requested_path))
        created_path = requested_path
    return {
        "action": "stamp",
        "input_path": str(input_path),
        "timestamp_path": str(created_path),
        "runner": runner_kind,
        "submitted_calendars": parse_submitted_calendars(combined_output(result)),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def upgrade(args: argparse.Namespace) -> dict:
    timestamp_path = ensure_file(args.timestamp)
    runner, runner_kind = resolve_ots_runner()
    command = runner + build_global_args(args) + ["upgrade"]
    for calendar in args.calendar:
        command.extend(["--calendar", calendar])
    if args.dry_run:
        command.append("--dry-run")
    command.append(str(timestamp_path))
    result = run_checked(command)
    backup_path = backup_timestamp_path(timestamp_path)
    output = combined_output(result)
    return {
        "action": "upgrade",
        "timestamp_path": str(timestamp_path),
        "runner": runner_kind,
        "backup_path": str(backup_path) if backup_path.exists() else None,
        "pending_calendars": parse_pending_calendars(output),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def verify(args: argparse.Namespace) -> dict:
    if bool(args.input) and bool(args.digest):
        raise OpenTimestampsError("use either --input or --digest, not both")

    timestamp_path = ensure_file(args.timestamp)
    runner, runner_kind = resolve_ots_runner()
    command = runner + build_global_args(args) + ["verify"]
    input_path = None
    if args.input:
        input_path = ensure_file(args.input)
        command.extend(["-f", str(input_path)])
    elif args.digest:
        command.extend(["-d", args.digest])
    else:
        inferred = infer_target_path(timestamp_path)
        if inferred.is_file():
            input_path = inferred
    command.append(str(timestamp_path))
    result = run_checked(command)
    output = combined_output(result)
    return {
        "action": "verify",
        "timestamp_path": str(timestamp_path),
        "input_path": str(input_path) if input_path else None,
        "runner": runner_kind,
        "pending_calendars": parse_pending_calendars(output),
        "verification": parse_verify_success(output),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def info(args: argparse.Namespace) -> dict:
    timestamp_path = ensure_file(args.timestamp)
    runner, runner_kind = resolve_ots_runner()
    command = runner + build_global_args(args) + ["info", str(timestamp_path)]
    result = run_checked(command)
    output = combined_output(result)
    summary = parse_info_summary(output)
    return {
        "action": "info",
        "timestamp_path": str(timestamp_path),
        "runner": runner_kind,
        "summary": summary,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenTimestamps structured wrapper")
    parser.add_argument("--wait", action="store_true", help="wait for a complete attestation when supported")
    parser.add_argument("--no-bitcoin", action="store_true", help="disable Bitcoin verification logic")
    parser.add_argument("--bitcoin-node", help="Bitcoin node URL for verify flows")
    parser.add_argument("--socks5-proxy", help="route network traffic through a socks5 proxy")

    subparsers = parser.add_subparsers(dest="command", required=True)

    stamp_parser = subparsers.add_parser("stamp", help="timestamp a local file")
    stamp_parser.add_argument("--input", required=True, help="path to the local file")
    stamp_parser.add_argument("--timestamp", help="expected .ots path; defaults to <input>.ots")
    stamp_parser.add_argument("--calendar", action="append", default=[], help="calendar URL override")
    stamp_parser.add_argument("--timeout", type=int, help="calendar timeout in seconds")
    stamp_parser.add_argument("--min-calendars", type=int, help="minimum calendars before returning")

    upgrade_parser = subparsers.add_parser("upgrade", help="upgrade an existing .ots file")
    upgrade_parser.add_argument("--timestamp", required=True, help="path to the .ots file")
    upgrade_parser.add_argument("--calendar", action="append", default=[], help="calendar URL override")
    upgrade_parser.add_argument("--dry-run", action="store_true", help="show whether upgrade would succeed")

    verify_parser = subparsers.add_parser("verify", help="verify an existing .ots file")
    verify_parser.add_argument("--timestamp", required=True, help="path to the .ots file")
    verify_target = verify_parser.add_mutually_exclusive_group()
    verify_target.add_argument("--input", help="path to the original file")
    verify_target.add_argument("--digest", help="hex-encoded digest to verify instead of a file")

    info_parser = subparsers.add_parser("info", help="inspect an existing .ots file")
    info_parser.add_argument("--timestamp", required=True, help="path to the .ots file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "stamp":
            payload = stamp(args)
        elif args.command == "upgrade":
            payload = upgrade(args)
        elif args.command == "verify":
            payload = verify(args)
        else:
            payload = info(args)
        print_json(payload)
        return 0
    except OpenTimestampsCommandError as exc:
        output = "\n".join(part for part in [exc.stdout.strip(), exc.stderr.strip()] if part).strip()
        print_json(
            {
                "ok": False,
                "error": exc.message,
                "command": exc.command,
                "exit_code": exc.exit_code,
                "pending_calendars": parse_pending_calendars(output),
                "submitted_calendars": parse_submitted_calendars(output),
                "verification": parse_verify_success(output),
                "stdout": exc.stdout.strip(),
                "stderr": exc.stderr.strip(),
            }
        )
        return exc.exit_code or 1
    except OpenTimestampsError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
