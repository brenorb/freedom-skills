#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_DIR = Path.home() / ".cache" / "freedom-skills" / "bitcoin-pir-upstream"
UPSTREAM_REPO_URL = "https://github.com/Bitcoin-PIR/Bitcoin-PIR.git"
ADDRESS_HEADER = "=== Address \u2192 PIR script hash (HASH160(scriptPubKey)) ==="
TXID_RE = re.compile(r"^[0-9a-fA-F]{64}$")
OUTPOINT_RE = re.compile(r"^[0-9a-fA-F]{64}:\d+$")
XPUB_RE = re.compile(r"^(xpub|ypub|zpub|tpub|upub|vpub)[A-Za-z0-9]+$")
CATALOG_LINE_RE = re.compile(
    r"^\s+\[(?P<db_id>\d+)\] (?P<name>\S+) (?P<kind>.+?) "
    r"height=(?P<height>\d+) index_bins=(?P<index_bins>\d+) chunk_bins=(?P<chunk_bins>\d+)$"
)
RESULT_HEADER_RE = re.compile(r"^=== (?P<address>.+) \((?P<script_hash>[0-9a-f]{40})\) ===$")
UTXO_LINE_RE = re.compile(
    r"^\s{4}(?P<txid>[0-9a-f]{64}):(?P<vout>\d+) = (?P<amount>\d+) sats$"
)


class QueryAddressesError(RuntimeError):
    pass


def run(cmd: list[str], *, cwd: Path | None = None, description: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise QueryAddressesError(f"{description} failed with exit code {result.returncode}: {detail}")
    return result


def ensure_repo(repo_dir: Path) -> Path:
    manifest_path = repo_dir / "Cargo.toml"
    example_path = repo_dir / "pir-sdk-client" / "examples" / "fetch_addresses.rs"
    if manifest_path.exists() and example_path.exists():
        return repo_dir

    if repo_dir.exists():
        raise QueryAddressesError(
            f"upstream repo path exists but does not look like Bitcoin-PIR: {repo_dir}"
        )

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    run(
        ["git", "clone", "--depth", "1", UPSTREAM_REPO_URL, str(repo_dir)],
        description=f"cloning {UPSTREAM_REPO_URL}",
    )
    return repo_dir


def find_unsupported_queries(values: list[str]) -> list[str]:
    unsupported = []
    for value in values:
        candidate = value.strip()
        if TXID_RE.fullmatch(candidate) or OUTPOINT_RE.fullmatch(candidate) or XPUB_RE.fullmatch(candidate):
            unsupported.append(candidate)
    return unsupported


def _coerce_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise QueryAddressesError(f"expected boolean value, got {value!r}")


def parse_fetch_addresses_output(stdout: str) -> dict:
    lines = stdout.splitlines()
    try:
        start = lines.index(ADDRESS_HEADER)
    except ValueError as exc:
        raise QueryAddressesError("upstream output did not contain the expected address header") from exc

    i = start + 1
    addresses: list[dict] = []
    while i < len(lines):
        line = lines[i]
        if line.startswith("Connecting:"):
            break
        if not line.strip():
            i += 1
            continue
        if i + 2 >= len(lines):
            raise QueryAddressesError("truncated address preamble in upstream output")
        address = line.strip()
        spk_line = lines[i + 1].strip()
        sh_line = lines[i + 2].strip()
        if not spk_line.startswith("scriptPubKey : "):
            raise QueryAddressesError(f"unexpected scriptPubKey line: {lines[i + 1]!r}")
        if not sh_line.startswith("script_hash  : "):
            raise QueryAddressesError(f"unexpected script_hash line: {lines[i + 2]!r}")
        addresses.append(
            {
                "address": address,
                "script_pubkey": spk_line.split(":", 1)[1].strip(),
                "script_hash": sh_line.split(":", 1)[1].strip(),
            }
        )
        i += 3

    if i >= len(lines) or not lines[i].startswith("Connecting:"):
        raise QueryAddressesError("upstream output did not include the connection line")

    connection_line = lines[i]
    _, servers = connection_line.split("Connecting:", 1)
    server_parts = [part.strip() for part in re.split(r"\s+/\s+", servers.strip()) if part.strip()]
    i += 1

    while i < len(lines) and not lines[i].startswith("Catalog:"):
        i += 1
    if i >= len(lines):
        raise QueryAddressesError("upstream output did not include the catalog section")

    catalog_header = lines[i]
    match = re.match(r"^Catalog: (?P<count>\d+) database\(s\):$", catalog_header)
    if not match:
        raise QueryAddressesError(f"unexpected catalog header: {catalog_header!r}")
    catalog_count = int(match.group("count"))
    i += 1

    catalog = []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            break
        match = CATALOG_LINE_RE.match(line)
        if not match:
            raise QueryAddressesError(f"unexpected catalog line: {line!r}")
        catalog.append(
            {
                "db_id": int(match.group("db_id")),
                "name": match.group("name"),
                "kind": match.group("kind"),
                "height": int(match.group("height")),
                "index_bins": int(match.group("index_bins")),
                "chunk_bins": int(match.group("chunk_bins")),
            }
        )
        i += 1

    while i < len(lines) and not lines[i].startswith("Synced to height "):
        i += 1
    if i >= len(lines):
        raise QueryAddressesError("upstream output did not include the synced height")
    synced_height = int(lines[i].split()[-1])
    i += 1

    results_by_address = {}
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        header_match = RESULT_HEADER_RE.match(line)
        if not header_match:
            raise QueryAddressesError(f"unexpected result header: {line!r}")

        address = header_match.group("address")
        result = {
            "address": address,
            "script_hash": header_match.group("script_hash"),
            "found": True,
            "merkle_verified": None,
            "is_whale": None,
            "utxo_count": 0,
            "total_balance_sats": 0,
            "utxos": [],
        }
        i += 1

        while i < len(lines) and lines[i].strip():
            row = lines[i]
            stripped = row.strip()
            if stripped == "(not found)":
                result["found"] = False
                i += 1
                break
            if stripped.startswith("merkle_verified : "):
                result["merkle_verified"] = _coerce_bool(stripped.split(":", 1)[1])
            elif stripped.startswith("is_whale        : "):
                result["is_whale"] = _coerce_bool(stripped.split(":", 1)[1])
            elif stripped.startswith("UTXO count      : "):
                result["utxo_count"] = int(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("total balance   : "):
                amount_text = stripped.split(":", 1)[1].strip()
                result["total_balance_sats"] = int(amount_text.removesuffix(" sats"))
            else:
                utxo_match = UTXO_LINE_RE.match(row)
                if not utxo_match:
                    raise QueryAddressesError(f"unexpected result line: {row!r}")
                result["utxos"].append(
                    {
                        "txid": utxo_match.group("txid"),
                        "vout": int(utxo_match.group("vout")),
                        "amount_sats": int(utxo_match.group("amount")),
                    }
                )
            i += 1

        results_by_address[address] = result

    queries = []
    for entry in addresses:
        merged = dict(entry)
        merged.update(results_by_address.get(entry["address"], {"found": False}))
        queries.append(merged)

    return {
        "ok": True,
        "repo_dir": str(DEFAULT_REPO_DIR),
        "servers": server_parts,
        "catalog_count": catalog_count,
        "catalog": catalog,
        "synced_height": synced_height,
        "queries": queries,
    }


def build_error_payload(message: str, unsupported: list[str]) -> dict:
    return {
        "ok": False,
        "error": "unsupported_lookup",
        "message": message,
        "unsupported": unsupported,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query current Bitcoin address UTXOs through the public Bitcoin PIR demo."
    )
    parser.add_argument("queries", nargs="+", help="One or more Bitcoin addresses")
    parser.add_argument(
        "--upstream-dir",
        default=str(DEFAULT_REPO_DIR),
        help=f"Path to the local Bitcoin-PIR clone (default: {DEFAULT_REPO_DIR})",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw upstream example output instead of parsed JSON",
    )
    args = parser.parse_args()

    unsupported = find_unsupported_queries(args.queries)
    if unsupported:
        payload = build_error_payload(
            "Bitcoin PIR currently supports address-to-current-UTXO lookups here, not standalone txid, outpoint, or xpub lookups.",
            unsupported,
        )
        print(json.dumps(payload, indent=2))
        return 2

    repo_dir = ensure_repo(Path(args.upstream_dir).expanduser().resolve())
    result = run(
        [
            "cargo",
            "run",
            "--release",
            "-p",
            "pir-sdk-client",
            "--example",
            "fetch_addresses",
            "--manifest-path",
            str(repo_dir / "Cargo.toml"),
            "--",
            *args.queries,
        ],
        cwd=repo_dir,
        description="running upstream fetch_addresses example",
    )

    if args.raw:
        sys.stdout.write(result.stdout)
        return 0

    payload = parse_fetch_addresses_output(result.stdout)
    payload["repo_dir"] = str(repo_dir)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QueryAddressesError as exc:
        print(json.dumps({"ok": False, "error": "runtime_error", "message": str(exc)}, indent=2))
        raise SystemExit(1)
