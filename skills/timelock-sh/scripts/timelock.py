#!/usr/bin/env python3
"""Wrapper for timelock.sh file encryption and decryption."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DEFAULT_BASE_URL = "https://timelock.sh"
MINUTE_WITH_SECONDS = "%Y-%m-%dT%H:%M:%SZ"
MINUTE_NO_SECONDS = "%Y-%m-%dT%H:%MZ"
TIMESTAMP_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z")


class TimelockError(RuntimeError):
    """Operational error for the wrapper."""


@dataclass
class TimelockHTTPError(TimelockError):
    status: int
    error: str
    message: str
    retry_after_seconds: int | None = None


def normalize_minute(raw: str) -> str:
    """Normalize accepted timelock.sh minute formats to YYYY-MM-DDTHH:MMZ."""
    value = raw.strip()
    try:
        parsed = datetime.strptime(value, MINUTE_NO_SECONDS)
        return parsed.strftime(MINUTE_NO_SECONDS)
    except ValueError:
        pass

    try:
        parsed = datetime.strptime(value, MINUTE_WITH_SECONDS)
    except ValueError as exc:
        raise TimelockError(
            "unlock minute must be UTC in YYYY-MM-DDTHH:MMZ or YYYY-MM-DDTHH:MM:00Z form"
        ) from exc

    if parsed.second != 0:
        raise TimelockError("unlock minute must be truncated to the minute")
    return parsed.strftime(MINUTE_NO_SECONDS)


def default_encrypt_output(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.name}.enc")


def default_decrypt_output(input_path: Path) -> Path:
    if input_path.name.endswith(".enc"):
        return input_path.with_name(input_path.name[:-4])
    return input_path.with_name(f"{input_path.name}.decrypted")


def ensure_input_file(path: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        raise TimelockError(f"input file not found: {file_path}")
    return file_path


def ensure_openssl() -> str:
    openssl = shutil.which("openssl")
    if not openssl:
        raise TimelockError("openssl not found in PATH")

    result = run_checked([openssl, "version"], capture_output=True, text=True)
    version_line = result.stdout.strip()
    if "OpenSSL 3." not in version_line:
        raise TimelockError(f"OpenSSL 3.x required, found: {version_line}")
    return openssl


def build_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def fetch_url_bytes(url: str) -> bytes:
    request = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        error = ""
        message = body or exc.reason
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            error = str(payload.get("error", "") or "")
            message = str(payload.get("message", "") or message)
        retry_after = exc.headers.get("Retry-After")
        raise TimelockHTTPError(
            status=exc.code,
            error=error,
            message=message,
            retry_after_seconds=int(retry_after) if retry_after and retry_after.isdigit() else None,
        ) from exc
    except urllib.error.URLError as exc:
        raise TimelockError(f"network error while fetching {url}: {exc.reason}") from exc


def fetch_json(url: str) -> dict:
    payload = fetch_url_bytes(url)
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise TimelockError(f"invalid JSON response from {url}") from exc


def run_checked(
    cmd: list[str], *, capture_output: bool = False, text: bool = False
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=True, capture_output=capture_output, text=text)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if isinstance(exc.stderr, str) else ""
        stdout = exc.stdout.strip() if isinstance(exc.stdout, str) else ""
        detail = stderr or stdout or f"exit status {exc.returncode}"
        raise TimelockError(f"command failed: {' '.join(cmd)}: {detail}") from exc


def extract_minute_from_asn1(text: str) -> str:
    match = TIMESTAMP_RE.search(text)
    if not match:
        raise TimelockError("could not find unlock minute embedded in ciphertext")
    return match.group(0)


def extract_minute(input_path: Path, openssl: str) -> str:
    result = run_checked(
        [openssl, "asn1parse", "-inform", "DER", "-in", str(input_path)],
        capture_output=True,
        text=True,
    )
    return extract_minute_from_asn1(result.stdout)


def write_temp_file(contents: bytes, suffix: str) -> tempfile.NamedTemporaryFile:
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    handle.write(contents)
    handle.flush()
    handle.close()
    return handle


def encrypt_file(input_path: Path, unlock_minute: str, output_path: Path, base_url: str) -> dict:
    openssl = ensure_openssl()
    minute = normalize_minute(unlock_minute)
    cert_url = build_url(
        base_url,
        f"/api/v1/keys/{urllib.parse.quote(minute, safe='')}/cert",
    )
    cert_file = write_temp_file(fetch_url_bytes(cert_url), ".pem")
    try:
        run_checked(
            [
                openssl,
                "cms",
                "-encrypt",
                "-binary",
                "-in",
                str(input_path),
                "-recip",
                cert_file.name,
                "-keyopt",
                "rsa_padding_mode:oaep",
                "-keyopt",
                "rsa_oaep_md:sha256",
                "-aes-256-gcm",
                "-outform",
                "DER",
                "-out",
                str(output_path),
            ]
        )
    finally:
        Path(cert_file.name).unlink(missing_ok=True)

    return {
        "action": "encrypt",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "unlock_minute": minute,
        "cert_url": cert_url,
    }


def decrypt_file(
    input_path: Path, output_path: Path, base_url: str, minute_override: str | None
) -> dict:
    openssl = ensure_openssl()
    minute = normalize_minute(minute_override) if minute_override else extract_minute(input_path, openssl)
    key_url = build_url(
        base_url,
        f"/api/v1/keys/{urllib.parse.quote(minute, safe='')}/key",
    )
    key_file = write_temp_file(fetch_url_bytes(key_url), ".pem")
    try:
        run_checked(
            [
                openssl,
                "cms",
                "-decrypt",
                "-binary",
                "-inform",
                "DER",
                "-in",
                str(input_path),
                "-inkey",
                key_file.name,
                "-out",
                str(output_path),
            ]
        )
    finally:
        Path(key_file.name).unlink(missing_ok=True)

    return {
        "action": "decrypt",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "unlock_minute": minute,
        "key_url": key_url,
    }


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="timelock.sh OpenSSL wrapper")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="timelock.sh base URL (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt", help="encrypt a file to a future UTC minute")
    encrypt_parser.add_argument("--unlock", required=True, help="UTC minute in YYYY-MM-DDTHH:MMZ form")
    encrypt_parser.add_argument("--input", required=True, help="path to plaintext input file")
    encrypt_parser.add_argument("--output", help="output path for the ciphertext")

    decrypt_parser = subparsers.add_parser("decrypt", help="decrypt a released ciphertext")
    decrypt_parser.add_argument("--input", required=True, help="path to ciphertext input file")
    decrypt_parser.add_argument("--output", help="output path for the plaintext")
    decrypt_parser.add_argument(
        "--unlock",
        help="override the embedded unlock minute instead of extracting it from the ciphertext",
    )

    extract_parser = subparsers.add_parser(
        "extract-minute",
        help="extract the embedded unlock minute from a ciphertext",
    )
    extract_parser.add_argument("--input", required=True, help="path to ciphertext input file")

    subparsers.add_parser("status", help="fetch the timelock.sh service status")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "encrypt":
            input_path = ensure_input_file(args.input)
            output_path = (
                Path(args.output).expanduser().resolve()
                if args.output
                else default_encrypt_output(input_path)
            )
            payload = encrypt_file(input_path, args.unlock, output_path, args.base_url)
        elif args.command == "decrypt":
            input_path = ensure_input_file(args.input)
            output_path = (
                Path(args.output).expanduser().resolve()
                if args.output
                else default_decrypt_output(input_path)
            )
            payload = decrypt_file(input_path, output_path, args.base_url, args.unlock)
        elif args.command == "extract-minute":
            input_path = ensure_input_file(args.input)
            payload = {
                "action": "extract-minute",
                "input_path": str(input_path),
                "unlock_minute": extract_minute(input_path, ensure_openssl()),
            }
        else:
            payload = {
                "action": "status",
                "base_url": args.base_url,
                "status": fetch_json(build_url(args.base_url, "/api/v1/status")),
            }

        print_json(payload)
        return 0
    except TimelockHTTPError as exc:
        print_json(
            {
                "error": exc.error or "http_error",
                "message": exc.message,
                "retry_after_seconds": exc.retry_after_seconds,
                "status": exc.status,
            }
        )
        return 1
    except TimelockError as exc:
        print_json({"error": "timelock_error", "message": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
