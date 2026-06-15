#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
STATE_ROOT = Path.home() / ".cache" / "freedom-skills" / "filepizza"
RUNTIME_DIR = STATE_ROOT / "runtime"
UPLOADS_DIR = STATE_ROOT / "uploads"
SEED_SCRIPT = Path(__file__).with_name("filepizza_seed.js")


@dataclass(frozen=True)
class UploadPaths:
    upload_id: str
    manifest_path: Path
    state_path: Path
    log_path: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def create_upload_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(4)


def get_upload_paths(upload_id: str) -> UploadPaths:
    return UploadPaths(
        upload_id=upload_id,
        manifest_path=UPLOADS_DIR / f"{upload_id}.json",
        state_path=UPLOADS_DIR / f"{upload_id}.state.json",
        log_path=UPLOADS_DIR / f"{upload_id}.log",
    )


def ensure_directories() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def require_binary(name: str) -> None:
    if shutil.which(name):
        return
    raise RuntimeError(f"Required binary not found in PATH: {name}")


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def tmux_available() -> bool:
    return shutil.which("tmux") is not None


def tmux_session_name(upload_id: str) -> str:
    return f"filepizza_{upload_id}"


def is_tmux_session_alive(session_name: str | None) -> bool:
    if not session_name or not tmux_available():
        return False
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_runtime() -> None:
    require_binary("node")
    require_binary("npm")

    package_json = RUNTIME_DIR / "package.json"
    node_modules = RUNTIME_DIR / "node_modules" / "playwright"
    chromium_marker = RUNTIME_DIR / ".chromium-installed"

    if not package_json.exists():
        run(["npm", "init", "-y"], cwd=RUNTIME_DIR)
    if not node_modules.exists():
        run(["npm", "install", "playwright"], cwd=RUNTIME_DIR)
    if not chromium_marker.exists():
        run(["npx", "playwright", "install", "chromium"], cwd=RUNTIME_DIR)
        chromium_marker.write_text("ok\n")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def is_pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def tail_text(path: Path, limit: int = 20) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(errors="replace").splitlines()
    return lines[-limit:]


def merge_upload_state(manifest: dict[str, object]) -> dict[str, object]:
    result = dict(manifest)
    state_path = Path(str(manifest["state_path"]))
    if state_path.exists():
        result.update(read_json(state_path))
    pid = result.get("pid")
    pid_alive = is_pid_alive(int(pid)) if isinstance(pid, int) else False
    tmux_alive = is_tmux_session_alive(str(result.get("tmux_session"))) if result.get("launcher") == "tmux" else False
    alive = pid_alive or tmux_alive
    result["alive"] = alive
    if result.get("status") == "seeding" and not alive:
        result["status"] = "stopped"
    return result


def wait_for_share_links(paths: UploadPaths, timeout_s: int = 180) -> dict[str, object]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if paths.state_path.exists():
            data = read_json(paths.state_path)
            if data.get("short_url") and data.get("long_url"):
                return data
        time.sleep(1)
    log_lines = "\n".join(tail_text(paths.log_path))
    raise RuntimeError("Timed out waiting for FilePizza share links.\n" + log_lines.strip())


def start_upload(file_path: Path) -> dict[str, object]:
    ensure_directories()
    ensure_runtime()

    resolved = file_path.expanduser().resolve()
    if not resolved.exists() or not resolved.is_file():
        raise RuntimeError(f"Local file not found: {resolved}")

    upload_id = create_upload_id()
    paths = get_upload_paths(upload_id)
    manifest = {
        "ok": True,
        "upload_id": upload_id,
        "file": str(resolved),
        "state_path": str(paths.state_path),
        "log_path": str(paths.log_path),
        "status": "starting",
        "started_at": utc_now(),
    }
    write_json(paths.manifest_path, manifest)

    if tmux_available():
        session_name = tmux_session_name(upload_id)
        command = " ".join(
            [
                f"cd {shlex.quote(str(RUNTIME_DIR))}",
                "&&",
                "node",
                shlex.quote(str(SEED_SCRIPT)),
                shlex.quote(str(resolved)),
                shlex.quote(str(paths.state_path)),
                shlex.quote(upload_id),
                f">> {shlex.quote(str(paths.log_path))} 2>&1",
            ]
        )
        paths.log_path.write_text("")
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "sh", "-lc", command],
            check=True,
        )
        manifest["launcher"] = "tmux"
        manifest["tmux_session"] = session_name
    else:
        with paths.log_path.open("w") as log_file:
            process = subprocess.Popen(
                ["node", str(SEED_SCRIPT), str(resolved), str(paths.state_path), upload_id],
                cwd=str(RUNTIME_DIR),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                text=True,
            )
        manifest["launcher"] = "subprocess"
        manifest["pid"] = process.pid
    write_json(paths.manifest_path, manifest)

    state = wait_for_share_links(paths)
    result = merge_upload_state(read_json(paths.manifest_path))
    result.update(state)
    write_json(paths.manifest_path, result)
    return result


def load_manifest(upload_id: str) -> dict[str, object]:
    paths = get_upload_paths(upload_id)
    if not paths.manifest_path.exists():
        raise RuntimeError(f"Unknown upload_id: {upload_id}")
    return read_json(paths.manifest_path)


def list_uploads() -> list[dict[str, object]]:
    ensure_directories()
    uploads = []
    for path in sorted(UPLOADS_DIR.glob("*.json"), reverse=True):
        if path.name.endswith(".state.json"):
            continue
        uploads.append(merge_upload_state(read_json(path)))
    return uploads


def status_upload(upload_id: str) -> dict[str, object]:
    return merge_upload_state(load_manifest(upload_id))


def stop_upload(upload_id: str) -> dict[str, object]:
    manifest = load_manifest(upload_id)
    pid = manifest.get("pid")
    if manifest.get("launcher") == "tmux":
        session_name = str(manifest.get("tmux_session") or "")
        if is_tmux_session_alive(session_name):
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=True)
            deadline = time.time() + 10
            while time.time() < deadline and is_tmux_session_alive(session_name):
                time.sleep(0.25)
        if isinstance(pid, int) and is_pid_alive(pid):
            os.kill(pid, signal.SIGTERM)
            deadline = time.time() + 10
            while time.time() < deadline and is_pid_alive(pid):
                time.sleep(0.25)
    else:
        if isinstance(pid, int) and is_pid_alive(pid):
            os.kill(pid, signal.SIGTERM)
            deadline = time.time() + 10
            while time.time() < deadline and is_pid_alive(pid):
                time.sleep(0.25)
    result = merge_upload_state(manifest)
    result["status"] = "stopped"
    write_json(Path(str(manifest["manifest_path"])) if "manifest_path" in manifest else get_upload_paths(upload_id).manifest_path, result)
    return result


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
