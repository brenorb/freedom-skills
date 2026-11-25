#!/usr/bin/env python3
"""Require nonempty string metadata in changed SKILL.md frontmatter."""

import argparse
from pathlib import PurePosixPath
import subprocess
import sys

import yaml


def metadata_error(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "missing YAML frontmatter"
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return "unterminated YAML frontmatter"
    try:
        header = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return "invalid YAML frontmatter"
    if not isinstance(header, dict):
        return "YAML frontmatter must be a mapping"
    metadata = header.get("metadata")
    if not isinstance(metadata, dict) or not metadata:
        return "metadata must be a non-empty mapping (for example, metadata: {repository: 'https://github.com/owner/repo'})"
    if any(not isinstance(key, str) or not key.strip() or
           not isinstance(value, str) or not value.strip() for key, value in metadata.items()):
        return "metadata keys and values must be non-empty strings; quote version numbers"
    return None


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Validate the index snapshot used by git commit")
    parser.add_argument("--base", help="Base commit for CI range validation")
    parser.add_argument("--head", help="Head commit for CI range validation")
    args = parser.parse_args()
    if (args.base is None) != (args.head is None) or (args.staged and args.base is not None):
        parser.error("use --staged, or both --base and --head")
    try:
        options = ["diff", "--name-only", "--diff-filter=ACMR", "-z"]
        options += [args.base, args.head] if args.base is not None else ["--cached"]
        paths = [p for p in git(*options).decode("utf-8").split("\0")
                 if p and PurePosixPath(p).name == "SKILL.md"]
        errors = []
        for path in paths:
            revision = f"{args.head}:{path}" if args.head is not None else f":{path}"
            error = metadata_error(git("show", revision).decode("utf-8"))
            if error:
                errors.append(f"{path}: {error}")
    except (subprocess.CalledProcessError, UnicodeError):
        print("Cannot read the Git snapshot for SKILL.md metadata validation.", file=sys.stderr)
        return 2
    if errors:
        print("SKILL.md metadata validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(f"OK: metadata in {len(paths)} changed SKILL.md file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
