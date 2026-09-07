#!/usr/bin/env python3
"""Check literal endpoint evidence in a static build; never execute site code."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


def validate(build, blossom=False):
    if not build.is_dir() or not (build / "index.html").is_file():
        raise ValueError("Expected a build directory containing index.html")
    evidence = {"relay": [], "blossom": []}
    errors = []
    # Literal scanning cannot determine which code runs or resolve computed URLs.
    pattern = re.compile(r'''(?:wss?|https?)://[^\s\"'`<>\\]+''')
    for path in sorted(build.rglob("*")):
        if path.is_symlink():
            raise ValueError("Build contains a symlink; validate a self-contained build")
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".mjs", ".json"}:
            continue
        if any(part.startswith(".") for part in path.relative_to(build).parts):
            continue
        source = path.read_text(encoding="utf-8").replace(r"\/", "/")
        for match in pattern.finditer(source):
            raw = match.group().rstrip(");,}")
            location = f"{path.relative_to(build)}:{source.count(chr(10), 0, match.start()) + 1}"
            try:
                url = urlsplit(raw)
                port = url.port
                if not url.hostname:
                    raise ValueError("missing host")
            except ValueError:
                errors.append(f"{location}: unresolved or malformed URL; inspect manually")
                continue
            if url.scheme in {"ws", "wss"}:
                if port == 4870:
                    evidence["relay"].append(location)
                else:
                    errors.append(f"{location}: WebSocket URL does not use port 4870")
            elif port == 24243:
                evidence["blossom"].append(location)
    if not evidence["relay"]:
        errors.append("No literal ws/wss endpoint on port 4870 found")
    if blossom and not evidence["blossom"]:
        errors.append("Blossom requested: no literal http/https endpoint on port 24243 found")
    return {"ok": not errors, "evidence": evidence, "errors": errors,
            "scope": "Static URL evidence only: verify actual connections in the browser. "
                     "All literal WebSocket URLs are treated as relay candidates. "
                     "HTTP URLs cannot be classified as Blossom automatically."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--blossom", action="store_true", help="Require a Blossom endpoint on port 24243")
    args = parser.parse_args()
    try:
        result = validate(args.build, args.blossom)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Cannot validate build: {error}\n")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
