#!/usr/bin/env python3
"""
Wayback Machine archiving helper.

Usage:
    python3 skills/wayback-archive/scripts/wayback_archive.py save https://example.com
    python3 skills/wayback-archive/scripts/wayback_archive.py available https://example.com
    python3 skills/wayback-archive/scripts/wayback_archive.py history https://example.com
    python3 skills/wayback-archive/scripts/wayback_archive.py nearest https://example.com --timestamp 20260101120000
    python3 skills/wayback-archive/scripts/wayback_archive.py compare https://example.com
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
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError


SAVE_BASE_URL = "https://web.archive.org/save/"
AVAILABLE_API_URL = "https://archive.org/wayback/available?url="
CDX_API_URL = "https://web.archive.org/cdx/search/cdx?url="
WAYBACK_CHANGES_BASE_URL = "https://web.archive.org/web/changes/"
USER_AGENT = "wayback-archive-skill/1.0"
DEFAULT_TIMEOUT = 60
DEFAULT_POLL_ATTEMPTS = 6
DEFAULT_POLL_INTERVAL = 5.0
CDX_RETRY_ATTEMPTS = 3
CDX_RETRY_BACKOFF_SECONDS = 2.0
TIMESTAMP_RE = re.compile(r"/web/(\d{14})/")
CDX_FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]


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


def build_cdx_url(
    url: str,
    *,
    limit: int | None = None,
    from_timestamp: str | None = None,
    to_timestamp: str | None = None,
) -> str:
    query = CDX_API_URL + urllib.parse.quote(url, safe="")
    if limit is not None:
        query += "&limit=" + urllib.parse.quote(str(limit), safe="")
    if from_timestamp:
        query += "&from=" + urllib.parse.quote(from_timestamp, safe="")
    if to_timestamp:
        query += "&to=" + urllib.parse.quote(to_timestamp, safe="")
    return query


def build_changes_url(url: str) -> str:
    return WAYBACK_CHANGES_BASE_URL + quote_target(url)


def build_snapshot_url(url: str, timestamp: str) -> str:
    return f"https://web.archive.org/web/{timestamp}/{url}"


def extract_timestamp(archived_url: str | None) -> str | None:
    if not archived_url:
        return None
    match = TIMESTAMP_RE.search(archived_url)
    return match.group(1) if match else None


def parse_wayback_timestamp(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y%m%d%H%M%S")


def is_retryable_cdx_error(exc: Exception) -> bool:
    if isinstance(exc, HTTPError):
        return 500 <= exc.code < 600
    return isinstance(exc, (URLError, TimeoutError))


def fetch_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def parse_cdx_response(text: str) -> list[dict]:
    entries = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(" ")
        if len(parts) < len(CDX_FIELDS):
            continue
        values = parts[: len(CDX_FIELDS)]
        entry = dict(zip(CDX_FIELDS, values, strict=True))
        entries.append(entry)
    return entries


def get_history(
    url: str,
    *,
    limit: int | None = None,
    from_timestamp: str | None = None,
    to_timestamp: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[dict]:
    cdx_url = build_cdx_url(
        url,
        limit=limit,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
    )
    last_exc: Exception | None = None
    for attempt in range(CDX_RETRY_ATTEMPTS):
        try:
            text = fetch_text(cdx_url, timeout=timeout)
            break
        except (HTTPError, URLError, TimeoutError) as exc:
            last_exc = exc
            if not is_retryable_cdx_error(exc) or attempt + 1 >= CDX_RETRY_ATTEMPTS:
                raise WaybackArchiveError(
                    f"Unable to retrieve snapshot history for {url}: CDX endpoint unavailable after {attempt + 1} attempt(s): {exc}"
                ) from exc
            time.sleep(CDX_RETRY_BACKOFF_SECONDS * (attempt + 1))
    else:  # pragma: no cover
        raise WaybackArchiveError(f"Unable to retrieve snapshot history for {url}: {last_exc}")
    entries = parse_cdx_response(text)
    for entry in entries:
        entry["archived_url"] = build_snapshot_url(entry["original"], entry["timestamp"])
    return entries


def get_available_snapshot(url: str, timestamp: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict | None:
    try:
        payload = fetch_json(build_available_url(url, timestamp=timestamp), timeout=timeout)
    except (HTTPError, URLError):
        return None
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


def find_nearest_in_history(entries: list[dict], requested_timestamp: str) -> dict:
    if not entries:
        raise WaybackArchiveError("No archived snapshots available")

    requested_dt = parse_wayback_timestamp(requested_timestamp)

    def distance(entry: dict) -> tuple[float, datetime]:
        entry_dt = parse_wayback_timestamp(entry["timestamp"])
        return (abs((entry_dt - requested_dt).total_seconds()), entry_dt)

    best = min(entries, key=distance)
    return {
        "input_url": best["original"],
        "archived_url": best["archived_url"],
        "timestamp": best["timestamp"],
        "status": best.get("statuscode"),
        "available": True,
    }


def get_nearest_snapshot(url: str, timestamp: str, *, timeout: int = DEFAULT_TIMEOUT) -> dict:
    snapshot = get_available_snapshot(url, timestamp=timestamp, timeout=timeout)
    if snapshot:
        snapshot["requested_timestamp"] = timestamp
        snapshot["source"] = "availability_api"
        return snapshot

    history = get_history(url, timeout=timeout)
    if not history:
        raise WaybackArchiveError(f"Unable to find a snapshot near {timestamp} for {url}")
    snapshot = find_nearest_in_history(history, timestamp)
    snapshot["requested_timestamp"] = timestamp
    snapshot["source"] = "cdx_api"
    return snapshot


def choose_compare_pair(entries: list[dict]) -> tuple[dict, dict]:
    if len(entries) < 2:
        raise WaybackArchiveError("compare requires at least two archived snapshots")

    latest = entries[-1]
    for candidate in reversed(entries[:-1]):
        if candidate.get("digest") != latest.get("digest"):
            return candidate, latest

    return entries[-2], latest


def compare_snapshots(
    url: str,
    *,
    from_timestamp: str | None = None,
    to_timestamp: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    if from_timestamp and to_timestamp:
        left = get_nearest_snapshot(url, from_timestamp, timeout=timeout)
        right = get_nearest_snapshot(url, to_timestamp, timeout=timeout)
        return {
            "input_url": url,
            "comparison_mode": "nearest_to_requested_timestamps",
            "changes_url": build_changes_url(url),
            "left": left,
            "right": right,
        }

    try:
        history = get_history(url, timeout=timeout)
    except WaybackArchiveError as exc:
        raise WaybackArchiveError(
            f"Unable to auto-select snapshots for comparison for {url}: {exc}. Try again later or rerun compare with --from-timestamp and --to-timestamp."
        ) from exc
    left, right = choose_compare_pair(history)
    return {
        "input_url": url,
        "comparison_mode": "latest_different_digest" if left.get("digest") != right.get("digest") else "latest_two_snapshots",
        "changes_url": build_changes_url(url),
        "left": {
            "timestamp": left["timestamp"],
            "archived_url": left["archived_url"],
            "digest": left.get("digest"),
            "status": left.get("statuscode"),
            "original": left.get("original"),
        },
        "right": {
            "timestamp": right["timestamp"],
            "archived_url": right["archived_url"],
            "digest": right.get("digest"),
            "status": right.get("statuscode"),
            "original": right.get("original"),
        },
        "history_count": len(history),
    }


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

    history_parser = subparsers.add_parser("history", help="List archived snapshots for a URL.")
    history_parser.add_argument("url")
    history_parser.add_argument("--limit", type=int)
    history_parser.add_argument("--from-timestamp")
    history_parser.add_argument("--to-timestamp")
    history_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)

    nearest_parser = subparsers.add_parser(
        "nearest",
        aliases=["at"],
        help="Find the snapshot nearest a requested timestamp.",
    )
    nearest_parser.add_argument("url")
    nearest_parser.add_argument("--timestamp", required=True)
    nearest_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)

    compare_parser = subparsers.add_parser("compare", help="Select two snapshots to compare.")
    compare_parser.add_argument("url")
    compare_parser.add_argument("--from-timestamp")
    compare_parser.add_argument("--to-timestamp")
    compare_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)

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

    if args.command == "history":
        entries = get_history(
            args.url,
            limit=args.limit,
            from_timestamp=args.from_timestamp,
            to_timestamp=args.to_timestamp,
            timeout=args.timeout,
        )
        payload = {
            "mode": "history",
            "input_url": args.url,
            "count": len(entries),
            "snapshots": entries,
        }
        json_dump(payload)
        return 0

    if args.command in {"nearest", "at"}:
        snapshot = get_nearest_snapshot(args.url, args.timestamp, timeout=args.timeout)
        payload = {
            "mode": "nearest",
            "input_url": args.url,
            "snapshot": snapshot,
        }
        json_dump(payload)
        return 0

    if args.command == "compare":
        payload = compare_snapshots(
            args.url,
            from_timestamp=args.from_timestamp,
            to_timestamp=args.to_timestamp,
            timeout=args.timeout,
        )
        payload["mode"] = "compare"
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
