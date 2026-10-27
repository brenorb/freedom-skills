"""Create and verify local evidence archives without rewriting legacy studies.

Never follow symlinks or include CLI auth state, caches, copied executables or
sealed final data. Originals remain in place. No uploads or deletion occur.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile

INVENTORY = '_archive_inventory.json'
PRIVATE_COMPONENTS = {'.venv', 'node_modules', '__pycache__', 'codex-state', 'claude-state',
                      'omp-state', '.locks', 'locks', '.git'}


def omitted(relative):
    parts = relative.parts
    if any(part in PRIVATE_COMPONENTS for part in parts):
        return 'auth-state-or-cache'
    if relative.name.endswith(('.pyc', '.pyo')) or relative.name == '.refresh.lock':
        return 'transient'
    if parts[:2] == ('toolchain', 'bin') or ('workspace' in parts and 'bin' in parts[parts.index('workspace') + 1:]):
        return 'reproducible-executables'
    if 'fixtures-final' in parts or relative.name == 'sealed-final.json' or relative.name.startswith('fresh-'):
        return 'sealed-final-data'
    return None


def files_under(root):
    """Walk without following directory symlinks, recording each omitted boundary."""
    included, excluded = [], []
    def walk(folder):
        for path in sorted(folder.iterdir()):
            relative = path.relative_to(root)
            reason = omitted(relative)
            if path.is_symlink():
                reason = 'symlink-not-followed'
            if reason:
                excluded.append({'path': relative.as_posix(), 'reason': reason})
            elif path.is_dir():
                walk(path)
            elif path.is_file():
                included.append(path)
            else:
                excluded.append({'path': relative.as_posix(), 'reason': 'non-regular-file'})
    walk(root)
    return included, excluded


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def create(source, destination):
    if Path(source).is_symlink():
        raise ValueError('Source must not be a symlink')
    source = Path(source).resolve()
    destination = Path(destination).absolute()
    if not source.is_dir() or source.is_symlink():
        raise ValueError('Source must be a study directory')
    if destination.exists() or destination.is_symlink():
        raise ValueError('Archive already exists; never overwrite evidence')
    if destination.resolve().is_relative_to(source):
        raise ValueError('Archive must be outside its source study')
    if not destination.parent.is_dir():
        raise ValueError('Archive parent must exist')
    paths, excluded = files_under(source)
    if (source / INVENTORY).exists():
        raise ValueError('Reserved archive inventory name exists in source')
    inventory = {'schema_version': 1, 'study_id': source.name, 'files': {}, 'excluded': excluded,
                 'policy': 'Filtered local archive; originals retained. Sealed final data/auth state are not exported.'}
    with tempfile.TemporaryDirectory(prefix='.evidence-', dir=destination.parent) as folder:
        temporary = Path(folder) / 'evidence.tar.gz'
        with tarfile.open(temporary, 'w:gz') as archive:
            for path in paths:
                before = path.stat()
                data = path.read_bytes()
                after = path.stat()
                if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
                    raise ValueError('Source changed while archiving: ' + str(path))
                relative = path.relative_to(source).as_posix()
                inventory['files'][relative] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
                entry = tarfile.TarInfo(relative)
                entry.size, entry.mode, entry.mtime = len(data), before.st_mode & 0o777, int(before.st_mtime)
                archive.addfile(entry, io.BytesIO(data))
            data = (json.dumps(inventory, indent=2) + '\n').encode()
            entry = tarfile.TarInfo(INVENTORY)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
        verify(temporary)
        # A hard-link publish refuses a destination created concurrently.
        import os
        os.link(temporary, destination)
    reasons = {}
    for item in excluded:
        reasons[item['reason']] = reasons.get(item['reason'], 0) + 1
    return {'schema_version': 1, 'study_id': source.name, 'archive_sha256': sha256(destination),
            'archive_bytes': destination.stat().st_size, 'included_files': len(inventory['files']),
            'included_bytes': sum(x['bytes'] for x in inventory['files'].values()),
            'excluded_boundaries_by_reason': reasons, 'inventory_member': INVENTORY,
            'availability': 'local_only', 'archive_name': destination.name,
            'retrieval': 'Obtain this local archive from the study maintainer; no hosted copy has been published.',
            'originals_retained': True}


def verify(path, expected_sha256=None):
    path = Path(path)
    if expected_sha256 is not None and sha256(path) != expected_sha256:
        raise ValueError('Archive checksum mismatch')
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        if len(names) != len(set(names)) or INVENTORY not in names:
            raise ValueError('Archive has duplicate names or no inventory')
        for member in members:
            name = PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts:
                raise ValueError('Archive contains unsafe/non-regular entries')
        with archive.extractfile(INVENTORY) as stream:
            inventory = json.load(stream)
        if set(names) != set(inventory['files']) | {INVENTORY}:
            raise ValueError('Archive contents differ from inventory')
        for name, expected in inventory['files'].items():
            digest = hashlib.sha256()
            size = 0
            with archive.extractfile(name) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block); size += len(block)
            if digest.hexdigest() != expected['sha256'] or size != expected['bytes']:
                raise ValueError('Archive member checksum mismatch: ' + name)
    return {'verified_files': len(inventory['files']), 'study_id': inventory['study_id']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    make = commands.add_parser('create'); make.add_argument('source', type=Path); make.add_argument('destination', type=Path)
    check = commands.add_parser('verify'); check.add_argument('archive', type=Path); check.add_argument('--sha256')
    args = parser.parse_args()
    result = create(args.source, args.destination) if args.command == 'create' else verify(args.archive, args.sha256)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
