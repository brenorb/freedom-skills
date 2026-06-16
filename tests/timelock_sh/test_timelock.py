from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def load_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "timelock-sh"
        / "scripts"
        / "timelock.py"
    )
    spec = importlib.util.spec_from_file_location("timelock_skill", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


timelock = load_module()


def test_normalize_minute_accepts_supported_formats():
    assert timelock.normalize_minute("2026-07-01T12:00Z") == "2026-07-01T12:00Z"
    assert timelock.normalize_minute("2026-07-01T12:00:00Z") == "2026-07-01T12:00Z"


def test_normalize_minute_rejects_non_minute_precision():
    with pytest.raises(timelock.TimelockError):
        timelock.normalize_minute("2026-07-01T12:00:30Z")

    with pytest.raises(timelock.TimelockError):
        timelock.normalize_minute("2026-07-01T12:00+00:00")


def test_extract_minute_from_asn1_output():
    text = """
    1234:d=5  hl=2 l=  16 prim: UTF8STRING        :2026-07-01T12:00Z
    """
    assert timelock.extract_minute_from_asn1(text) == "2026-07-01T12:00Z"


def test_default_decrypt_output_strips_enc_suffix():
    path = Path("/tmp/example.txt.enc")
    assert timelock.default_decrypt_output(path) == Path("/tmp/example.txt")


def test_decrypt_file_surfaces_retry_after(monkeypatch, tmp_path):
    encrypted = tmp_path / "secret.txt.enc"
    encrypted.write_bytes(b"ciphertext")

    monkeypatch.setattr(timelock, "ensure_openssl", lambda: "/usr/bin/openssl")
    monkeypatch.setattr(timelock, "extract_minute", lambda input_path, openssl: "2026-07-01T12:00Z")

    def fail_fetch(url: str):
        raise timelock.TimelockHTTPError(
            status=425,
            error="not_yet_released",
            message="key is not available yet",
            retry_after_seconds=42,
        )

    monkeypatch.setattr(timelock, "fetch_url_bytes", fail_fetch)

    with pytest.raises(timelock.TimelockHTTPError) as exc_info:
        timelock.decrypt_file(
            encrypted,
            tmp_path / "secret.txt",
            timelock.DEFAULT_BASE_URL,
            None,
        )

    assert exc_info.value.status == 425
    assert exc_info.value.retry_after_seconds == 42


def test_encrypt_file_invokes_required_openssl_flags(monkeypatch, tmp_path):
    plaintext = tmp_path / "hello.txt"
    plaintext.write_text("hello")
    output = tmp_path / "hello.txt.enc"
    commands = []

    monkeypatch.setattr(timelock, "ensure_openssl", lambda: "/usr/bin/openssl")
    monkeypatch.setattr(timelock, "fetch_url_bytes", lambda url: b"PEM DATA")

    def fake_run(cmd, capture_output=False, text=False):
        commands.append(cmd)
        return None

    monkeypatch.setattr(timelock, "run_checked", fake_run)

    payload = timelock.encrypt_file(
        plaintext,
        "2026-07-01T12:00:00Z",
        output,
        timelock.DEFAULT_BASE_URL,
    )

    assert payload["unlock_minute"] == "2026-07-01T12:00Z"
    assert commands
    cmd = commands[0]
    assert "-binary" in cmd
    assert "-keyopt" in cmd
    assert "rsa_padding_mode:oaep" in cmd
    assert "rsa_oaep_md:sha256" in cmd
    assert "-aes-256-gcm" in cmd


def test_decrypt_file_invokes_binary_mode(monkeypatch, tmp_path):
    encrypted = tmp_path / "hello.txt.enc"
    encrypted.write_bytes(b"ciphertext")
    output = tmp_path / "hello.txt"
    commands = []

    monkeypatch.setattr(timelock, "ensure_openssl", lambda: "/usr/bin/openssl")
    monkeypatch.setattr(timelock, "fetch_url_bytes", lambda url: b"PEM DATA")

    def fake_run(cmd, capture_output=False, text=False):
        commands.append(cmd)
        return None

    monkeypatch.setattr(timelock, "run_checked", fake_run)

    payload = timelock.decrypt_file(
        encrypted,
        output,
        timelock.DEFAULT_BASE_URL,
        "2026-07-01T12:00Z",
    )

    assert payload["unlock_minute"] == "2026-07-01T12:00Z"
    assert commands
    cmd = commands[0]
    assert "-binary" in cmd
    assert "-decrypt" in cmd
