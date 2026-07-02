from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path
from urllib.error import HTTPError


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
