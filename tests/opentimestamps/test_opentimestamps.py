from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "opentimestamps"
        / "scripts"
        / "opentimestamps.py"
    )
    spec = importlib.util.spec_from_file_location("opentimestamps_skill", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


opentimestamps = load_module()


def test_default_timestamp_path_appends_ots():
    path = Path("/tmp/archive.tar.gz")
    assert opentimestamps.default_timestamp_path(path) == Path("/tmp/archive.tar.gz.ots")


def test_infer_target_path_removes_ots_suffix():
    path = Path("/tmp/archive.tar.gz.ots")
    assert opentimestamps.infer_target_path(path) == Path("/tmp/archive.tar.gz")


def test_backup_timestamp_path_appends_bak():
    path = Path("/tmp/archive.tar.gz.ots")
    assert opentimestamps.backup_timestamp_path(path) == Path("/tmp/archive.tar.gz.ots.bak")


def test_parse_submitted_calendars_reads_all_matches():
    text = """
    Submitting to remote calendar https://a.pool.opentimestamps.org
    Submitting to remote calendar https://b.pool.opentimestamps.org
    """
    assert opentimestamps.parse_submitted_calendars(text) == [
        "https://a.pool.opentimestamps.org",
        "https://b.pool.opentimestamps.org",
    ]


def test_parse_pending_calendars_supports_verify_output():
    text = """
    Calendar https://alice.btc.calendar.opentimestamps.org: Pending confirmation in Bitcoin blockchain
    Calendar https://btc.calendar.catallaxy.com: Pending confirmation in Bitcoin blockchain
    """
    assert opentimestamps.parse_pending_calendars(text) == [
        "https://alice.btc.calendar.opentimestamps.org",
        "https://btc.calendar.catallaxy.com",
    ]


def test_parse_pending_calendars_supports_info_output():
    text = "verify PendingAttestation('https://bob.btc.calendar.opentimestamps.org')"
    assert opentimestamps.parse_pending_calendars(text) == [
        "https://bob.btc.calendar.opentimestamps.org"
    ]


def test_parse_verify_success_extracts_block_and_time():
    text = "Success! Bitcoin block 358391 attests data existed as of 2015-06-05 UTC"
    assert opentimestamps.parse_verify_success(text) == {
        "block_height": 358391,
        "attested_at": "2015-06-05 UTC",
    }


def test_parse_info_summary_extracts_digest_and_pending():
    text = """
    File sha256 hash: e66347a0e1fab2e35b031c12ed6916bd6b8584808ee4e09f82f23fb76d221575
    verify PendingAttestation('https://bob.btc.calendar.opentimestamps.org')
    """
    assert opentimestamps.parse_info_summary(text) == {
        "file_sha256": "e66347a0e1fab2e35b031c12ed6916bd6b8584808ee4e09f82f23fb76d221575",
        "pending_calendars": ["https://bob.btc.calendar.opentimestamps.org"],
    }


def test_resolve_ots_runner_prefers_system_binary(monkeypatch):
    monkeypatch.setattr(opentimestamps.shutil, "which", lambda name: "/usr/bin/ots" if name == "ots" else None)
    assert opentimestamps.resolve_ots_runner() == (["/usr/bin/ots"], "system")


def test_resolve_ots_runner_falls_back_to_uvx(monkeypatch):
    def fake_which(name: str):
        if name == "uvx":
            return "/usr/bin/uvx"
        return None

    monkeypatch.setattr(opentimestamps.shutil, "which", fake_which)
    assert opentimestamps.resolve_ots_runner() == (
        ["/usr/bin/uvx", "--from", "opentimestamps-client", "ots"],
        "uvx",
    )
