---
name: wayback-archive
description: Use this skill when the user wants to archive a live webpage in the Internet Archive Wayback Machine, get a stable citation URL for a page that may change or disappear, check whether a URL is already archived, or batch-save a list of URLs with a local command-line wrapper.
---

# wayback-archive

Use the bundled wrapper around the Internet Archive Wayback Machine to save a live URL, check whether a URL already has a snapshot, or batch-save a list of URLs.

## Default workflow

1. Save a single live page:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py save https://example.com/article
```

2. Read the JSON result:
- `archived_url` is the permanent Wayback snapshot URL.
- `timestamp` is the 14-digit Wayback capture timestamp when available.
- `source` shows whether the result came directly from the save endpoint or from the availability lookup fallback.
- If the goal is simply to obtain a stable archived URL, an existing snapshot returned by the availability fallback is acceptable.
- If the goal is to force a fresh capture now, inspect `timestamp` and do not assume `save` created a new snapshot unless the returned time is actually new.

3. Check whether a URL is already archived without submitting a new save:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py available https://example.com/article
```

4. If the user has a file with one URL per line, batch-save it:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py batch-save \
  --input /absolute/path/to/urls.txt
```

5. If the user wants the snapshot history for one URL:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py history https://example.com/article
```

6. If the user wants the snapshot nearest a specific date or time:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py nearest \
  https://example.com/article \
  --timestamp 20260101120000
```

7. If the user wants two snapshots selected for comparison:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py compare https://example.com/article
```

8. If the user already knows the two times they care about, compare the nearest snapshots to those requested timestamps:

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py compare \
  https://example.com/article \
  --from-timestamp 20260101120000 \
  --to-timestamp 20260201120000
```

## Defaults

- Prefer the bundled wrapper over handwritten `curl` because it handles redirects, structured JSON output, and a retry path through the official availability API.
- Prefer Wayback Machine for programmatic archiving by default.
- Prefer `available` when the user only wants to inspect archive state and has not asked to create a new snapshot.
- Prefer `history` when the user wants a timeline of revisions.
- Prefer `nearest` or its alias `at` when the user is asking for the version closest to a known date.
- Prefer `compare` when the user wants to inspect how a page changed over time.
- Prefer batch-save from a file when the user gives a long URL list.

## Safety rules

- Treat `save` and `batch-save` as external network actions because they submit URLs to the Internet Archive.
- Call out that the save flow archives a single page, not a whole site crawl.
- Do not claim that a newly submitted page is instantly visible in all query surfaces; the wrapper may need to poll the availability API briefly.
- If the user explicitly asks for `archive.is` or `archive.today`, note that those services do not provide a stable public write API for automated submission and may require CAPTCHA; use Wayback unless the user explicitly wants the brittle path.

## Gotchas

- The official lookup API is `https://archive.org/wayback/available?url=...`.
- The CDX API is `https://web.archive.org/cdx/search/cdx?url=...` and exposes snapshot rows with fields such as `timestamp`, `original`, `statuscode`, and `digest`.
- The save path is `https://web.archive.org/save/<url>` and commonly answers with a redirect to the archived snapshot.
- `compare` returns a `changes_url` for the built-in Wayback comparison UI and also returns two concrete snapshot URLs.
- Raw save example: `curl -I "https://web.archive.org/save/https://example.com"`.
- Raw availability example: `curl "https://archive.org/wayback/available?url=https://example.com"`.
- Raw history example: `curl "https://web.archive.org/cdx/search/cdx?url=https://example.com"`.
- Some sites still fail to archive because of crawler, SSL, or server-side restrictions.
- A returned archive URL can point to an existing close snapshot when the save fallback path is used after a save attempt fails.
- This skill treats `save` as successful when it can return a usable archived snapshot, even if that snapshot already existed before the current request.
