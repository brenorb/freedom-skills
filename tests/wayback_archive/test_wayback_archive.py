from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest


def load_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "wayback-archive"
        / "scripts"
        / "wayback_archive.py"
    )
    spec = importlib.util.spec_from_file_location("wayback_archive_skill", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


wayback_archive = load_module()


class FakeResponse:
    def __init__(self, *, url: str, body: bytes = b"{}"):
        self._url = url
        self._body = body

    def geturl(self):
        return self._url

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def test_extract_timestamp_returns_capture_id():
    url = "https://web.archive.org/web/20260702020209/https://example.com/"
    assert wayback_archive.extract_timestamp(url) == "20260702020209"


def test_validate_wayback_timestamp_rejects_non_14_digit_input():
    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.validate_wayback_timestamp("nope", "--timestamp")

    assert "14-digit Wayback timestamp" in str(exc_info.value)


def test_validate_wayback_timestamp_rejects_impossible_calendar_values():
    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.validate_wayback_timestamp("20261301120000", "--timestamp")

    assert "real calendar timestamp" in str(exc_info.value)


def test_build_lookup_urls_adds_https_variant_for_http_input():
    assert wayback_archive.build_lookup_urls("http://example.com/path?x=1") == [
        "http://example.com/path?x=1",
        "https://example.com/path?x=1",
    ]


def test_get_available_snapshot_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(wayback_archive, "fetch_json", lambda url, timeout=60: {"archived_snapshots": {}})
    assert wayback_archive.get_available_snapshot("https://example.com") is None


def test_get_available_snapshot_returns_closest_snapshot(monkeypatch):
    monkeypatch.setattr(
        wayback_archive,
        "fetch_json",
        lambda url, timeout=60: {
            "archived_snapshots": {
                "closest": {
                    "available": True,
                    "status": "200",
                    "url": "https://web.archive.org/web/20260702020209/https://example.com/",
                    "timestamp": "20260702020209",
                }
            }
        },
    )

    result = wayback_archive.get_available_snapshot("https://example.com")

    assert result == {
        "input_url": "https://example.com",
        "archived_url": "https://web.archive.org/web/20260702020209/https://example.com/",
        "timestamp": "20260702020209",
        "status": "200",
        "available": True,
    }


def test_get_available_snapshot_with_variants_tries_alternate_scheme(monkeypatch):
    def fake_available(url, timestamp=None, timeout=60):
        if url == "http://example.com":
            return None
        return {
            "input_url": url,
            "archived_url": "https://web.archive.org/web/20260702020209/https://example.com/",
            "timestamp": "20260702020209",
            "status": "200",
            "available": True,
        }

    monkeypatch.setattr(wayback_archive, "get_available_snapshot", fake_available)

    result = wayback_archive.get_available_snapshot_with_variants("http://example.com")

    assert result["input_url"] == "https://example.com"


def test_parse_cdx_response_parses_snapshot_rows():
    text = (
        "com,example)/ 20260101120000 https://example.com text/html 200 AAAA 123\n"
        "com,example)/ 20260102120000 https://example.com text/html 200 BBBB 456\n"
    )

    result = wayback_archive.parse_cdx_response(text)

    assert result == [
        {
            "urlkey": "com,example)/",
            "timestamp": "20260101120000",
            "original": "https://example.com",
            "mimetype": "text/html",
            "statuscode": "200",
            "digest": "AAAA",
            "length": "123",
        },
        {
            "urlkey": "com,example)/",
            "timestamp": "20260102120000",
            "original": "https://example.com",
            "mimetype": "text/html",
            "statuscode": "200",
            "digest": "BBBB",
            "length": "456",
        },
    ]


def test_get_history_adds_archived_urls(monkeypatch):
    monkeypatch.setattr(
        wayback_archive,
        "fetch_text",
        lambda url, timeout=60: "com,example)/ 20260101120000 https://example.com text/html 200 AAAA 123\n",
    )

    result = wayback_archive.get_history("https://example.com")

    assert result == [
        {
            "urlkey": "com,example)/",
            "timestamp": "20260101120000",
            "original": "https://example.com",
            "mimetype": "text/html",
            "statuscode": "200",
            "digest": "AAAA",
            "length": "123",
            "archived_url": "https://web.archive.org/web/20260101120000/https://example.com",
        }
    ]


def test_get_history_retries_retryable_cdx_errors(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    def fake_fetch_text(url, timeout=60):
        calls["count"] += 1
        if calls["count"] < 3:
            raise HTTPError(url, 503, "Service Unavailable", {}, io.BytesIO(b""))
        return "com,example)/ 20260101120000 https://example.com text/html 200 AAAA 123\n"

    monkeypatch.setattr(wayback_archive, "fetch_text", fake_fetch_text)
    monkeypatch.setattr(wayback_archive.time, "sleep", lambda seconds: sleeps.append(seconds))

    result = wayback_archive.get_history("https://example.com")

    assert calls["count"] == 3
    assert sleeps == [2.0, 4.0]
    assert result[0]["timestamp"] == "20260101120000"


def test_save_once_uses_final_redirect_url(monkeypatch):
    def fake_urlopen(request, timeout=60):
        return FakeResponse(url="https://web.archive.org/web/20260702020209/https://example.com/")

    monkeypatch.setattr(wayback_archive.urllib.request, "urlopen", fake_urlopen)

    result = wayback_archive.save_once("https://example.com")

    assert result == {
        "input_url": "https://example.com",
        "archived_url": "https://web.archive.org/web/20260702020209/https://example.com/",
        "timestamp": "20260702020209",
        "source": "save_endpoint",
    }


def test_save_once_uses_http_error_location_header(monkeypatch):
    def fake_urlopen(request, timeout=60):
        raise HTTPError(
            request.full_url,
            302,
            "Found",
            {"Location": "https://web.archive.org/web/20260702020209/https://example.com/"},
            io.BytesIO(b""),
        )

    monkeypatch.setattr(wayback_archive.urllib.request, "urlopen", fake_urlopen)

    result = wayback_archive.save_once("https://example.com")

    assert result["archived_url"] == "https://web.archive.org/web/20260702020209/https://example.com/"
    assert result["source"] == "save_endpoint"


def test_save_url_falls_back_to_availability_api(monkeypatch):
    calls = {"count": 0}

    def fake_save_once(url, timeout=60):
        raise HTTPError(url, 503, "unavailable", {}, io.BytesIO(b""))

    def fake_available(url, timestamp=None, timeout=60):
        calls["count"] += 1
        if calls["count"] < 2:
            return None
        return {
            "input_url": url,
            "archived_url": "https://web.archive.org/web/20260702020209/https://example.com/",
            "timestamp": "20260702020209",
            "status": "200",
            "available": True,
        }

    monkeypatch.setattr(wayback_archive, "save_once", fake_save_once)
    monkeypatch.setattr(wayback_archive, "get_available_snapshot", fake_available)
    monkeypatch.setattr(wayback_archive.time, "sleep", lambda _: None)

    result = wayback_archive.save_url("https://example.com", poll_attempts=3, poll_interval=0)

    assert result["source"] == "availability_api"
    assert result["poll_attempt"] == 2


def test_get_nearest_snapshot_uses_requested_timestamp(monkeypatch):
    monkeypatch.setattr(
        wayback_archive,
        "get_available_snapshot",
        lambda url, timestamp=None, timeout=60: {
            "input_url": url,
            "archived_url": "https://web.archive.org/web/20260101115900/https://example.com/",
            "timestamp": "20260101115900",
            "status": "200",
            "available": True,
        },
    )

    result = wayback_archive.get_nearest_snapshot("https://example.com", "20260101120000")

    assert result["requested_timestamp"] == "20260101120000"
    assert result["timestamp"] == "20260101115900"
    assert result["source"] == "availability_api"


def test_get_nearest_snapshot_falls_back_to_cdx_history(monkeypatch):
    monkeypatch.setattr(wayback_archive, "get_available_snapshot_with_variants", lambda url, timestamp=None, timeout=60: None)
    monkeypatch.setattr(wayback_archive, "get_exact_snapshot_from_cdx", lambda url, timestamp, timeout=60: None)
    monkeypatch.setattr(
        wayback_archive,
        "get_history",
        lambda url, timeout=60: [
            {
                "timestamp": "20251231120000",
                "original": "https://example.com",
                "archived_url": "https://web.archive.org/web/20251231120000/https://example.com",
                "statuscode": "200",
            },
            {
                "timestamp": "20260102120000",
                "original": "https://example.com",
                "archived_url": "https://web.archive.org/web/20260102120000/https://example.com",
                "statuscode": "200",
            },
        ],
    )

    result = wayback_archive.get_nearest_snapshot("https://example.com", "20260101120000")

    assert result["timestamp"] == "20251231120000"
    assert result["source"] == "cdx_api"


def test_get_nearest_snapshot_prefers_exact_cdx_match_before_full_history(monkeypatch):
    monkeypatch.setattr(wayback_archive, "get_available_snapshot_with_variants", lambda url, timestamp=None, timeout=60: None)
    monkeypatch.setattr(
        wayback_archive,
        "get_exact_snapshot_from_cdx",
        lambda url, timestamp, timeout=60: {
            "input_url": "https://example.com",
            "archived_url": "https://web.archive.org/web/20260101115900/https://example.com/",
            "timestamp": "20260101115900",
            "status": "200",
            "available": True,
            "requested_timestamp": timestamp,
            "source": "cdx_api",
        },
    )
    monkeypatch.setattr(
        wayback_archive,
        "get_history",
        lambda url, timeout=60: (_ for _ in ()).throw(AssertionError("full history should not be queried")),
    )

    result = wayback_archive.get_nearest_snapshot("http://example.com", "20260101120000")

    assert result["timestamp"] == "20260101115900"
    assert result["source"] == "cdx_api"


def test_choose_compare_pair_prefers_latest_different_digest():
    entries = [
        {"timestamp": "20260101120000", "digest": "AAAA"},
        {"timestamp": "20260102120000", "digest": "AAAA"},
        {"timestamp": "20260103120000", "digest": "BBBB"},
    ]

    left, right = wayback_archive.choose_compare_pair(entries)

    assert left["timestamp"] == "20260102120000"
    assert right["timestamp"] == "20260103120000"


def test_compare_snapshots_uses_history_when_timestamps_not_supplied(monkeypatch):
    monkeypatch.setattr(
        wayback_archive,
        "get_history",
        lambda url, timeout=60: [
            {
                "timestamp": "20260101120000",
                "archived_url": "https://web.archive.org/web/20260101120000/https://example.com",
                "digest": "AAAA",
                "statuscode": "200",
                "original": "https://example.com",
            },
            {
                "timestamp": "20260102120000",
                "archived_url": "https://web.archive.org/web/20260102120000/https://example.com",
                "digest": "BBBB",
                "statuscode": "200",
                "original": "https://example.com",
            },
        ],
    )

    result = wayback_archive.compare_snapshots("https://example.com")

    assert result["comparison_mode"] == "latest_different_digest"
    assert result["left"]["timestamp"] == "20260101120000"
    assert result["right"]["timestamp"] == "20260102120000"
    assert result["changes_url"] == "https://web.archive.org/web/changes/https://example.com"


def test_compare_snapshots_auto_selection_surfaces_actionable_error(monkeypatch):
    monkeypatch.setattr(
        wayback_archive,
        "get_history",
        lambda url, timeout=60: (_ for _ in ()).throw(
            wayback_archive.WaybackArchiveError(
                "Unable to retrieve snapshot history for https://example.com: CDX endpoint unavailable after 3 attempt(s): HTTP Error 503: Service Unavailable"
            )
        ),
    )

    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.compare_snapshots("https://example.com")

    message = str(exc_info.value)
    assert "auto-select snapshots for comparison" in message
    assert "--from-timestamp" in message
    assert "--to-timestamp" in message


def test_compare_snapshots_uses_nearest_when_both_timestamps_supplied(monkeypatch):
    def fake_nearest(url, timestamp, timeout=60):
        return {
            "input_url": url,
            "archived_url": f"https://web.archive.org/web/{timestamp}/https://example.com/",
            "timestamp": timestamp,
            "status": "200",
            "available": True,
            "requested_timestamp": timestamp,
        }

    monkeypatch.setattr(wayback_archive, "get_nearest_snapshot", fake_nearest)

    result = wayback_archive.compare_snapshots(
        "https://example.com",
        from_timestamp="20260101120000",
        to_timestamp="20260102120000",
    )

    assert result["comparison_mode"] == "nearest_to_requested_timestamps"
    assert result["left"]["timestamp"] == "20260101120000"
    assert result["right"]["timestamp"] == "20260102120000"


def test_resolve_compare_pair_retries_via_cdx_when_availability_collapses(monkeypatch):
    calls = []

    def fake_nearest(url, timestamp, timeout=60, prefer_cdx=False):
        calls.append((timestamp, prefer_cdx))
        if not prefer_cdx:
            return {
                "input_url": url,
                "archived_url": "https://web.archive.org/web/20180427130634/https://example.com/",
                "timestamp": "20180427130634",
                "status": "200",
                "available": True,
                "requested_timestamp": timestamp,
                "source": "availability_api",
            }
        if timestamp == "20180427130634":
            return {
                "input_url": url,
                "archived_url": "https://web.archive.org/web/20180427130634/https://example.com/",
                "timestamp": "20180427130634",
                "status": "200",
                "available": True,
                "requested_timestamp": timestamp,
                "source": "cdx_api",
            }
        return {
            "input_url": url,
            "archived_url": "https://web.archive.org/web/20181115172501/http://example.com:80/",
            "timestamp": "20181115172501",
            "status": "302",
            "available": True,
            "requested_timestamp": timestamp,
            "source": "cdx_api",
        }

    monkeypatch.setattr(wayback_archive, "get_nearest_snapshot", fake_nearest)

    left, right = wayback_archive.resolve_compare_pair(
        "http://example.com/",
        "20180427130634",
        "20181115172501",
    )

    assert left["timestamp"] == "20180427130634"
    assert right["timestamp"] == "20181115172501"
    assert calls == [
        ("20180427130634", False),
        ("20181115172501", False),
        ("20180427130634", True),
        ("20181115172501", True),
    ]


def test_resolve_compare_pair_raises_when_both_timestamps_still_collapse(monkeypatch):
    monkeypatch.setattr(
        wayback_archive,
        "get_nearest_snapshot",
        lambda url, timestamp, timeout=60, prefer_cdx=False: {
            "input_url": url,
            "archived_url": "https://web.archive.org/web/20180427130634/https://example.com/",
            "timestamp": "20180427130634",
            "status": "200",
            "available": True,
            "requested_timestamp": timestamp,
            "source": "cdx_api" if prefer_cdx else "availability_api",
        },
    )

    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.resolve_compare_pair(
            "http://example.com/",
            "20180427130634",
            "20181115172501",
        )

    assert "both resolved to the same snapshot" in str(exc_info.value)


def test_resolve_compare_pair_surfaces_cdx_disambiguation_failure(monkeypatch):
    calls = {"count": 0}

    def fake_nearest(url, timestamp, timeout=60, prefer_cdx=False):
        if not prefer_cdx:
            return {
                "input_url": url,
                "archived_url": "https://web.archive.org/web/20180427130634/https://example.com/",
                "timestamp": "20180427130634",
                "status": "200",
                "available": True,
                "requested_timestamp": timestamp,
                "source": "availability_api",
            }
        calls["count"] += 1
        raise wayback_archive.WaybackArchiveError("CDX endpoint unavailable after 3 attempt(s): HTTP Error 503: Service Unavailable")

    monkeypatch.setattr(wayback_archive, "get_nearest_snapshot", fake_nearest)

    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.resolve_compare_pair(
            "http://example.com/",
            "20180427130634",
            "20181115172501",
        )

    message = str(exc_info.value)
    assert "Availability API resolved both requested timestamps to the same snapshot" in message
    assert "CDX fallback could not disambiguate them" in message
    assert calls["count"] == 1


def test_compare_snapshots_uses_variant_and_exact_cdx_for_explicit_timestamps(monkeypatch):
    def fake_available_variants(url, timestamp=None, timeout=60):
        if timestamp == "20180427130634":
            return {
                "input_url": "https://example.com",
                "archived_url": "https://web.archive.org/web/20180427130634/https://example.com/",
                "timestamp": "20180427130634",
                "status": "200",
                "available": True,
            }
        return None

    def fake_exact_snapshot(url, timestamp, timeout=60):
        if timestamp == "20181115172501":
            return {
                "input_url": "http://example.com:80/",
                "archived_url": "https://web.archive.org/web/20181115172501/http://example.com:80/",
                "timestamp": "20181115172501",
                "status": "302",
                "available": True,
                "requested_timestamp": timestamp,
                "source": "cdx_api",
            }
        return None

    monkeypatch.setattr(wayback_archive, "get_available_snapshot_with_variants", fake_available_variants)
    monkeypatch.setattr(wayback_archive, "get_exact_snapshot_from_cdx", fake_exact_snapshot)
    monkeypatch.setattr(
        wayback_archive,
        "get_history",
        lambda url, timeout=60: (_ for _ in ()).throw(AssertionError("full history should not be queried")),
    )

    result = wayback_archive.compare_snapshots(
        "http://example.com/",
        from_timestamp="20180427130634",
        to_timestamp="20181115172501",
    )

    assert result["left"]["timestamp"] == "20180427130634"
    assert result["right"]["timestamp"] == "20181115172501"
    assert result["right"]["source"] == "cdx_api"


def test_read_url_file_skips_comments_and_blank_lines(tmp_path):
    path = tmp_path / "urls.txt"
    path.write_text(
        "\n# keep this comment\nhttps://example.com\n\nhttps://example.org\n",
        encoding="utf-8",
    )

    assert wayback_archive.read_url_file(path) == [
        "https://example.com",
        "https://example.org",
    ]


def test_read_url_file_raises_structured_error_for_missing_file(tmp_path):
    path = tmp_path / "missing.txt"

    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.read_url_file(path)

    assert "Unable to read URL input file" in str(exc_info.value)


def test_main_compare_requires_both_explicit_timestamps():
    with pytest.raises(wayback_archive.WaybackArchiveError) as exc_info:
        wayback_archive.main(
            [
                "compare",
                "https://example.com",
                "--from-timestamp",
                "20260101120000",
            ]
        )

    assert "requires both --from-timestamp and --to-timestamp together" in str(exc_info.value)
