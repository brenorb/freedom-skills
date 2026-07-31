from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "skills" / "blossom-storage" / "uvx"
CLI_BINARY = os.environ.get("BLOSSOM_RUST_CLI_BIN") or shutil.which("blossom-cli")
SERVER_BINARY = os.environ.get("BLOSSOM_SERVER_BIN") or shutil.which("blossom-server")


def run_uvx(*args: str, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["uvx", "--from", str(WRAPPER), "blossom", *args]
    return subprocess.run(command, env=env, text=True, capture_output=True, check=check)


@pytest.mark.e2e
def test_uvx_wrapper_delegates_to_rust_cli() -> None:
    if CLI_BINARY is None:
        pytest.skip("install blossom-cli or set BLOSSOM_RUST_CLI_BIN")

    env = os.environ.copy()
    env["BLOSSOM_RUST_CLI_BIN"] = CLI_BINARY
    env["BLOSSOM_CLI_NO_INSTALL"] = "1"

    result = run_uvx("--version", env=env)

    assert result.returncode == 0
    assert "blossom-cli 0.5.6" in result.stdout


@pytest.mark.e2e
def test_upload_exists_download_delete_against_local_rust_server(tmp_path: Path) -> None:
    if CLI_BINARY is None or SERVER_BINARY is None:
        pytest.skip("install blossom-cli and blossom-server or set their *_BIN variables")

    port = 39000 + (os.getpid() % 1000)
    server_url = f"http://127.0.0.1:{port}"
    server_data = tmp_path / "server"
    source = tmp_path / "source.txt"
    downloaded = tmp_path / "downloaded.txt"
    source.write_bytes(b"blossom uvx e2e\n")
    expected_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    env = os.environ.copy()
    env["BLOSSOM_RUST_CLI_BIN"] = CLI_BINARY
    env["BLOSSOM_CLI_NO_INSTALL"] = "1"
    env["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")
    keygen_output = run_uvx("keygen", env=env).stdout
    secret_key_lines = [line for line in keygen_output.splitlines() if line.startswith("Secret key (hex):")]
    public_key_lines = [line for line in keygen_output.splitlines() if line.startswith("Public key (hex):")]
    assert len(secret_key_lines) == 1
    assert len(public_key_lines) == 1
    env["BLOSSOM_SECRET_KEY"] = secret_key_lines[0].split(":", 1)[1].strip()
    public_key = public_key_lines[0].split(":", 1)[1].strip()

    server_env = os.environ.copy()
    server_env["RUST_LOG"] = "warn"
    server = subprocess.Popen(
        [
            SERVER_BINARY,
            "--data-dir",
            str(server_data),
            "--db-path",
            str(tmp_path / "blossom.db"),
            "--bind",
            f"127.0.0.1:{port}",
            "--require-auth",
            "--admin",
            public_key,
        ],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_for_server(server_url, server)

        uploaded = run_uvx(
            "--server",
            server_url,
            "--format",
            "json",
            "--no-publish",
            "upload",
            str(source),
            env=env,
        )
        descriptor = json.loads(uploaded.stdout)
        assert descriptor["sha256"] == expected_hash

        exists = run_uvx(
            "--server",
            server_url,
            "--format",
            "json",
            "exists",
            expected_hash,
            env=env,
        )
        assert parse_exists(exists)

        run_uvx(
            "--server",
            server_url,
            "download",
            expected_hash,
            str(downloaded),
            env=env,
        )
        assert downloaded.read_bytes() == source.read_bytes()
        assert hashlib.sha256(downloaded.read_bytes()).hexdigest() == expected_hash

        deleted = run_uvx(
            "--server",
            server_url,
            "delete",
            expected_hash,
            "--yes",
            env=env,
            check=False,
        )
        assert deleted.returncode == 0, deleted.stderr or deleted.stdout
        missing = run_uvx(
            "--server",
            server_url,
            "exists",
            expected_hash,
            env=env,
            check=False,
        )
        assert missing.returncode != 0 or not parse_exists(missing)
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)


@pytest.mark.e2e
def test_upload_exists_download_delete_against_existing_server(tmp_path: Path) -> None:
    """Exercise a real configured server without requiring blossom-server locally."""
    if CLI_BINARY is None:
        pytest.skip("install blossom-cli or set BLOSSOM_RUST_CLI_BIN")

    server_url = os.environ.get("BLOSSOM_E2E_SERVER", "").rstrip("/")
    secret_key = os.environ.get("BLOSSOM_E2E_SECRET_KEY") or os.environ.get("BLOSSOM_SECRET_KEY")
    if not server_url or not secret_key:
        pytest.skip("set BLOSSOM_E2E_SERVER and BLOSSOM_E2E_SECRET_KEY")

    source = tmp_path / "source.txt"
    downloaded = tmp_path / "downloaded.txt"
    source.write_bytes(b"blossom uvx remote e2e\n" + os.urandom(16))
    expected_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    env = os.environ.copy()
    env["BLOSSOM_RUST_CLI_BIN"] = CLI_BINARY
    env["BLOSSOM_CLI_NO_INSTALL"] = "1"
    env["BLOSSOM_SECRET_KEY"] = secret_key
    env["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")

    uploaded_hash: str | None = None
    try:
        uploaded = run_uvx(
            "--server",
            server_url,
            "--format",
            "json",
            "--no-publish",
            "upload",
            str(source),
            env=env,
        )
        descriptor = json.loads(uploaded.stdout)
        uploaded_hash = descriptor["sha256"]
        assert uploaded_hash == expected_hash

        exists = run_uvx(
            "--server",
            server_url,
            "--format",
            "json",
            "exists",
            expected_hash,
            env=env,
        )
        assert parse_exists(exists)

        run_uvx(
            "--server",
            server_url,
            "download",
            expected_hash,
            str(downloaded),
            env=env,
        )
        assert downloaded.read_bytes() == source.read_bytes()

        deleted = run_uvx(
            "--server",
            server_url,
            "delete",
            expected_hash,
            "--yes",
            env=env,
            check=False,
        )
        assert deleted.returncode == 0, deleted.stderr or deleted.stdout
        uploaded_hash = None

        missing = run_uvx(
            "--server",
            server_url,
            "--format",
            "json",
            "exists",
            expected_hash,
            env=env,
            check=False,
        )
        assert missing.returncode != 0 or not parse_exists(missing)
    finally:
        if uploaded_hash:
            run_uvx(
                "--server",
                server_url,
                "delete",
                uploaded_hash,
                "--yes",
                env=env,
                check=False,
            )


def wait_for_server(server_url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr else ""
            raise AssertionError(f"blossom-server exited before startup: {stderr}")
        try:
            with urlopen(f"{server_url}/health", timeout=1) as response:
                if 200 <= response.status < 300:
                    return
        except (OSError, URLError):
            pass
        time.sleep(0.25)
    raise AssertionError(f"blossom-server did not become ready at {server_url}")


def parse_exists(result: subprocess.CompletedProcess[str]) -> bool:
    """Accept the JSON and text forms emitted by blossom-cli 0.5.x."""
    output = result.stdout.strip()
    try:
        return bool(json.loads(output)["exists"])
    except (KeyError, json.JSONDecodeError, TypeError):
        return output.lower() in {"exists", "true", "yes"}
