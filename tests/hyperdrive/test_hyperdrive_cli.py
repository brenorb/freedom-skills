from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "hyperdrive" / "scripts"
CLI = SCRIPT_DIR / "hyperdrive_cli.js"


def run_cli(*args: str, timeout: int = 30) -> dict:
    cmd = ["node", str(CLI), *args, "--json"]
    result = subprocess.run(
        cmd,
        cwd=SCRIPT_DIR,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=True,
    )
    return json.loads(result.stdout)


def ensure_wrapper_deps() -> None:
    node_modules = SCRIPT_DIR / "node_modules"
    if node_modules.exists():
        return
    subprocess.run(
        ["npm", "install"],
        cwd=SCRIPT_DIR,
        text=True,
        capture_output=True,
        timeout=120,
        check=True,
    )


def test_create_put_list_get_and_mirror_local(tmp_path: Path) -> None:
    ensure_wrapper_deps()

    store = tmp_path / "store"
    source = tmp_path / "note.txt"
    output = tmp_path / "out" / "note.txt"
    mirror_dest = tmp_path / "mirror"
    source.write_text("hello hyperdrive\n", encoding="utf-8")

    created = run_cli("create", "--store", str(store))
    assert created["writable"] is True
    assert created["version"] >= 1
    assert created["drive_id"]

    put = run_cli(
        "put",
        "--store",
        str(store),
        "--source",
        str(source),
        "--path",
        "/drops/note.txt",
    )
    assert put["remote_path"] == "/drops/note.txt"
    assert put["byte_length"] == len("hello hyperdrive\n")
    assert put["written"] == [
        {
            "path": "/drops/note.txt",
            "type": "file",
            "source": str(source),
            "byte_length": len("hello hyperdrive\n"),
        }
    ]

    listed = run_cli("list", "--store", str(store), "--prefix", "/drops")
    assert listed["entries"] == [
        {
            "path": "/drops/note.txt",
            "type": "file",
            "byte_length": len("hello hyperdrive\n"),
            "executable": False,
            "linkname": None,
        }
    ]

    got = run_cli(
        "get",
        "--store",
        str(store),
        "--path",
        "/drops/note.txt",
        "--output",
        str(output),
    )
    assert got["output"] == str(output)
    assert output.read_text(encoding="utf-8") == "hello hyperdrive\n"

    mirrored = run_cli(
        "mirror",
        "--store",
        str(store),
        "--dest",
        str(mirror_dest),
    )
    assert mirrored["written"][0]["path"] == "/drops/note.txt"
    assert (mirror_dest / "drops" / "note.txt").read_text(encoding="utf-8") == "hello hyperdrive\n"


def test_put_directory_and_strip_prefix_mirror(tmp_path: Path) -> None:
    ensure_wrapper_deps()

    store = tmp_path / "store"
    bundle = tmp_path / "bundle"
    mirror_dest = tmp_path / "mirror"
    (bundle / "nested").mkdir(parents=True)
    (bundle / "report.txt").write_text("report body\n", encoding="utf-8")
    (bundle / "nested" / "proof.txt").write_text("proof body\n", encoding="utf-8")

    run_cli("create", "--store", str(store))
    put = run_cli(
        "put",
        "--store",
        str(store),
        "--source",
        str(bundle),
        "--path",
        "/case-123",
    )
    assert put["remote_path"] == "/case-123"
    assert sorted(entry["path"] for entry in put["written"]) == [
        "/case-123/nested/proof.txt",
        "/case-123/report.txt",
    ]

    listed = run_cli("list", "--store", str(store), "--prefix", "/case-123")
    assert sorted(entry["path"] for entry in listed["entries"]) == [
        "/case-123/nested/proof.txt",
        "/case-123/report.txt",
    ]

    mirrored = run_cli(
        "mirror",
        "--store",
        str(store),
        "--prefix",
        "/case-123",
        "--strip-prefix",
        "--dest",
        str(mirror_dest),
    )
    assert mirrored["strip_prefix"] is True
    assert sorted(entry["path"] for entry in mirrored["written"]) == [
        "/case-123/nested/proof.txt",
        "/case-123/report.txt",
    ]
    assert (mirror_dest / "report.txt").read_text(encoding="utf-8") == "report body\n"
    assert (mirror_dest / "nested" / "proof.txt").read_text(encoding="utf-8") == "proof body\n"


def test_seed_then_list_and_get_remote(tmp_path: Path) -> None:
    ensure_wrapper_deps()

    sender_store = tmp_path / "sender-store"
    receiver_store = tmp_path / "receiver-cache"
    source = tmp_path / "evidence.txt"
    downloaded = tmp_path / "downloaded.txt"
    source.write_text("remote evidence\n", encoding="utf-8")

    run_cli("create", "--store", str(sender_store))
    run_cli(
        "put",
        "--store",
        str(sender_store),
        "--source",
        str(source),
        "--path",
        "/evidence.txt",
    )

    proc = subprocess.Popen(
        ["node", str(CLI), "seed", "--store", str(sender_store), "--json"],
        cwd=SCRIPT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        assert proc.stdout is not None
        first_line = proc.stdout.readline().strip()
        payload = json.loads(first_line)
        key = payload["key_hex"]
        assert key

        listed = run_cli(
            "list",
            "--store",
            str(receiver_store),
            "--key",
            key,
            "--prefix",
            "/",
            "--timeout-ms",
            "30000",
            timeout=40,
        )
        assert any(entry["path"] == "/evidence.txt" for entry in listed["entries"])

        got = run_cli(
            "get",
            "--store",
            str(receiver_store),
            "--key",
            key,
            "--path",
            "/evidence.txt",
            "--output",
            str(downloaded),
            "--timeout-ms",
            "30000",
            timeout=40,
        )
        assert got["remote_path"] == "/evidence.txt"
        assert downloaded.read_text(encoding="utf-8") == "remote evidence\n"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
