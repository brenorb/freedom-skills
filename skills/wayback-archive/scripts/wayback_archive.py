#!/usr/bin/env python3
"""
Wayback Machine archiving helper.

Usage:
    python3 skills/wayback-archive/scripts/wayback_archive.py save https://example.com
    python3 skills/wayback-archive/scripts/wayback_archive.py available https://example.com
    python3 skills/wayback-archive/scripts/wayback_archive.py batch-save --input /tmp/urls.txt

All output is structured JSON. No dependencies beyond Python stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError


SAVE_BASE_URL = "https://web.archive.org/save/"
AVAILABLE_API_URL = "https://archive.org/wayback/available?url="
USER_AGENT = "wayback-archive-skill/1.0"
DEFAULT_TIMEOUT = 60
DEFAULT_POLL_ATTEMPTS = 6
DEFAULT_POLL_INTERVAL = 5.0
TIMESTAMP_RE = re.compile(r"/web/(\d{14})/")


class WaybackArchiveError(RuntimeError):
    """Raised when the wrapper cannot get a usable archive result."""


def json_dump(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def quote_target(url: str) -> str:
    return urllib.parse.quote(url, safe=":/?&=#%")


def build_save_url(url: str) -> str:
    return SAVE_BASE_URL + quote_target(url)


def build_available_url(url: str, timestamp: str | None = None) -> str:
    query = AVAILABLE_API_URL + urllib.parse.quote(url, safe="")
    if timestamp:
        query += "&timestamp=" + urllib.parse.quote(timestamp, safe="")
    return query


def extract_timestamp(archived_url: str | None) -> str | None:
    if not archived_url:
        return None
    match = TIMESTAMP_RE.search(archived_url)
    return match.group(1) if match else None


def fetch_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_available_snapshot(url: str, timestamp: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict | None:
    payload = fetch_json(build_available_url(url, timestamp=timestamp), timeout=timeout)
    closest = payload.get("archived_snapshots", {}).get("closest")
    if not closest or not closest.get("available") or not closest.get("url"):
        return None
    return {
        "input_url": url,
        "archived_url": closest["url"],
        "timestamp": closest.get("timestamp") or extract_timestamp(closest["url"]),
        "status": closest.get("status"),
        "available": True,
    }


def save_once(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict | None:
    request = urllib.request.Request(
        build_save_url(url),
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            archived_url = response.geturl()
            if "/web/" not in archived_url:
                return None
            return {
                "input_url": url,
                "archived_url": archived_url,
                "timestamp": extract_timestamp(archived_url),
                "source": "save_endpoint",
            }
    except HTTPError as exc:
        location = exc.headers.get("Location")
        if location and "/web/" in location:
            return {
                "input_url": url,
                "archived_url": location,
                "timestamp": extract_timestamp(location),
                "source": "save_endpoint",
            }
        raise


def save_url(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    poll_attempts: int = DEFAULT_POLL_ATTEMPTS,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> dict:
    try:
        direct = save_once(url, timeout=timeout)
    except (HTTPError, URLError):
        direct = None

    if direct:
        return direct

    for attempt in range(poll_attempts):
        snapshot = get_available_snapshot(url, timeout=timeout)
        if snapshot:
            snapshot["source"] = "availability_api"
            snapshot["poll_attempt"] = attempt + 1
            return snapshot
        if attempt + 1 < poll_attempts:
            time.sleep(poll_interval)

    raise WaybackArchiveError(f"Unable to obtain an archived snapshot for {url}")


def batch_save(
    urls: list[str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    poll_attempts: int = DEFAULT_POLL_ATTEMPTS,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> dict:
    results = []
    for url in urls:
        try:
            results.append(
                {
                    "input_url": url,
                    "result": save_url(
                        url,
                        timeout=timeout,
                        poll_attempts=poll_attempts,
                        poll_interval=poll_interval,
                    ),
                }
            )
        except Exception as exc:  # pragma: no cover - covered by result shape assertions
            results.append(
                {
                    "input_url": url,
                    "error": str(exc),
                }
            )
    return {"mode": "batch-save", "total": len(urls), "results": results}


def read_url_file(path: Path) -> list[str]:
    urls = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive webpages in Wayback Machine.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save_parser = subparsers.add_parser("save", help="Save one live URL in Wayback Machine.")
    save_parser.add_argument("url")
    save_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    save_parser.add_argument("--poll-attempts", type=int, default=DEFAULT_POLL_ATTEMPTS)
    save_parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)

    available_parser = subparsers.add_parser("available", help="Check whether a URL is archived.")
    available_parser.add_argument("url")
    available_parser.add_argument("--timestamp")
    available_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)

    batch_parser = subparsers.add_parser("batch-save", help="Save multiple URLs.")
    batch_parser.add_argument("urls", nargs="*")
    batch_parser.add_argument("--input", type=Path)
    batch_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    batch_parser.add_argument("--poll-attempts", type=int, default=DEFAULT_POLL_ATTEMPTS)
    batch_parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.command == "save":
        payload = save_url(
            args.url,
            timeout=args.timeout,
            poll_attempts=args.poll_attempts,
            poll_interval=args.poll_interval,
        )
        payload["mode"] = "save"
        json_dump(payload)
        return 0

    if args.command == "available":
        snapshot = get_available_snapshot(args.url, timestamp=args.timestamp, timeout=args.timeout)
        payload = {
            "mode": "available",
            "input_url": args.url,
            "available": bool(snapshot),
            "snapshot": snapshot,
        }
        json_dump(payload)
        return 0

    if args.command == "batch-save":
        urls = list(args.urls)
        if args.input:
            urls.extend(read_url_file(args.input))
        urls = list(dict.fromkeys(urls))
        if not urls:
            raise WaybackArchiveError("batch-save requires at least one URL or --input")
        payload = batch_save(
            urls,
            timeout=args.timeout,
            poll_attempts=args.poll_attempts,
            poll_interval=args.poll_interval,
        )
        json_dump(payload)
        return 0

    raise WaybackArchiveError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WaybackArchiveError as exc:
        json_dump({"error": str(exc)})
        raise SystemExit(1)
