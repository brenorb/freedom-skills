#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


PACKAGE_SPEC = os.environ.get("FILEPIZZA_CLI_SPEC", "filepizza-cli@0.1.0")
STATE_ROOT = Path.home() / ".cache" / "filepizza-cli"
UPLOADS_DIR = STATE_ROOT / "uploads"


def require_binary(name: str) -> None:
    if shutil.which(name):
        return
    raise RuntimeError(f"Required binary not found in PATH: {name}")


def ensure_runtime() -> None:
    require_binary("node")
    require_binary("npm")


def snake_case_key(key: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()


def normalize_value(value: object) -> object:
    if isinstance(value, dict):
        return {snake_case_key(str(key)): normalize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value


def normalize_manifest(payload: dict[str, object]) -> dict[str, object]:
    normalized = dict(normalize_value(payload))
    if "file_path" in normalized and "file" not in normalized:
        normalized["file"] = normalized["file_path"]
    if "upload_id" in normalized and "id" not in normalized:
        normalized["id"] = normalized["upload_id"]
    return normalized


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def is_pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def materialize_manifest_status(manifest: dict[str, object]) -> dict[str, object]:
    result = dict(manifest)
    pid = result.get("pid")
    alive = is_pid_alive(int(pid)) if isinstance(pid, int) else False
    result["alive"] = alive
    if result.get("status") == "seeding" and not alive:
        result["status"] = "stopped"
    return result


def run_filepizza_cli(args: list[str]) -> dict[str, object]:
    ensure_runtime()
    result = subprocess.run(
        ["npx", "--yes", PACKAGE_SPEC, *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip() or f"filepizza-cli failed with exit code {result.returncode}"
        raise RuntimeError(error_text)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"filepizza-cli returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("filepizza-cli returned a non-object JSON payload")
    return payload


def start_upload(file_path: Path) -> dict[str, object]:
    resolved = file_path.expanduser().resolve()
    if not resolved.exists() or not resolved.is_file():
        raise RuntimeError(f"Local file not found: {resolved}")
    return normalize_manifest(run_filepizza_cli(["share", str(resolved)]))


def load_manifest(upload_id: str) -> dict[str, object]:
    manifest_path = UPLOADS_DIR / f"{upload_id}.json"
    if not manifest_path.exists():
        raise RuntimeError(f"Unknown upload_id: {upload_id}")
    return read_json(manifest_path)


def list_uploads() -> list[dict[str, object]]:
    if not UPLOADS_DIR.exists():
        return []
    uploads: list[dict[str, object]] = []
    for path in sorted(UPLOADS_DIR.glob("*.json"), reverse=True):
        manifest = materialize_manifest_status(load_manifest(path.stem))
        uploads.append(normalize_manifest(manifest))
    return uploads


def status_upload(upload_id: str) -> dict[str, object]:
    return normalize_manifest(run_filepizza_cli(["status", upload_id]))


def stop_upload(upload_id: str) -> dict[str, object]:
    return normalize_manifest(run_filepizza_cli(["stop", upload_id]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Public FilePizza wrapper for Freedom Skills")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload_parser = subparsers.add_parser("upload", help="Create a new file.pizza upload")
    upload_parser.add_argument("file", help="Absolute or user-relative path to the local file")

    status_parser = subparsers.add_parser("status", help="Inspect an existing upload")
    status_parser.add_argument("upload_id")

    stop_parser = subparsers.add_parser("stop", help="Stop an existing upload")
    stop_parser.add_argument("upload_id")

    subparsers.add_parser("list", help="List known uploads")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "upload":
        result = start_upload(Path(args.file))
    elif args.command == "status":
        result = status_upload(args.upload_id)
    elif args.command == "stop":
        result = stop_upload(args.upload_id)
    elif args.command == "list":
        result = {"ok": True, "uploads": list_uploads()}
    else:
        raise RuntimeError(f"Unsupported command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
