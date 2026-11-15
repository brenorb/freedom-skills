import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'benchmarks/harness'))
import archive
from dataset_loader import CaseDataLoader, search_loaders
from package import build


class Packaging(unittest.TestCase):
    def test_actual_skill_has_no_answers_in_runtime_package(self):
        source = ROOT / 'skills/btcdeb'
        before = hashlib.sha256((source / 'SKILL.md').read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'skill'
            manifest = build(source, target)
            self.assertEqual(before, manifest['files']['SKILL.md'])
            self.assertTrue((target / 'references/execution.md').is_file())
            self.assertFalse((target / 'evals').exists())
            self.assertEqual(len(list(target.rglob('*.md'))), 6)
        self.assertEqual(before, hashlib.sha256((source / 'SKILL.md').read_bytes()).hexdigest())

    def test_answers_unknown_roots_and_symlink_resources_are_not_packaged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); skill = root / 'skill'; skill.mkdir()
            (skill / 'SKILL.md').write_text('runtime')
            (skill / 'evals').mkdir(); (skill / 'evals/answers.json').write_text('PRIVATE_ANSWER')
            (skill / 'secret.txt').write_text('PRIVATE_ANSWER')
            output = root / 'output'; manifest = build(skill, output)
            self.assertEqual(set(manifest['files']), {'SKILL.md'})
            (skill / 'references').symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError): build(skill, root / 'another')

    def test_refuses_overwrite_and_source_descendant(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'SKILL.md').write_text('x')
            with self.assertRaises(ValueError): build(root, root / 'nested')
            target = root.parent / root.name / 'existing'; target.mkdir(); (target / 'keep').write_text('original')
            with self.assertRaises(ValueError): build(root, target)
            self.assertEqual((target / 'keep').read_text(), 'original')


class DatasetIsolation(unittest.TestCase):
    def test_equal_payload_ids_never_share_gepa_cache_ids(self):
        a, b = search_loaders([{'id': 'same', 'prompt': 'train'}], [{'id': 'same', 'prompt': 'validation'}])
        self.assertTrue(set(a.all_ids()).isdisjoint(b.all_ids()))
        self.assertEqual(a.fetch(a.all_ids())[0]['prompt'], 'train')
        self.assertEqual(b.fetch(b.all_ids())[0]['prompt'], 'validation')

    def test_duplicate_and_unsafe_ids_fail(self):
        for namespace, cases in [('train/x', [{'id': 'x'}]), ('train', [{'id': '../x'}]),
                                 ('train', [{'id': 'x'}, {'id': 'x'}]), ('train', [])]:
            with self.assertRaises(ValueError): CaseDataLoader(namespace, cases)

    def test_all_twenty_public_cases_and_fixtures_are_loadable(self):
        base = ROOT / 'skills/btcdeb'; data = json.loads((base / 'evals/evals.json').read_text())
        cases = data['evals']; self.assertEqual(len(cases), 20)
        self.assertEqual(len(CaseDataLoader('public', cases)), 20)
        for case in cases:
            self.assertTrue(case['prompt'] and case['expected_output'] and case['assertions'])
            self.assertEqual(set(case['files']), set(case['fixture_destinations']))
            for file in case['files']:
                p = (base / file).resolve(); self.assertTrue(p.is_relative_to(base.resolve()))
                self.assertTrue(p.is_file())
        manifest = json.loads((base / 'evals/fixture-manifest.json').read_text())['files']
        for relative, expected in manifest.items():
            self.assertEqual(hashlib.sha256((base / relative).read_bytes()).hexdigest(), expected)
        queries = json.loads((base / 'evals/trigger-queries.json').read_text())['queries']
        self.assertEqual(sum(q['should_trigger'] is True for q in queries), 10)
        self.assertEqual(sum(q['should_trigger'] is False for q in queries), 10)


class EvidenceArchive(unittest.TestCase):
    def test_roundtrip_preserves_sources_and_excludes_private_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'study'; source.mkdir()
            (source / 'report.md').write_bytes(b'original\x00bytes')
            for file in ['runs/a/claude-state/token.json', 'runs/a/workspace/bin/btcdeb',
                         '.venv/lib/cache', 'dataset/sealed-final.json', 'dataset/fixtures-final/F01/input', 'dataset/fresh-tuple-design.json']:
                p = source / file; p.parent.mkdir(parents=True, exist_ok=True); p.write_text('DO_NOT_EXPORT')
            (source / 'outside-link').symlink_to(root, target_is_directory=True)
            before = (source / 'report.md').read_bytes()
            dest = root / 'evidence.tar.gz'; manifest = archive.create(source, dest)
            self.assertEqual(archive.verify(dest, manifest['archive_sha256'])['verified_files'], 1)
            self.assertEqual(before, (source / 'report.md').read_bytes())
            self.assertTrue((source / 'runs/a/claude-state/token.json').exists())
            with tarfile.open(dest) as tar:
                self.assertEqual(set(tar.getnames()), {'report.md', archive.INVENTORY})
            self.assertEqual(manifest['availability'], 'local_only')
            with self.assertRaises(ValueError): archive.create(source, dest)
            with self.assertRaises(ValueError): archive.verify(dest, '0' * 64)

    def test_member_corruption_and_unsafe_entries_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.tar.gz'
            for name in ['file.txt', '../escape']:
                inventory = {'study_id': 'synthetic', 'files': {name: {'sha256': '0' * 64, 'bytes': 3}}}
                with tarfile.open(path, 'w:gz') as tar:
                    for entry_name, data in [(name, b'bad'), (archive.INVENTORY, json.dumps(inventory).encode())]:
                        entry = tarfile.TarInfo(entry_name); entry.size = len(data); tar.addfile(entry, io.BytesIO(data))
                with self.assertRaises(ValueError): archive.verify(path)

    def test_cannot_archive_into_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError): archive.create(root, root / 'self.tar.gz')


if __name__ == '__main__': unittest.main()
