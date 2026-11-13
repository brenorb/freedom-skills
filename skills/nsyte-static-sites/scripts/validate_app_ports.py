#!/usr/bin/env python3
"""Check literal endpoint evidence in a static build; never execute site code."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


def validate(build, blossom=False, no_relay=False):
    if not build.is_dir() or not (build / "index.html").is_file():
        raise ValueError("Expected a build directory containing index.html")
    evidence = {"relay": [], "blossom": []}
    errors = []
    http_candidates = []
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
                    actual = port if port is not None else (443 if url.scheme == "wss" else 80)
                    errors.append(f"{location}: WebSocket uses port {actual}; expected 4870. "
                                  "Configure a reachable relay on 4870 and rebuild.")
            else:
                actual = port if port is not None else (443 if url.scheme == "https" else 80)
                http_candidates.append(f"{location} (port {actual})")
                if port == 24243:
                    evidence["blossom"].append(location)
    if not evidence["relay"] and not no_relay:
        errors.append("No literal ws/wss endpoint on port 4870 found. Configure the runtime relay "
                      "and rebuild; use --no-relay only if the app has no relay functionality.")
    if blossom and not evidence["blossom"]:
        observed = ", ".join(http_candidates) or "none"
        errors.append("Blossom requires port 24243; no matching literal endpoint found. "
                      f"HTTP(S) candidates (not necessarily Blossom): {observed}. "
                      "Configure a reachable Blossom service on 24243 and rebuild. "
                      "Port 443 is not a substitute. Keep --blossom while the app uses Blossom.")
    return {"ok": not errors, "evidence": evidence, "errors": errors,
            "next_action": ("STOP: do not deploy. Fix the errors and rerun with the same required flags. "
                            "For computed URLs, verify the actual runtime port manually. "
                            "If the required service is unavailable, report that blocker; "
                            "do not remove flags or add unused URLs to pass."
                            if errors else "Verify actual runtime connections before deployment."),
            "scope": "Static URL evidence only: verify actual connections in the browser. "
                     "All literal WebSocket URLs are treated as relay candidates. "
                     "HTTP URLs cannot be classified as Blossom automatically."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--blossom", action="store_true", help="Require a Blossom endpoint on port 24243")
    parser.add_argument("--no-relay", action="store_true", help="App has no relay functionality; still inspect any literal WebSocket URLs")
    args = parser.parse_args()
    try:
        result = validate(args.build, args.blossom, args.no_relay)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Cannot validate build: {error}\n")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
