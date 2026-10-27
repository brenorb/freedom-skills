"""Build only runtime skill files; eval answers stay in the parent checkout.

This is a packaging boundary, not an operating-system or network sandbox.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

RUNTIME_DIRS = ('scripts', 'references', 'assets', 'agents')


def runtime_files(source):
    source = Path(source).resolve()
    entry = source / 'SKILL.md'
    if entry.is_symlink() or not entry.is_file():
        raise ValueError('A regular SKILL.md is required')
    files = [entry]
    for name in RUNTIME_DIRS:
        folder = source / name
        if folder.is_symlink():
            raise ValueError('Runtime symlinks are not supported: ' + name)
        if not folder.exists():
            continue
        if not folder.is_dir():
            raise ValueError('Runtime resource must be a directory: ' + name)
        for path in sorted(folder.rglob('*')):
            if path.is_symlink():
                raise ValueError('Runtime symlinks are not supported: ' + str(path))
            if '__pycache__' in path.parts or path.suffix in ('.pyc', '.pyo'):
                continue
            if path.is_file():
                files.append(path)
    return source, files


def build(source, destination):
    source, files = runtime_files(source)
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('Destination must not exist; never overwrite a previous package')
    if destination.resolve().is_relative_to(source):
        raise ValueError('Destination must be outside the source skill')
    if not destination.parent.is_dir():
        raise ValueError('Destination parent must exist')
    with tempfile.TemporaryDirectory(prefix='.skill-package-', dir=destination.parent) as temporary:
        staging = Path(temporary) / 'skill'
        staging.mkdir()
        hashes = {}
        for path in files:
            relative = path.relative_to(source)
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            shutil.copymode(path, target)
            hashes[relative.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
        destination.mkdir()  # Reserve without replacing a concurrently created directory.
        for child in staging.iterdir():
            child.rename(destination / child.name)
    return {'files': hashes, 'excluded_root_categories': ['evals', 'benchmarks', 'tests'],
            'limit': 'Runtime allowlist only; callers must enforce filesystem/network isolation separately.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.destination), indent=2))


if __name__ == '__main__':
    main()
