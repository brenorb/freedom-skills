"""End-to-end tests for the blossom-cli skill.

Each workflow runs the exact bash blocks from skills/blossom-cli/SKILL.md via
the published `uvx blossom-cli` package against local, in-process Blossom
servers that verify signed kind 24242 authorization per BUD-11.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blossom_server import BlossomTestServer  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "blossom-cli" / "SKILL.md"

MISSING_X_TAG = (
    "blossom-cli 0.5.6 signs delete and mirror authorization without the `x` tag "
    "that BUD-11 requires, so spec-compliant servers reject them with 401"
)
UNKNOWN_IS_ABSENT = (
    "blossom-cli 0.5.6 reports `not found` for a 5xx HEAD response, the same as a 404; "
    "see https://github.com/brenorb/blossom-cli/issues/1"
)

pytestmark = pytest.mark.skipif(shutil.which("uvx") is None, reason="uvx is required")


# --- SKILL.md command extraction --------------------------------------------


def skill_sections() -> dict[str, list[str]]:
    """Map each `## Heading` in SKILL.md to the bash blocks beneath it."""
    sections: dict[str, list[str]] = {}
    current = ""
    for part in re.split(r"(?m)^(## .+)$", SKILL.read_text()):
        if part.startswith("## "):
            current = part[3:].strip()
            continue
        blocks = re.findall(r"```bash\n(.*?)```", part, flags=re.S)
        if blocks:
            sections.setdefault(current, []).extend(blocks)
    return sections


def skill_command(section: str, subcommand: str) -> str:
    """Return the single SKILL.md command for `subcommand` in `section`."""
    commands = []
    for block in skill_sections()[section]:
        for command in block.replace("\\\n", " ").splitlines():
            if re.search(rf"\s{subcommand}\s", f" {command} "):
                commands.append(command.strip())
    assert len(commands) == 1, f"expected one `{subcommand}` command under ## {section}, found {commands}"
    # Swap the documented placeholder paths for variables the test controls.
    return (
        commands[0]
        .replace('"/absolute/path/to/output-file"', '"$OUTPUT_FILE"')
        .replace('"/absolute/path/to/file"', '"$INPUT_FILE"')
    )


# --- Helpers -----------------------------------------------------------------


@pytest.fixture(scope="module")
def keypair() -> dict[str, str]:
    result = subprocess.run(["uvx", "-q", "blossom-cli", "keygen"], capture_output=True, text=True, check=True)
    fields = dict(line.split(":", 1) for line in result.stdout.splitlines() if ":" in line)
    return {
        "secret": fields["Secret key (hex)"].strip(),
        "pubkey": fields["Public key (hex)"].strip(),
    }


@pytest.fixture
def servers():
    with BlossomTestServer() as origin, BlossomTestServer() as replica:
        yield origin, replica


def run_skill(section: str, subcommand: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", skill_command(section, subcommand)],
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        timeout=120,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upload(server: BlossomTestServer, source: Path, keypair: dict[str, str]) -> dict:
    result = run_skill(
        "Upload",
        "upload",
        {"BLOSSOM_SERVER": server.url, "BLOSSOM_SECRET_KEY": keypair["secret"], "INPUT_FILE": str(source)},
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def exists(server: BlossomTestServer, sha256: str, keypair: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return run_skill(
        "Inspect",
        "exists",
        {"BLOSSOM_SERVER": server.url, "BLOSSOM_SECRET_KEY": keypair["secret"], "SHA256": sha256},
    )


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "note.txt"
    path.write_bytes(b"freedom skills blossom e2e\n" + os.urandom(16))
    return path


# --- Static checks on the skill ---------------------------------------------


def test_every_skill_command_uses_uvx_and_keeps_keys_out_of_argv() -> None:
    blocks = [block for blocks in skill_sections().values() for block in blocks]
    assert blocks
    for block in blocks:
        command = block.replace("\\\n", " ")
        for line in filter(str.strip, command.splitlines()):
            assert line.strip().startswith("uvx blossom-cli "), line
            assert not re.search(r"(\s-k\s|--key|nsec1|[0-9a-f]{64})", line), line


def test_writes_default_to_no_publish() -> None:
    for section, subcommand in (("Upload", "upload"), ("Mirror or replicate", "mirror")):
        assert "--no-publish" in skill_command(section, subcommand)


# --- Upload, download, inspect ----------------------------------------------


def test_upload_returns_descriptor_matching_local_hash(servers, source, keypair) -> None:
    origin, _ = servers
    descriptor = upload(origin, source, keypair)

    local_hash = sha256_file(source)
    assert descriptor["sha256"] == local_hash
    assert descriptor["size"] == source.stat().st_size
    assert descriptor["url"] == f"{origin.url}/{local_hash}"
    assert origin.blobs[local_hash].data == source.read_bytes()

    # --no-publish: the only request is the authorized upload itself.
    assert [(r.method, r.path, r.status) for r in origin.requests] == [("PUT", "/upload", 200)]
    tags = origin.requests[0].auth["tags"]
    assert ["t", "upload"] in tags and ["x", local_hash] in tags
    assert origin.requests[0].auth["pubkey"] == keypair["pubkey"]


def test_download_by_hash_produces_identical_bytes(servers, source, keypair, tmp_path) -> None:
    origin, _ = servers
    sha256 = upload(origin, source, keypair)["sha256"]
    output = tmp_path / "downloaded.txt"

    result = run_skill(
        "Download or recover",
        "download",
        {"BLOSSOM_SERVER": origin.url, "BLOSSOM_SECRET_KEY": keypair["secret"], "SHA256": sha256,
         "OUTPUT_FILE": str(output)},
    )

    assert result.returncode == 0, result.stderr
    assert sha256_file(output) == sha256


def test_inspect_status_exists_and_list(servers, source, keypair) -> None:
    origin, _ = servers
    sha256 = upload(origin, source, keypair)["sha256"]
    env = {"BLOSSOM_SERVER": origin.url, "BLOSSOM_SECRET_KEY": keypair["secret"]}

    status = run_skill("Inspect", "status", env)
    assert status.returncode == 0, status.stderr
    assert json.loads(status.stdout)["status"] == "ok"

    present = exists(origin, sha256, keypair)
    assert (present.returncode, present.stdout.strip()) == (0, "exists")

    absent = exists(origin, "0" * 64, keypair)
    assert absent.returncode != 0
    assert absent.stdout.strip() == "not found"

    listed = run_skill("Inspect", "list", {**env, "PUBKEY": keypair["pubkey"]})
    assert listed.returncode == 0, listed.stderr
    assert [item["sha256"] for item in json.loads(listed.stdout)] == [sha256]


# --- Tri-state preflight and recovery ---------------------------------------


def test_exists_never_reports_presence_for_server_errors(servers, source, keypair) -> None:
    origin, _ = servers
    sha256 = upload(origin, source, keypair)["sha256"]
    origin.faults[("HEAD", "/")] = 500

    result = exists(origin, sha256, keypair)

    assert result.returncode != 0
    assert result.stdout.strip() != "exists"


@pytest.mark.xfail(reason=UNKNOWN_IS_ABSENT, strict=True)
def test_exists_distinguishes_server_errors_from_absence(servers, keypair) -> None:
    origin, _ = servers
    absent = exists(origin, "0" * 64, keypair)
    origin.faults[("HEAD", "/")] = 500
    failing = exists(origin, "0" * 64, keypair)

    assert (failing.returncode, failing.stdout, failing.stderr) != (absent.returncode, absent.stdout, absent.stderr)


def test_recovery_fails_over_to_next_server_and_verifies_hash(servers, source, keypair, tmp_path) -> None:
    broken, healthy = servers
    sha256 = upload(healthy, source, keypair)["sha256"]
    broken.faults[("GET", "/")] = 503
    original_url = f"https://cdn.example.invalid/{sha256}.txt"
    output = tmp_path / "recovered.txt"

    # Recovery as the skill describes it: take the hash from the URL, then try
    # servers in priority order until one returns verified bytes.
    recovered_hash = re.findall(r"[0-9a-f]{64}", original_url)[-1]
    attempts = []
    for server in (broken, healthy):
        result = run_skill(
            "Download or recover",
            "download",
            {"BLOSSOM_SERVER": server.url, "BLOSSOM_SECRET_KEY": keypair["secret"], "SHA256": recovered_hash,
             "OUTPUT_FILE": str(output)},
        )
        attempts.append(result.returncode)
        if result.returncode == 0 and sha256_file(output) == recovered_hash:
            break

    assert attempts[0] != 0
    assert attempts[-1] == 0
    assert sha256_file(output) == sha256


# --- Mirror ------------------------------------------------------------------


def mirror(source_server: BlossomTestServer, destination: BlossomTestServer, sha256: str, keypair):
    return run_skill(
        "Mirror or replicate",
        "mirror",
        {"DESTINATION_SERVER": destination.url, "BLOSSOM_SECRET_KEY": keypair["secret"],
         "SOURCE_BLOB_URL": f"{source_server.url}/{sha256}"},
    )


@pytest.mark.xfail(reason=MISSING_X_TAG, strict=True)
def test_mirror_replicates_blob_on_spec_compliant_server(servers, source, keypair) -> None:
    origin, replica = servers
    sha256 = upload(origin, source, keypair)["sha256"]

    result = mirror(origin, replica, sha256, keypair)

    assert result.returncode == 0, result.stderr


def test_mirror_replicates_blob_when_server_accepts_unscoped_auth(servers, source, keypair, tmp_path) -> None:
    origin, replica = servers
    replica.require_x_tags = False
    sha256 = upload(origin, source, keypair)["sha256"]

    result = mirror(origin, replica, sha256, keypair)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["sha256"] == sha256
    assert replica.blobs[sha256].data == source.read_bytes()
    assert exists(replica, sha256, keypair).stdout.strip() == "exists"


# --- Delete ------------------------------------------------------------------


def delete(server: BlossomTestServer, sha256: str, keypair):
    return run_skill(
        "Delete",
        "delete",
        {"BLOSSOM_SERVER": server.url, "BLOSSOM_SECRET_KEY": keypair["secret"], "SHA256": sha256},
    )


@pytest.mark.xfail(reason=MISSING_X_TAG, strict=True)
def test_delete_removes_blob_on_spec_compliant_server(servers, source, keypair) -> None:
    origin, _ = servers
    sha256 = upload(origin, source, keypair)["sha256"]

    result = delete(origin, sha256, keypair)

    assert result.returncode == 0, result.stderr


def test_failed_delete_leaves_blob_in_place(servers, source, keypair) -> None:
    origin, _ = servers
    sha256 = upload(origin, source, keypair)["sha256"]

    result = delete(origin, sha256, keypair)

    assert result.returncode != 0
    assert exists(origin, sha256, keypair).stdout.strip() == "exists"


def test_delete_then_verify_absence_when_server_accepts_unscoped_auth(servers, source, keypair) -> None:
    origin, _ = servers
    origin.require_x_tags = False
    sha256 = upload(origin, source, keypair)["sha256"]

    result = delete(origin, sha256, keypair)

    assert result.returncode == 0, result.stderr
    assert sha256 not in origin.blobs
    assert exists(origin, sha256, keypair).stdout.strip() == "not found"


# --- Fixture sanity -----------------------------------------------------------


def test_fixture_server_rejects_tampered_or_rescoped_authorization(servers, source, keypair) -> None:
    from blossom_server import AuthError, event_id, verify_auth
    import base64

    origin, _ = servers
    sha256 = upload(origin, source, keypair)["sha256"]
    event = origin.requests[0].auth

    def header(e: dict) -> str:
        return "Nostr " + base64.b64encode(json.dumps(e).encode()).decode()

    assert verify_auth(header(event), "upload", sha256)["pubkey"] == keypair["pubkey"]
    with pytest.raises(AuthError, match="scoped to 'delete'"):
        verify_auth(header(event), "delete", sha256)
    with pytest.raises(AuthError, match="blob hash"):
        verify_auth(header(event), "upload", "0" * 64)
    forged = {**event, "tags": [["t", "delete"], *event["tags"][1:]]}
    with pytest.raises(AuthError, match="id mismatch"):
        verify_auth(header(forged), "delete", sha256)
    forged["id"] = event_id(forged)
    with pytest.raises(AuthError, match="signature"):
        verify_auth(header(forged), "delete", sha256)
