#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_seed_worker(
    runtime_dir: Path,
    log_path: Path,
    seed_script: Path,
    file_path: Path,
    state_path: Path,
    upload_id: str,
) -> int:
    with log_path.open("a") as log_file:
        result = subprocess.run(
            ["node", str(seed_script), str(file_path), str(state_path), upload_id],
            cwd=str(runtime_dir),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FilePizza tmux worker launcher")
    parser.add_argument("runtime_dir")
    parser.add_argument("log_path")
    parser.add_argument("seed_script")
    parser.add_argument("file_path")
    parser.add_argument("state_path")
    parser.add_argument("upload_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    log_path = Path(args.log_path)
    try:
        return run_seed_worker(
            runtime_dir=Path(args.runtime_dir),
            log_path=log_path,
            seed_script=Path(args.seed_script),
            file_path=Path(args.file_path),
            state_path=Path(args.state_path),
            upload_id=args.upload_id,
        )
    except Exception as exc:
        with log_path.open("a") as log_file:
            print(str(exc), file=log_file)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
