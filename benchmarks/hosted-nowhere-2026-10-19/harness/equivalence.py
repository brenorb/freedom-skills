"""Validate an explicit primary-agent audit of unchanged model-visible skill inputs.

This does not infer equivalence from a story's route or from missing text. The
reviewer must inspect every tool input (including shell scripts and argv) and
record all instruction reads/searches. Unknown or dynamic reads require a fresh
run. Hashes bind that review to immutable traces and both skill snapshots.
"""
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


def frozen_hash(root):
    h = hashlib.sha256()
    for p in sorted(root.rglob('*')):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def initial_context_hashes(record):
    return {name: sha(record / name) for name in
            ['prompt.md', 'system-prompt.txt', 'context-audit.json']
            if (record / name).exists()}


def validate(manifest, record, source, target):
    if not manifest:
        return None
    key = source.name + '/' + record.parent.name + '/' + record.name
    entry = manifest.get('cases', {}).get(key)
    if not entry or entry.get('reviewer') != 'primary-agent' or entry.get('approved') is not True:
        return None
    a, b = inventory(source / 'skill-snapshot'), inventory(target / 'skill-snapshot')
    changed = sorted(p for p in a.keys() | b.keys() if a.get(p) != b.get(p))
    checks = [
        a.keys() == b.keys(),
        entry.get('source_skill_sha256') == frozen_hash(source / 'skill-snapshot'),
        entry.get('target_skill_sha256') == frozen_hash(target / 'skill-snapshot'),
        entry.get('changed_files') == changed,
        entry.get('tools_sha256') == sha(record / 'tools.jsonl'),
        entry.get('initial_context_sha256') == initial_context_hashes(record),
        {'prompt.md', 'system-prompt.txt'} <= initial_context_hashes(record).keys(),
        entry.get('all_tool_inputs_reviewed') is True,
        entry.get('uncertain_reads') == [],
        bool(entry.get('note')),
    ]
    reads = entry.get('instruction_files', [])
    checks += [bool(reads), all(p in a and a[p] == b.get(p) for p in reads)]
    # Direct broker reads are machine-checkable; a manual audit cannot omit a
    # changed reference that was actually loaded. Shell/helper reads still need
    # the explicit full-input review above.
    direct_reads = set()
    for line in (record / 'tools.jsonl').read_text().splitlines():
        event = json.loads(line)
        if event.get('name') != 'read' or not event.get('input', {}).get('path'):
            continue
        path = Path(event['input']['path'])
        path = path if path.is_absolute() else record / 'workspace' / path
        try:
            relative = str(path.resolve().relative_to((record / 'workspace' / 'skill').resolve()))
        except ValueError:
            continue
        if relative in a:
            direct_reads.add(relative)
    checks.append(direct_reads <= set(reads))
    # Searches may cover changed files only when the reviewer independently
    # compared the exact query's output under both frozen snapshots.
    for query in entry.get('content_searches', []):
        checks.append(bool(query.get('query')) and query.get('source_output_sha256') == query.get('target_output_sha256') and bool(query.get('source_output_sha256')))
    return entry if all(checks) else None
